
# coding:utf-8

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import User, Role
from flask.ext.pagedown.fields import PageDownField


class NameForm(Form):
    name = StringField("还不知道你的名字呢?", validators=[DataRequired()])
    submit = SubmitField('提交')


class EditProfileForm(Form):
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('填写地址', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')


class EditProfileAdminForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^\w[\w\d_.]*$', 0, 'User name must have only letters, '
                                               'dots, numbers or underscores.')])
    confirmed = BooleanField('已认证')
    role = SelectField('Role', coerce=int)
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('居住地', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(emil=field.data).first():
            raise ValidationError('该邮箱已注册')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已注册')


class PostForm(Form):
    title = StringField('', validators=[DataRequired()])
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('提交')

class CommentForm(Form):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('提交')


class SearchForm(Form):
    search = StringField('', validators=[DataRequired()])

class ChangeLogForm(Form):
    body = StringField('', validators=[DataRequired()])