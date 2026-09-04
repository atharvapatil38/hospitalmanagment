from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.extensions import db
from app.models.department import Department
from app.utils.audit import log_audit
from app.utils.decorators import roles_required

departments_bp = Blueprint('departments', __name__, url_prefix='/departments')

class DepartmentForm(FlaskForm):
    name = StringField('Department Name (e.g. Cardiology)', validators=[DataRequired(), Length(max=100)])
    code = StringField('Department Code (e.g. CARD)', validators=[DataRequired(), Length(max=20)])
    head_doctor_name = StringField('Head of Department (HOD Name)', validators=[Optional(), Length(max=120)])
    phone = StringField('Department Extension / Phone', validators=[Optional(), Length(max=20)])
    description = TextAreaField('Department Description & Services', validators=[Optional()])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    submit = SubmitField('Save Department')

@departments_bp.route('/')
@login_required
def index():
    departments = Department.query.order_by(Department.name.asc()).all()
    return render_template('departments/index.html', departments=departments)

@departments_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def create():
    form = DepartmentForm()
    if form.validate_on_submit():
        if Department.query.filter_by(name=form.name.data.strip()).first():
            flash('A department with this name already exists.', 'danger')
            return render_template('departments/form.html', form=form, title='Add New Department')
        if Department.query.filter_by(code=form.code.data.strip().upper()).first():
            flash('A department with this code already exists.', 'danger')
            return render_template('departments/form.html', form=form, title='Add New Department')

        dept = Department(
            name=form.name.data.strip(),
            code=form.code.data.strip().upper(),
            head_doctor_name=form.head_doctor_name.data.strip() if form.head_doctor_name.data else None,
            phone=form.phone.data.strip() if form.phone.data else None,
            description=form.description.data.strip() if form.description.data else None,
            status=form.status.data
        )
        db.session.add(dept)
        db.session.commit()

        log_audit('CREATE_DEPARTMENT', 'Department', f"Created department {dept.name} ({dept.code}).")
        flash(f"Department '{dept.name}' created successfully.", 'success')
        return redirect(url_for('departments.index'))

    return render_template('departments/form.html', form=form, title='Add New Department')

@departments_bp.route('/<int:dept_id>')
@login_required
def view_detail(dept_id):
    department = Department.query.get_or_404(dept_id)
    doctors = department.doctors.filter_by(status='Active').all()
    staff_members = department.staff.filter_by(status='Active').all()
    recent_appointments = department.appointments.order_by(Department.created_at.desc()).limit(10).all()
    return render_template('departments/detail.html', department=department, doctors=doctors, staff_members=staff_members, recent_appointments=recent_appointments)

@departments_bp.route('/<int:dept_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def edit(dept_id):
    department = Department.query.get_or_404(dept_id)
    form = DepartmentForm(obj=department)

    if form.validate_on_submit():
        existing_n = Department.query.filter_by(name=form.name.data.strip()).first()
        if existing_n and existing_n.id != department.id:
            flash('Another department with this name already exists.', 'danger')
            return render_template('departments/form.html', form=form, title=f"Edit Department: {department.name}", department=department)

        existing_c = Department.query.filter_by(code=form.code.data.strip().upper()).first()
        if existing_c and existing_c.id != department.id:
            flash('Another department with this code already exists.', 'danger')
            return render_template('departments/form.html', form=form, title=f"Edit Department: {department.name}", department=department)

        department.name = form.name.data.strip()
        department.code = form.code.data.strip().upper()
        department.head_doctor_name = form.head_doctor_name.data.strip() if form.head_doctor_name.data else None
        department.phone = form.phone.data.strip() if form.phone.data else None
        department.description = form.description.data.strip() if form.description.data else None
        department.status = form.status.data

        db.session.commit()
        log_audit('UPDATE_DEPARTMENT', 'Department', f"Updated department {department.name}.")
        flash(f"Department '{department.name}' updated successfully.", 'success')
        return redirect(url_for('departments.index'))

    return render_template('departments/form.html', form=form, title=f"Edit Department: {department.name}", department=department)
