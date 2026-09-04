from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.staff import Staff
from app.models.department import Department
from app.forms.staff_forms import StaffForm
from app.utils.id_generator import generate_staff_code
from app.utils.audit import log_audit
from app.utils.decorators import roles_required

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/')
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def index():
    role_filter = request.args.get('role', '', type=str)
    dept_id = request.args.get('department_id', '', type=str)
    search = request.args.get('search', '', type=str).strip()

    query = Staff.query
    if role_filter:
        query = query.filter(Staff.role_title == role_filter)
    if dept_id and dept_id.isdigit():
        query = query.filter(Staff.department_id == int(dept_id))
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Staff.name.ilike(search_fmt)) |
            (Staff.staff_code.ilike(search_fmt)) |
            (Staff.email.ilike(search_fmt)) |
            (Staff.phone.ilike(search_fmt))
        )

    staff_members = query.order_by(Staff.role_title.asc(), Staff.name.asc()).all()
    departments = Department.query.filter_by(status='Active').all()

    return render_template(
        'staff/index.html',
        staff_members=staff_members,
        departments=departments,
        role_filter=role_filter,
        dept_id=dept_id,
        search=search
    )

@staff_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def create():
    form = StaffForm()
    depts = Department.query.filter_by(status='Active').all()
    form.department_id.choices = [(0, '-- None / General Hospital --')] + [(d.id, d.name) for d in depts]

    if form.validate_on_submit():
        if Staff.query.filter_by(email=form.email.data.strip().lower()).first():
            flash('A staff member with this email already exists.', 'danger')
            return render_template('staff/form.html', form=form, title='Register Staff Member')

        code = generate_staff_code()
        staff = Staff(
            staff_code=code,
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip(),
            role_title=form.role_title.data,
            department_id=form.department_id.data if form.department_id.data > 0 else None,
            joining_date=form.joining_date.data,
            salary=form.salary.data or 0.0,
            status=form.status.data,
            qualification=form.qualification.data.strip() if form.qualification.data else None,
            address=form.address.data.strip() if form.address.data else None
        )
        db.session.add(staff)
        db.session.commit()

        log_audit('CREATE_STAFF', 'Staff Management', f"Registered staff {staff.name} ({staff.staff_code}) - {staff.role_title}.")
        flash(f"Staff member '{staff.name}' ({staff.staff_code}) registered successfully.", 'success')
        return redirect(url_for('staff.index'))

    return render_template('staff/form.html', form=form, title='Register Staff Member')

@staff_bp.route('/<int:staff_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def edit(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    form = StaffForm(obj=staff)
    depts = Department.query.filter_by(status='Active').all()
    form.department_id.choices = [(0, '-- None / General Hospital --')] + [(d.id, d.name) for d in depts]

    if request.method == 'GET':
        form.department_id.data = staff.department_id or 0

    if form.validate_on_submit():
        existing = Staff.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing and existing.id != staff.id:
            flash('Another staff member has this email address.', 'danger')
            return render_template('staff/form.html', form=form, title=f"Edit Staff: {staff.name}", staff=staff)

        staff.name = form.name.data.strip()
        staff.email = form.email.data.strip().lower()
        staff.phone = form.phone.data.strip()
        staff.role_title = form.role_title.data
        staff.department_id = form.department_id.data if form.department_id.data > 0 else None
        staff.joining_date = form.joining_date.data
        staff.salary = form.salary.data or 0.0
        staff.status = form.status.data
        staff.qualification = form.qualification.data.strip() if form.qualification.data else None
        staff.address = form.address.data.strip() if form.address.data else None

        db.session.commit()
        log_audit('UPDATE_STAFF', 'Staff Management', f"Updated staff details for {staff.name} ({staff.staff_code}).")
        flash(f"Staff record for '{staff.name}' updated successfully.", 'success')
        return redirect(url_for('staff.index'))

    return render_template('staff/form.html', form=form, title=f"Edit Staff: {staff.name}", staff=staff)
