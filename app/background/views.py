# coding:utf-8

from flask import jsonify
from . import background
from seaside.longtasks import send_async_email


@background.route('/mail/<task_id>')
def mailstatus(task_id):
    task = send_async_email.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'message': '一封激活信已发往你的注册邮箱, 请根据提示完成激活'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'message': '处理中, 请耐心等待...'
        }
    else:
        # something went wrong in the bg job
        response = {
            'state': task.state,
            'message': '出错啦, 请稍后再试 :('
        }
    return jsonify(response)
