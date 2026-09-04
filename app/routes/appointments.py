from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.forms.appointment_forms import AppointmentForm, AppointmentStatusForm
from app.utils.id_generator import generate_appointment_id
from app.utils.audit import log_audit
from app.utils.notifications import create_notification
from app.utils.decorators import roles_required
from app.utils.helpers import export_csv_response

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointments_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    status = request.args.get('status', '', type=str)
    doc_id = request.args.get('doctor_id', '', type=str)
    dept_id = request.args.get('department_id', '', type=str)
    date_filter = request.args.get('date', '', type=str)

    query = Appointment.query

    # If logged in as Doctor, default or restrict to doctor's appointments
    if current_user.role_name == 'Doctor':
        doc = Doctor.query.filter_by(email=current_user.email).first()
        if doc:
            query = query.filter(Appointment.doctor_id == doc.id)
    elif doc_id and doc_id.isdigit():
        query = query.filter(Appointment.doctor_id == int(doc_id))

    if search:
        search_fmt = f"%{search}%"
        query = query.join(Patient).filter(
            (Appointment.appointment_id.ilike(search_fmt)) |
            (Patient.first_name.ilike(search_fmt)) |
            (Patient.last_name.ilike(search_fmt)) |
            (Patient.patient_id.ilike(search_fmt))
        )
    if status:
        query = query.filter(Appointment.status == status)
    if dept_id and dept_id.isdigit():
        query = query.filter(Appointment.department_id == int(dept_id))
    if date_filter:
        if date_filter == 'today':
            query = query.filter(Appointment.appointment_date == date.today())
        elif date_filter == 'upcoming':
            query = query.filter(Appointment.appointment_date >= date.today())
        else:
            try:
                custom_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter(Appointment.appointment_date == custom_date)
            except ValueError:
                pass

    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.asc()).paginate(page=page, per_page=15, error_out=False)
    doctors = Doctor.query.filter_by(status='Active').all()
    departments = Department.query.filter_by(status='Active').all()

    return render_template(
        'appointments/index.html',
        appointments=appointments,
        doctors=doctors,
        departments=departments,
        search=search,
        status=status,
        doctor_id=doc_id,
        department_id=dept_id,
        date_filter=date_filter
    )

@appointments_bp.route('/export-csv')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Receptionist', 'Doctor')
def export_csv():
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    headers = ['Appointment ID', 'Patient Name', 'Patient ID', 'Doctor Name', 'Department', 'Date', 'Time Slot', 'Type', 'Status', 'Reason']
    rows = []
    for a in appointments:
        rows.append([
            a.appointment_id,
            a.patient.full_name if a.patient else 'N/A',
            a.patient.patient_id if a.patient else 'N/A',
            a.doctor.name if a.doctor else 'N/A',
            a.department.name if a.department else 'N/A',
            a.appointment_date.strftime('%Y-%m-%d'),
            a.appointment_time,
            a.appointment_type,
            a.status,
            a.reason
        ])
    return export_csv_response('appointments_report', headers, rows)

