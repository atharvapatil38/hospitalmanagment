from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User, Role
from app.forms.auth_forms import LoginForm, ChangePasswordForm, UserProfileForm, UserAdminForm
from app.utils.audit import log_audit
from app.utils.decorators import roles_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the hospital administrator.', 'danger')
                return render_template('auth/login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()

            log_audit('LOGIN', 'Authentication', f"User {user.username} ({user.role_name}) logged in successfully.")
            flash(f"Welcome back, {user.full_name}!", 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email address or password. Please try again.', 'danger')
            log_audit('LOGIN_FAILED', 'Authentication', f"Failed login attempt for email: {form.email.data}")

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    log_audit('LOGOUT', 'Authentication', f"User {current_user.username} logged out.")
    logout_user()
    flash('You have been securely signed out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.email = form.email.data.strip().lower()
        current_user.phone = form.phone.data.strip() if form.phone.data else None
        db.session.commit()

        log_audit('UPDATE_PROFILE', 'User Profile', f"User {current_user.username} updated profile information.")
        flash('Your profile details have been updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('The current password entered is incorrect.', 'danger')
        else:
            current_user.password = form.new_password.data
            db.session.commit()
            log_audit('CHANGE_PASSWORD', 'Authentication', f"User {current_user.username} changed password.")
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('auth.profile'))

    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/users')
@roles_required('Super Admin')
def user_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    role_filter = request.args.get('role', '', type=str)

    query = User.query
    if search:
        query = query.filter((User.full_name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%")) | (User.username.ilike(f"%{search}%")))
    if role_filter:
        query = query.join(Role).filter(Role.name == role_filter)

    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    roles = Role.query.all()
    return render_template('auth/user_list.html', users=users, roles=roles, search=search, role_filter=role_filter)

@auth_bp.route('/users/new', methods=['GET', 'POST'])
@roles_required('Super Admin')
def user_create():
    form = UserAdminForm()
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash('Username is already taken.', 'danger')
            return render_template('auth/user_form.html', form=form, title='Create New User Account')
        if User.query.filter_by(email=form.email.data.strip().lower()).first():
            flash('Email address is already registered.', 'danger')
            return render_template('auth/user_form.html', form=form, title='Create New User Account')
        if not form.password.data:
            flash('Password is required when creating a new account.', 'danger')
            return render_template('auth/user_form.html', form=form, title='Create New User Account')

        new_user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            full_name=form.full_name.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            role_id=form.role_id.data,
            is_active=form.is_active.data,
            password=form.password.data
        )
        db.session.add(new_user)
        db.session.commit()

        log_audit('CREATE_USER', 'User Management', f"Created user {new_user.username} with role {new_user.role_name}.")
        flash(f"User account for '{new_user.full_name}' created successfully.", 'success')
        return redirect(url_for('auth.user_list'))

    return render_template('auth/user_form.html', form=form, title='Create New User Account')

@auth_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@roles_required('Super Admin')
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserAdminForm(obj=user)
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        existing_u = User.query.filter_by(username=form.username.data.strip()).first()
        if existing_u and existing_u.id != user.id:
            flash('Username is already taken by another account.', 'danger')
            return render_template('auth/user_form.html', form=form, title=f"Edit User: {user.full_name}")

        existing_e = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing_e and existing_e.id != user.id:
            flash('Email is already registered by another account.', 'danger')
            return render_template('auth/user_form.html', form=form, title=f"Edit User: {user.full_name}")

        user.username = form.username.data.strip()
        user.email = form.email.data.strip().lower()
        user.full_name = form.full_name.data.strip()
        user.phone = form.phone.data.strip() if form.phone.data else None
        user.role_id = form.role_id.data
        user.is_active = form.is_active.data

        if form.password.data and len(form.password.data.strip()) >= 6:
            user.password = form.password.data.strip()

        db.session.commit()
        log_audit('UPDATE_USER', 'User Management', f"Updated account for {user.username}.")
        flash(f"Account for '{user.full_name}' updated successfully.", 'success')
        return redirect(url_for('auth.user_list'))

    return render_template('auth/user_form.html', form=form, title=f"Edit User: {user.full_name}", user=user)

@auth_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@roles_required('Super Admin')
def user_toggle_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('auth.user_list'))

    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activated" if user.is_active else "deactivated"
    log_audit('TOGGLE_USER_STATUS', 'User Management', f"User {user.username} {status_str}.")
    flash(f"User account '{user.full_name}' has been {status_str}.", 'info')
    return redirect(url_for('auth.user_list'))
