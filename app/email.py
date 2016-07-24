from flask import render_template, current_app
from flask.ext.mail import Message


def send_email(to, subject, template, **kwargs):
    """
        if you're using smtp.163.com as mail server, only mail in .txt format is allowed.
        Attempt to send a .html one may cause a '554 DT:SPM' error
    """
    app = current_app._get_current_object()
    msg = Message(app.config['SEASIDE_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['SEASIDE_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    # msg.html = render_template(template + '.html', **kwargs)
    from seaside.longtasks import send_async_email
    send_async_email.delay(msg)
