# coding:utf-8

from flask import render_template, current_app
from flask.ext.mail import Message
from flask import jsonify, url_for


def send_email(to, subject, template, **kwargs):
    """
        if you're using smtp.163.com as mail server, only '.txt' mail is allowed.
        Sending a '.html' mail may cause a '554 DT:SPM' error
        :param to: receiver address
        :param subject: mail subject
        :param template: mail content template
    """
    app = current_app._get_current_object()
    msg = Message(app.config['SEASIDE_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['SEASIDE_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    # msg.html = render_template(template + '.html', **kwargs)
    from seaside.longtasks import send_async_email
    task = send_async_email.delay(msg)
    return jsonify({}), 202, {'Location': url_for('background.mailstatus', task_id=task.id)}
