from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user

def roles_required(*roles):
    """
    Decorator to restrict view access to users with specified role(s).
    Usage: @roles_required('Super Admin', 'Hospital Admin', 'Doctor')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            if not current_user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return redirect(url_for('auth.login'))

            # Super Admin has universal access
            if current_user.role_name == 'Super Admin':
                return f(*args, **kwargs)

            if current_user.role_name not in roles:
                flash(f'Access denied: Your role ({current_user.role_name}) is not authorized to view this resource.', 'danger')
                return redirect(url_for('dashboard.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def active_user_required(f):
    """Decorator ensuring current user is active."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_active:
            flash('Access denied: Account inactive or not logged in.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
