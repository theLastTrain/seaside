/**
* Created by axl on 16/7/22.
*/

'use strict';

function isEmail(email){
    return (/^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z]+)+$/.test(email));
}

function isUsername(username){
    return(/^[\u2E80-\u9FFFA-Za-z\w\d_.]{3,24}$/.test(username));
}

function isPasswd(passwd){
    return (/^[a-zA-Z0-9_]{6,16}$/.test(passwd));
}

function showValidation(field, status, msg){
    if(status === 'success'){
        field.prev().text(msg).removeClass('hidden');
        field.parent().removeClass().addClass('has-success');
    }
    else if(status === 'error'){
        field.prev().text(msg).removeClass('hidden');
        field.parent().removeClass().addClass('has-error');
    }
    else {
        field.prev().addClass('hidden');
        field.parent().removeClass();
    }
}

function validateEmail(field, form, checkOccupying){
    var ret = false, value = field.val().trim();
    if(!isEmail(value)){
        if(value === ''){
            showValidation(field, 'error', '邮箱不能为空');
        }
        else {
            showValidation(field, 'error', '邮箱格式不正确');
        }
    }
    else {
        if(arguments.length === 3){
            if(checkOccupying === true){
                $.getJSON('/auth/email/' + value, function(data, status){
                    if(status === "error") {alert("未知错误");}
                    if(status === 'success'){
                        if(data['result'] === 'occupied'){
                            showValidation(field, 'error', '邮箱已注册');
                        }
                        else if(data['result'] === 'available'){
                            showValidation(field, 'success', '邮箱可用');
                            ret = true;
                            form.removeAttr('emailError');
                        }
                        else{
                            showValidation(field);
                        }
                    }
                });
            }
        }
        else{
            showValidation(field);
            ret = true;
        }
    }
    if(ret){
        form.removeAttr('emailError');
    }
    else{
        form.attr('emailError', true);
        console.log('fuck');
    }
}

function validateUsername(field, form, checkOccupying){
    var ret = false, value = field.val().trim();
    if(!isUsername(value)){
        if(value.length < 3){
            showValidation(field, 'error', '用户名长度应在3~24字符之间');
        }
        else {
            showValidation(field, 'error', '用户名只能使用中日韩文字,字母,数字,或者 _ .');
        }
    }
    else {
        if(arguments.length === 3){
            if(checkOccupying === true){
                $.getJSON('/auth/username/' + value, function(data, status){
                    if(status === "error") {alert("未知错误");}
                    if(status === 'success'){
                        if(data['result'] === 'occupied'){
                            showValidation(field, 'error', '用户名已注册');
                        }
                        else if(data['result'] === 'available'){
                            showValidation(field, 'success', '用户名可用');
                            ret = true;
                            form.removeAttr('usernameError');
                        }
                        else{
                            showValidation(field);
                        }
                    }
                });
            }
        }
        else{
            showValidation(field);
            ret = true;
        }
    }
    if(ret){
        form.removeAttr('usernameError');
    }
    else{
        form.attr('usernameError', true);
    }
}

function validatePassword(field, form){
    var ret = false, value = field.val();
    if(!isPasswd(value)){
        if(value === ''){
            showValidation(field, 'error', '密码不能为空');
        }
        else {
            showValidation(field, 'error', '密码必须为6-16位的字母,数字,或者_');
        }
    }
    else{
        showValidation(field);
        ret = true;
    }
    if(ret){
        form.removeAttr('passwordError');
    }
    else{
        form.attr('passwordError', true);
    }
}

function validatePassword2(field, form){
    var ret = false, value = field.val();
    if(!isPasswd(value)){
        if(value === ''){
            showValidation(field, 'error', '密码不能为空');
        }
        else {
            showValidation(field, 'error', '密码必须为6-16位的字母,数字,或者_');
        }
    }
    else{
        if(value === form.find(':password:first').val()){
            showValidation(field);
            ret = true;
        }
        else{
            showValidation(field, 'error', '两次输入的密码不一致');
        }
    }
    if(ret){
        form.removeAttr('password2Error');
    }
    else{
        form.attr('password2Error', true);
    }
}

$(document).ready(function(){
    var login = $('form:first'), register = $('form:last');

    var lFields = {'email': $('form:first input:first'), 'password': $('form:first :password:first')};
    lFields.email.change(function(){
        validateEmail($(this), login);
    });
    lFields.password.change(function(){
       validatePassword($(this), login);
    });

    var rFields = {'email': $('form:last input:first'), 'username': $('form:last input[name="username"]'),
        'password': $('form:last :password:first'), 'password2': $('form:last :password:last')};
    rFields.email.change(function(){
        validateEmail($(this), register, true);
    });
    rFields.username.change(function(){
        validateUsername($(this), register, true);
    });
    rFields.password.change(function(){
       validatePassword($(this), register);
    });
    rFields.password2.change(function(){
       validatePassword2($(this), register);
    });
    login.submit(function(e){
        validateEmail(lFields.email, $(this));
        validatePassword(lFields.password, $(this));
        if($(this).attr('emailError') || $(this).attr('passwordError')){
            e.preventDefault();
        }
    });

    register.submit(function(e){
        if(!$(this).attr('emailError')){
            validateEmail(rFields.email, $(this));
        }
        if(!$(this).attr('usernameError')){
            validateUsername(rFields.username, $(this));
        }
        validatePassword(rFields.password, $(this));
        validatePassword2(rFields.password2, $(this));
        if($(this).attr('emailError') || $(this).attr('usernameError')
            || $(this).attr('passwordError') || $(this).attr('password2Error')) {
            e.preventDefault()
        }
    });
});