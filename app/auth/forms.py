# coding:utf-8

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('邮箱')
    password = PasswordField('密码')
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')


class RegistrationForm(Form):
    email = StringField('邮箱')
    username = StringField('用户名')
    password = PasswordField('密码')
    password2 = PasswordField('确认密码')
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已注册')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[DataRequired('密码不能为空')])
    new_password = PasswordField('新密码', validators=[
        DataRequired('密码不能为空'), Length(6, 16, '密码长度必须在6至16字符之间'), EqualTo('password2', message='两次输入的密码不匹配')])
    new_password2 = PasswordField('确认密码', validators=[DataRequired('密码不能为空')])
    confirm = SubmitField('确认')


class ResetPasswordRequestForm(Form):
    email = StringField('邮箱', validators=[DataRequired('邮箱不能为空'), Email('无效的邮箱')])
    confirm = SubmitField('确认')


class ResetPasswordForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Email('无效的邮箱')])
    password = PasswordField('新密码', validators=[
        DataRequired(), Length(6, 16, '密码长度必须在6至16字符之间'), EqualTo("password2", message='两次输入的密码不匹配')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    confirm = SubmitField('更新')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError('该邮箱未注册')
