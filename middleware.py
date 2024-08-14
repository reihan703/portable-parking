from functools import wraps
from flask import session, flash, redirect, url_for


def auth(fn):
    @wraps(fn)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Login first.', 'danger')
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrap
