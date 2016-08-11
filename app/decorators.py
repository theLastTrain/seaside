from functools import wraps
from flask import abort, flash
from flask.ext.login import current_user
from .models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


def confirmation_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not current_user.confirmed:
            # return redirect(url_for('auth.unconfirmed'), code=403)
            abort(403)
        return f(*args, **kwargs)
    return decorator


def login_required_for_ajax(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', category='warning')
            abort(401)
        return f(*args, **kwargs)
    return decorated_view
