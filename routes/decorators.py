from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def worker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in as a Worker to access this page.', 'warning')
            return redirect(url_for('auth.login', role='worker'))
        if not current_user.is_worker():
            flash('Access restricted to registered Workers only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def employer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in as an Employer to access this page.', 'warning')
            return redirect(url_for('auth.login', role='employer'))
        if not current_user.is_employer():
            flash('Access restricted to registered Employers only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
