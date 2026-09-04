from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.forms.patient_forms import PatientForm
from app.utils.id_generator import generate_patient_id
from app.utils.audit import log_audit
from app.utils.decorators import roles_required
from app.utils.helpers import export_csv_response

patients_bp = Blueprint('patients', __name__, url_prefix='/patients')

@patients_bp.route('/')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor', 'Nurse', 'Receptionist', 'Accountant')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    gender = request.args.get('gender', '', type=str)
    blood_group = request.args.get('blood_group', '', type=str)
    status = request.args.get('status', '', type=str)
    dept_id = request.args.get('department_id', '', type=str)

    query = Patient.query

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Patient.patient_id.ilike(search_fmt)) |
            (Patient.first_name.ilike(search_fmt)) |
            (Patient.last_name.ilike(search_fmt)) |
            (Patient.phone.ilike(search_fmt)) |
            (Patient.email.ilike(search_fmt))
        )
    if gender:
        query = query.filter(Patient.gender == gender)
    if blood_group:
        query = query.filter(Patient.blood_group == blood_group)
    if status:
        query = query.filter(Patient.status == status)
    if dept_id and dept_id.isdigit():
        query = query.filter(Patient.department_id == int(dept_id))

    patients = query.order_by(Patient.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    departments = Department.query.filter_by(status='Active').all()

    return render_template(
        'patients/index.html',
        patients=patients,
        departments=departments,
        search=search,
        gender=gender,
        blood_group=blood_group,
        status=status,
        department_id=dept_id
    )

@patients_bp.route('/export-csv')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Receptionist', 'Accountant')
def export_csv():
    patients = Patient.query.order_by(Patient.patient_id.asc()).all()
    headers = ['Patient ID', 'Full Name', 'DOB', 'Gender', 'Blood Group', 'Phone', 'Email', 'Address', 'Status', 'Registered Date']
    rows = []
    for p in patients:
        rows.append([
            p.patient_id,
            p.full_name,
            p.dob.strftime('%Y-%m-%d') if p.dob else '',
            p.gender,
            p.blood_group or '',
            p.phone,
            p.email or '',
            p.address,
            p.status,
            p.registration_date.strftime('%Y-%m-%d') if p.registration_date else ''
        ])
    return export_csv_response('patients_master_list', headers, rows)

@patients_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Receptionist', 'Nurse', 'Doctor')
def create():
    form = PatientForm()
    # Populate dropdown choices
    depts = Department.query.filter_by(status='Active').all()
    form.department_id.choices = [(0, '-- None / Unassigned --')] + [(d.id, d.name) for d in depts]
    doctors = Doctor.query.filter_by(status='Active').all()
    form.primary_doctor_id.choices = [(0, '-- None / Unassigned --')] + [(doc.id, f"{doc.name} ({doc.specialization})") for doc in doctors]

    if form.validate_on_submit():
        pid = generate_patient_id()
        patient = Patient(
            patient_id=pid,
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            dob=form.dob.data,
            gender=form.gender.data,
            blood_group=form.blood_group.data if form.blood_group.data else None,
            phone=form.phone.data.strip(),
            email=form.email.data.strip().lower() if form.email.data else None,
            address=form.address.data.strip(),
            city=form.city.data.strip() if form.city.data else None,
            state=form.state.data.strip() if form.state.data else None,
            zip_code=form.zip_code.data.strip() if form.zip_code.data else None,
            emergency_contact_name=form.emergency_contact_name.data.strip() if form.emergency_contact_name.data else None,
            emergency_contact_phone=form.emergency_contact_phone.data.strip() if form.emergency_contact_phone.data else None,
            emergency_contact_relation=form.emergency_contact_relation.data.strip() if form.emergency_contact_relation.data else None,
            medical_history=form.medical_history.data.strip() if form.medical_history.data else None,
            allergies=form.allergies.data.strip() if form.allergies.data else None,
            existing_conditions=form.existing_conditions.data.strip() if form.existing_conditions.data else None,
            department_id=form.department_id.data if (form.department_id.data and form.department_id.data > 0) else None,
            primary_doctor_id=form.primary_doctor_id.data if (form.primary_doctor_id.data and form.primary_doctor_id.data > 0) else None,
            status=form.status.data
        )
        db.session.add(patient)
        db.session.commit()

        log_audit('CREATE_PATIENT', 'Patient', f"Registered new patient {patient.full_name} ({patient.patient_id}).")
        flash(f"Patient record for '{patient.full_name}' ({patient.patient_id}) created successfully!", 'success')
        return redirect(url_for('patients.view_profile', patient_id=patient.id))

    return render_template('patients/form.html', form=form, title='Register New Patient')

@patients_bp.route('/<int:patient_id>')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor', 'Nurse', 'Receptionist', 'Accountant', 'Pharmacist', 'Lab Technician')
def view_profile(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Pre-fetch related records
    appointments = patient.appointments.all()
    medical_records = patient.medical_records.all()
    vitals_history = patient.vitals_records.all()
    prescriptions = patient.prescriptions.all()
    lab_orders = patient.lab_orders.all()
    admissions = patient.admissions.all()
    invoices = patient.invoices.all()

    active_admission = patient.admissions.filter_by(status='Admitted').first()

    return render_template(
        'patients/profile.html',
        patient=patient,
        appointments=appointments,
        medical_records=medical_records,
        vitals_history=vitals_history,
        prescriptions=prescriptions,
        lab_orders=lab_orders,
        admissions=admissions,
        invoices=invoices,
        active_admission=active_admission
    )

@patients_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Receptionist', 'Nurse', 'Doctor')
def edit(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientForm(obj=patient)

    depts = Department.query.filter_by(status='Active').all()
    form.department_id.choices = [(0, '-- None / Unassigned --')] + [(d.id, d.name) for d in depts]
    doctors = Doctor.query.filter_by(status='Active').all()
    form.primary_doctor_id.choices = [(0, '-- None / Unassigned --')] + [(doc.id, f"{doc.name} ({doc.specialization})") for doc in doctors]

    if request.method == 'GET':
        form.department_id.data = patient.department_id or 0
        form.primary_doctor_id.data = patient.primary_doctor_id or 0

    if form.validate_on_submit():
        patient.first_name = form.first_name.data.strip()
        patient.last_name = form.last_name.data.strip()
        patient.dob = form.dob.data
        patient.gender = form.gender.data
        patient.blood_group = form.blood_group.data if form.blood_group.data else None
        patient.phone = form.phone.data.strip()
        patient.email = form.email.data.strip().lower() if form.email.data else None
        patient.address = form.address.data.strip()
        patient.city = form.city.data.strip() if form.city.data else None
        patient.state = form.state.data.strip() if form.state.data else None
        patient.zip_code = form.zip_code.data.strip() if form.zip_code.data else None
        patient.emergency_contact_name = form.emergency_contact_name.data.strip() if form.emergency_contact_name.data else None
        patient.emergency_contact_phone = form.emergency_contact_phone.data.strip() if form.emergency_contact_phone.data else None
        patient.emergency_contact_relation = form.emergency_contact_relation.data.strip() if form.emergency_contact_relation.data else None
        patient.medical_history = form.medical_history.data.strip() if form.medical_history.data else None
        patient.allergies = form.allergies.data.strip() if form.allergies.data else None
        patient.existing_conditions = form.existing_conditions.data.strip() if form.existing_conditions.data else None
        patient.department_id = form.department_id.data if form.department_id.data > 0 else None
        patient.primary_doctor_id = form.primary_doctor_id.data if form.primary_doctor_id.data > 0 else None
        patient.status = form.status.data

        db.session.commit()
        log_audit('UPDATE_PATIENT', 'Patient', f"Updated patient details for {patient.full_name} ({patient.patient_id}).")
        flash(f"Patient record for '{patient.full_name}' updated successfully!", 'success')
        return redirect(url_for('patients.view_profile', patient_id=patient.id))

    return render_template('patients/form.html', form=form, title=f"Edit Patient: {patient.full_name}", patient=patient)

@patients_bp.route('/<int:patient_id>/toggle-status', methods=['POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Receptionist')
def toggle_status(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    new_status = 'Inactive' if patient.status == 'Active' else 'Active'
    patient.status = new_status
    db.session.commit()

    log_audit('UPDATE_PATIENT_STATUS', 'Patient', f"Changed status of {patient.full_name} to {new_status}.")
    flash(f"Patient '{patient.full_name}' status updated to {new_status}.", 'info')
    return redirect(url_for('patients.view_profile', patient_id=patient.id))
