from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.doctor import Doctor, DoctorSchedule
from app.models.department import Department
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.forms.doctor_forms import DoctorForm
from app.utils.id_generator import generate_doctor_code
from app.utils.audit import log_audit
from app.utils.decorators import roles_required

doctors_bp = Blueprint('doctors', __name__, url_prefix='/doctors')

@doctors_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '', type=str).strip()
    dept_id = request.args.get('department_id', '', type=str)
    status = request.args.get('status', '', type=str)

    query = Doctor.query
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Doctor.name.ilike(search_fmt)) |
            (Doctor.specialization.ilike(search_fmt)) |
            (Doctor.doctor_code.ilike(search_fmt))
        )
    if dept_id and dept_id.isdigit():
        query = query.filter(Doctor.department_id == int(dept_id))
    if status:
        query = query.filter(Doctor.status == status)

    doctors = query.order_by(Doctor.name.asc()).all()
    departments = Department.query.filter_by(status='Active').all()

    return render_template('doctors/index.html', doctors=doctors, departments=departments, search=search, department_id=dept_id, status=status)

@doctors_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def create():
    form = DoctorForm()
    depts = Department.query.filter_by(status='Active').all()
    form.department_id.choices = [(d.id, d.name) for d in depts]

    if form.validate_on_submit():
        if Doctor.query.filter_by(email=form.email.data.strip().lower()).first():
            flash('A doctor with this email address already exists.', 'danger')
            return render_template('doctors/form.html', form=form, title='Add New Doctor')

        code = generate_doctor_code()
        doctor = Doctor(
            doctor_code=code,
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip(),
            department_id=form.department_id.data,
            specialization=form.specialization.data.strip(),
            qualification=form.qualification.data.strip(),
            experience_years=form.experience_years.data or 0,
            consultation_fee=form.consultation_fee.data or 50.0,
            availability_status=form.availability_status.data,
            available_days=form.available_days.data.strip(),
            available_time_start=form.available_time_start.data.strip(),
            available_time_end=form.available_time_end.data.strip(),
            room_number=form.room_number.data.strip() if form.room_number.data else None,
            bio=form.bio.data.strip() if form.bio.data else None,
            status=form.status.data
        )
        db.session.add(doctor)
        db.session.commit()

        log_audit('CREATE_DOCTOR', 'Doctor', f"Created doctor record {doctor.name} ({doctor.doctor_code}).")
        flash(f"Doctor '{doctor.name}' added successfully with code {doctor.doctor_code}.", 'success')
        return redirect(url_for('doctors.view_profile', doctor_id=doctor.id))

    return render_template('doctors/form.html', form=form, title='Add New Doctor')

@doctors_bp.route('/<int:doctor_id>')
@login_required
def view_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    today = date.today()
    today_appointments = doctor.appointments.filter_by(appointment_date=today).order_by(Appointment.appointment_time.asc()).all()
    all_appointments = doctor.appointments.order_by(Appointment.appointment_date.desc()).limit(20).all()
    assigned_patients = Patient.query.filter_by(primary_doctor_id=doctor.id).all()
    schedules = doctor.schedules.all()

    return render_template(
        'doctors/profile.html',
        doctor=doctor,
        today_appointments=today_appointments,
        all_appointments=all_appointments,
        assigned_patients=assigned_patients,
        schedules=schedules
    )

@doctors_bp.route('/<int:doctor_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def edit(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    form = DoctorForm(obj=doctor)
    depts = Department.query.filter_by(status='Active').all()
    form.department_id.choices = [(d.id, d.name) for d in depts]

    if form.validate_on_submit():
        existing = Doctor.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing and existing.id != doctor.id:
            flash('Another doctor is already registered with this email.', 'danger')
            return render_template('doctors/form.html', form=form, title=f"Edit Doctor: {doctor.name}", doctor=doctor)

        doctor.name = form.name.data.strip()
        doctor.email = form.email.data.strip().lower()
        doctor.phone = form.phone.data.strip()
        doctor.department_id = form.department_id.data
        doctor.specialization = form.specialization.data.strip()
        doctor.qualification = form.qualification.data.strip()
        doctor.experience_years = form.experience_years.data or 0
        doctor.consultation_fee = form.consultation_fee.data or 0.0
        doctor.availability_status = form.availability_status.data
        doctor.available_days = form.available_days.data.strip()
        doctor.available_time_start = form.available_time_start.data.strip()
        doctor.available_time_end = form.available_time_end.data.strip()
        doctor.room_number = form.room_number.data.strip() if form.room_number.data else None
        doctor.bio = form.bio.data.strip() if form.bio.data else None
        doctor.status = form.status.data

        db.session.commit()
        log_audit('UPDATE_DOCTOR', 'Doctor', f"Updated doctor record for {doctor.name}.")
        flash(f"Doctor profile for '{doctor.name}' updated successfully.", 'success')
        return redirect(url_for('doctors.view_profile', doctor_id=doctor.id))

    return render_template('doctors/form.html', form=form, title=f"Edit Doctor: {doctor.name}", doctor=doctor)
