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


class PostForm(Form):
    title = StringField('', validators=[DataRequired()])
    tag_string = StringField('')
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentForm(Form):
    body = PageDownField('', validators=[DataRequired()])
    submit = SubmitField('提交')


class SearchForm(Form):
    search = StringField('', validators=[DataRequired()])


class ChangeLogForm(Form):
    body = StringField('', validators=[DataRequired()])