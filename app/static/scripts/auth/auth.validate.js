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
    field.parentElement.classList.add('has-error');
    var label = field.parentElement.getElementsByTagName('label')[0];
    label.innerText= msg;
    label.classList.remove('hidden-default');
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



var loginForm = document.forms['login'];
loginForm.onsubmit = function(){
    var ret = true;
    var fields = {'email':document.forms['login'].elements[0],
        'password':document.forms['login'].elements[1]
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
    //validate password
    if(fields.password.value.length < 6 || fields.password.value.length > 16){
        showValidateErr(fields.password, '密码长度必须在6~16字符之间');
        ret = false;
    }

    return ret;
};
