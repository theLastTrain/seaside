from functools import wraps
from flask import abort, request, redirect, url_for
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
        if current_user.is_authenticated:
            current_user.ping()
            if not current_user.confirmed:
                return redirect(url_for('auth.unconfirmed'), code=403)
        return f(*args, **kwargs)
    return decorator
