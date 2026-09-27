from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in first.', 'info')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard.index'))
            return func(*args, **kwargs)
        return wrapped
    return decorator
