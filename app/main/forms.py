
# coding:utf-8

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, ValidationError, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import User, Role
from flask.ext.pagedown.fields import PageDownField


class EditProfileForm(Form):
    gender = RadioField('性别', coerce=int, choices=[(0, '男'), (1, '女')])
    about_me = StringField('关于我')
    self_intro = TextAreaField('个人简介')
    job = StringField('所在行业')
    location = StringField('居住地', validators=[Length(0, 64)])
    submit = SubmitField('确定')


# class EditProfileAdminForm(Form):
#     email = StringField('邮箱', validators=[DataRequired(), Email(), Length(1, 64)])
#     username = StringField('用户名', validators=[
#         DataRequired('用户名不能为空'), Length(3, 24, '名字长度应在3至24字符之间'),
#         Regexp(r'^[\u2E80-\u9FFF]|[A-Za-z]|[\w\d_.]*$', 0, '用户名只能由中日韩文字, 英文字母, 数字, "."或者"_"组成')])
#     confirmed = BooleanField('已认证')
#     role = SelectField('Role', coerce=int)
#     name = StringField('姓名', validators=[Length(0, 64)])
#     location = StringField('居住地', validators=[Length(0, 64)])
#     about_me = TextAreaField('关于我')
#     submit = SubmitField('提交')
#
#     def __init__(self, user, *args, **kwargs):
#         super(EditProfileAdminForm, self).__init__(*args, **kwargs)
#         self.role.choices = [(role.id, role.name)
#                              for role in Role.query.order_by(Role.name).all()]
#         self.user = user
#
#     def validate_email(self, field):
#         if field.data != self.user.email and \
#                 User.query.filter_by(emil=field.data).first():
#             raise ValidationError('该邮箱已注册')
#
#     def validate_username(self, field):
#         if field.data != self.user.username and \
#                 User.query.filter_by(username=field.data).first():
#             raise ValidationError('用户名已注册')


class PostForm(Form):
    title = StringField('', validators=[DataRequired()])
    tag_string = StringField('')
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentForm(Form):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('提交')


class SearchForm(Form):
    search = StringField('', validators=[DataRequired()])


class ChangeLogForm(Form):
    body = StringField('', validators=[DataRequired()])