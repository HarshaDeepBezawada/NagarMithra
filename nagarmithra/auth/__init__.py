"""
Auth Blueprint
===============
Handles administrator authentication (login/logout).
"""

from functools import wraps
from flask import (
    Blueprint, render_template, redirect, url_for, flash, session, request,
)
from werkzeug.security import check_password_hash

from nagarmithra.models import Admin
from nagarmithra.forms import LoginForm

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """
    Decorator that protects a route so only authenticated administrators
    can access it. Redirects unauthenticated users to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in to access the admin dashboard.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Administrator login page.

    Validates credentials against the database using secure password
    hash comparison. Never reveals whether the username or password
    was incorrect individually.
    """
    # If already logged in, go to dashboard
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data.strip()).first()

        if admin and admin.is_active and check_password_hash(admin.password_hash, form.password.data):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash(f'Welcome, {admin.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """Log out the current administrator and clear the session."""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