@appointments_bp.route('/book', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Receptionist', 'Doctor', 'Nurse')
def book():
    form = AppointmentForm()
    
    patients = Patient.query.filter_by(status='Active').order_by(Patient.first_name.asc()).all()
    form.patient_id.choices = [(p.id, f"{p.full_name} ({p.patient_id}) - {p.phone}") for p in patients]

    doctors = Doctor.query.filter_by(status='Active').order_by(Doctor.name.asc()).all()
    form.doctor_id.choices = [(d.id, f"{d.name} - {d.specialization} (₹{d.consultation_fee:0.2f})") for d in doctors]

    depts = Department.query.filter_by(status='Active').order_by(Department.name.asc()).all()
    form.department_id.choices = [(dept.id, dept.name) for dept in depts]

    # Pre-select patient if provided in query param
    pre_patient_id = request.args.get('patient_id', type=int)
    if pre_patient_id and request.method == 'GET':
        form.patient_id.data = pre_patient_id

    if form.validate_on_submit():
        # Conflict Check: Check if doctor has another active appointment at this date & time
        conflict = Appointment.query.filter(
            Appointment.doctor_id == form.doctor_id.data,
            Appointment.appointment_date == form.appointment_date.data,
            Appointment.appointment_time == form.appointment_time.data,
            Appointment.status.in_(['Scheduled', 'Confirmed'])
        ).first()

        if conflict:
            flash(f"Scheduling Conflict: Dr. {conflict.doctor.name} already has a confirmed/scheduled appointment at {form.appointment_time.data} on {form.appointment_date.data.strftime('%Y-%m-%d')}. Please choose a different time slot or doctor.", 'danger')
            return render_template('appointments/form.html', form=form, title='Book Medical Appointment')

        apt_id = generate_appointment_id()
        appointment = Appointment(
            appointment_id=apt_id,
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            department_id=form.department_id.data,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data,
            appointment_type=form.appointment_type.data,
            reason=form.reason.data.strip(),
            status='Scheduled',
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(appointment)
        db.session.commit()

        # Notify doctor and log audit
        log_audit('BOOK_APPOINTMENT', 'Appointment', f"Booked appointment {appointment.appointment_id} for Patient ID {appointment.patient_id} with Dr. {appointment.doctor.name}.")
        create_notification(
            title=f"New Appointment: {appointment.patient.full_name}",
            message=f"Appointment {appointment.appointment_id} booked for {appointment.appointment_date.strftime('%b %d, %Y')} at {appointment.appointment_time}.",
            target_role='Doctor',
            link=url_for('appointments.index')
        )

        flash(f"Appointment booked successfully! Appointment Ref: {appointment.appointment_id}", 'success')
        return redirect(url_for('appointments.index'))

    return render_template('appointments/form.html', form=form, title='Book Medical Appointment')

@appointments_bp.route('/<int:apt_id>/status', methods=['POST'])
@login_required
def update_status(apt_id):
    appointment = Appointment.query.get_or_404(apt_id)
    new_status = request.form.get('status')
    cancellation_reason = request.form.get('cancellation_reason')

    if new_status in ['Scheduled', 'Confirmed', 'Completed', 'Cancelled', 'No Show']:
        appointment.status = new_status
        if cancellation_reason:
            appointment.cancellation_reason = cancellation_reason
        db.session.commit()

        log_audit('UPDATE_APPOINTMENT_STATUS', 'Appointment', f"Updated status of {appointment.appointment_id} to {new_status}.")
        flash(f"Appointment {appointment.appointment_id} marked as '{new_status}'.", 'success')
    else:
        flash('Invalid status value provided.', 'danger')

    return redirect(request.referrer or url_for('appointments.index'))

@appointments_bp.route('/<int:apt_id>/reschedule', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Receptionist', 'Doctor')
def reschedule(apt_id):
    appointment = Appointment.query.get_or_404(apt_id)
    form = AppointmentForm(obj=appointment)

    patients = Patient.query.all()
    form.patient_id.choices = [(p.id, f"{p.full_name} ({p.patient_id})") for p in patients]
    doctors = Doctor.query.filter_by(status='Active').all()
    form.doctor_id.choices = [(d.id, f"{d.name} ({d.specialization})") for d in doctors]
    depts = Department.query.filter_by(status='Active').all()
    form.department_id.choices = [(dept.id, dept.name) for dept in depts]

    if form.validate_on_submit():
        # Check conflict excluding current appointment
        conflict = Appointment.query.filter(
            Appointment.doctor_id == form.doctor_id.data,
            Appointment.appointment_date == form.appointment_date.data,
            Appointment.appointment_time == form.appointment_time.data,
            Appointment.id != appointment.id,
            Appointment.status.in_(['Scheduled', 'Confirmed'])
        ).first()

        if conflict:
            flash(f"Scheduling Conflict: Dr. {conflict.doctor.name} already has an appointment at {form.appointment_time.data} on {form.appointment_date.data.strftime('%Y-%m-%d')}.", 'danger')
            return render_template('appointments/form.html', form=form, title=f"Reschedule Appointment: {appointment.appointment_id}", appointment=appointment)

        appointment.doctor_id = form.doctor_id.data
        appointment.department_id = form.department_id.data
        appointment.appointment_date = form.appointment_date.data
        appointment.appointment_time = form.appointment_time.data
        appointment.appointment_type = form.appointment_type.data
        appointment.reason = form.reason.data.strip()
        appointment.notes = form.notes.data.strip() if form.notes.data else None
        appointment.status = 'Scheduled'

        db.session.commit()
        log_audit('RESCHEDULE_APPOINTMENT', 'Appointment', f"Rescheduled appointment {appointment.appointment_id} to {appointment.appointment_date} at {appointment.appointment_time}.")
        flash(f"Appointment {appointment.appointment_id} rescheduled successfully.", 'success')
        return redirect(url_for('appointments.index'))

    return render_template('appointments/form.html', form=form, title=f"Reschedule Appointment: {appointment.appointment_id}", appointment=appointment)
