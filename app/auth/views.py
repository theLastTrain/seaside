
# coding:utf-8

# added May 17th 1:33 am, this block solves the problem:
#   UnicodeDecodeError: 'ascii' codec can't decode byte 0xe9 in position 0: ordinal not in range(128)

from flask import render_template, redirect, request, flash, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from ..decorators import confirmation_required
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    ResetPasswordRequestForm, ResetPasswordForm
from ..email import send_email

import os
if 'heroku' == os.environ.get('FLASK_COVERAGE'):
    import sys
    if sys.getdefaultencoding() != 'utf8':
        reload(sys)
        sys.setdefaultencoding('utf8')
        default_encoding = sys.getdefaultencoding()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    loginform = LoginForm()
    registerform = RegistrationForm()
    active = 'login'
    if request.method == 'POST':
        submit_name = request.form['submit']
        if submit_name == '登陆':
            if loginform.validate():
                user = User.query.filter_by(email=loginform.email.data).first()
                if user is None:
                    loginform.email.errors.append('邮箱未注册')
                elif not user.verify_password(loginform.password.data):
                    loginform.password.errors.append('密码错误')
                else:
                    login_user(user, loginform.remember_me.data)
                    return redirect(url_for('main.index'))
        if submit_name == '注册':
            if registerform.validate():
                user = User(email=registerform.email.data,
                            username=registerform.username.data,
                            password=registerform.password.data)
                db.session.add(user)
                db.session.commit()
                token = user.generate_confirmation_token()
                send_email(user.email, '激活你的账户',
                           'auth/email/confirm', user=user, token=token)
                login_user(user, loginform.remember_me.data)
                flash("一封含有激活链接的邮件已经发往你的注册邮箱")
                return redirect(url_for('main.index'))
            else:
                active = 'register'
    return render_template('auth/login.html', loginform=loginform, registerform=registerform, active=active)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('再见, 要再来哦 (｡･ω･)ﾉﾞ', category='success')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:  # User obj has been loaded in route /login
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('你的账户已经激活', category='success')
    else:
        flash('激活链接无效或已过期', category='danger')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '激活你的账户',
               'auth/email/confirm', user=current_user, token=token)
    flash('一封新的激活邮件已发往你的注册邮箱', category='info')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('密码已更新', category='success')
            return redirect(url_for('main.index'))
        else:
            flash('密码错误', category='danger')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_password_token()
            send_email(user.email, '重置你的密码', 'auth/email/reset-password', user=user, token=token)
            flash('一封介绍如何重置密码的邮件已发往你的邮箱', category='info')
            return redirect(url_for('auth.login'))
        else:
            form.email.errors.append('该邮箱未注册')
    return render_template("auth/reset_password.html", form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('密码已更新', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('链接无效或者已过期', category='danger')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
