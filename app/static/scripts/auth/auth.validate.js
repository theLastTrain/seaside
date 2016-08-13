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

function showValidateErr(field, msg){
    field.prev().text(msg).removeClass('hidden');
    field.parent().addClass('has-error');
}

var registerForm = document.forms['register'];
registerForm.onsubmit = function(){
    var ret = true;
    var fields = {'email':document.forms['register'].elements[0],
        'username':document.forms['register'].elements[1],
        'password':document.forms['register'].elements[2],
        'password2':document.forms['register'].elements[3]
    };
    //validate email
    if(!fields.email.value){
        showValidateErr(fields.email, '邮箱不能为空');
        ret = false;
    }
    else{
        if(!isEmail(fields.email.value)) {
            showValidateErr(fields.email, '无效的邮箱');
            ret = false;
        }
    }
    //validate username
    if(!fields.username.value){
        showValidateErr(fields.username, '用户名不能为空');
        ret = false;
    }
    else if(fields.username.value.length < 3 || fields.username.value.length > 24){
        showValidateErr(fields.username, '用户名长度应在3至24字符之间');
    }
    else {
        if(!isUsername(fields.username.value)) {
            showValidateErr(fields.username, "只能输入中日文字, 英文字母, 数字, '.'或者'_'");
            ret = false;
        }
    }
    //validate password
    if(fields.password.value.length < 6 || fields.password.value.length > 16){
        showValidateErr(fields.password, '密码长度必须在6~16字符之间');
        ret = false;
    }
    if(fields.password2.value != fields.password.value){
        showValidateErr(fields.password2, '两次输入密码不一致');
        ret = false;
    }
    return ret;
};


$('[name="login"]').submit(function(e){
    var ret = true;
    var fields = {'email': $(this).find("input[name='email']"),
        'password': $(this).find(':password')};

    if(fields.email.val() === ''){
        showValidateErr(fields.email, '邮箱不能为空');
        ret = false;
    }
    if(fields.password.val() === ''){
        showValidateErr(fields.password, '密码不能为空');
        ret = false;
    }
    if(!ret){
        e.preventDefault();
    }
});


$('[name="login"] input[name="email"]').blur(function(){
    var disable = false, value = $(this).val();
    if(!isEmail(value)) {
        if(value === ''){
            showValidation($(this), 'error', '邮箱不能为空');
        }
        else{
            showValidation($(this), 'error', '邮箱格式不正确');
        }
        disable = true;
    }
    else {
        showValidation($(this));
    }
    $(this).parentsUntil('#login').find(':submit').attr('disabled', disable);
});


$('[name="register"] input:first').blur(function(){
    var disable = false, value = $(this).val(), that = this;
    if(!isEmail(value)) {
        if(value === ''){
            showValidation($(this), 'error', '邮箱不能为空');
        }
        else{
            showValidation($(this), 'error', '邮箱格式不正确');
        }
        disable = true;
    }
    else {
        $.getJSON('/auth/validation/email/' + value, function(data, status){
            if(status === "error") {alert("未知错误");}
            if(status === 'success'){
                if(data['result'] === 'occupied'){
                    showValidation($(that), 'error', '邮箱已注册');
                    disable = true;
                }
                else if(data['result'] === 'available'){
                    showValidation($(that), 'success', '邮箱可用');
                }
                else{
                    showValidation(that);
                }
            }
        });
    }
    $(this).parentsUntil('#register').find(':submit').attr('disabled', disable);
});


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