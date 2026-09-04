from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.medical_record import MedicalRecord, Vitals
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.forms.clinical_forms import MedicalRecordForm, VitalsForm
from app.utils.id_generator import generate_record_id
from app.utils.audit import log_audit
from app.utils.decorators import roles_required

medical_records_bp = Blueprint('medical_records', __name__, url_prefix='/medical-records')

@medical_records_bp.route('/')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor', 'Nurse')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    patient_id = request.args.get('patient_id', type=int)

    query = MedicalRecord.query
    if patient_id:
        query = query.filter(MedicalRecord.patient_id == patient_id)
    if search:
        search_fmt = f"%{search}%"
        query = query.join(Patient).filter(
            (MedicalRecord.record_id.ilike(search_fmt)) |
            (MedicalRecord.diagnosis.ilike(search_fmt)) |
            (Patient.first_name.ilike(search_fmt)) |
            (Patient.last_name.ilike(search_fmt))
        )

    records = query.order_by(MedicalRecord.visit_date.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('medical_records/index.html', records=records, search=search, patient_id=patient_id)

@medical_records_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor')
def create():
    form = MedicalRecordForm()
    patients = Patient.query.order_by(Patient.first_name.asc()).all()
    form.patient_id.choices = [(p.id, f"{p.full_name} ({p.patient_id})") for p in patients]

    doctors = Doctor.query.filter_by(status='Active').all()
    form.doctor_id.choices = [(d.id, f"{d.name} ({d.specialization})") for d in doctors]

    # Pre-select if passed in query params
    pre_patient = request.args.get('patient_id', type=int)
    if pre_patient and request.method == 'GET':
        form.patient_id.data = pre_patient

    # Auto select current doctor if logged in as doctor
    if current_user.role_name == 'Doctor' and request.method == 'GET':
        doc = Doctor.query.filter_by(email=current_user.email).first()
        if doc:
            form.doctor_id.data = doc.id

    if form.validate_on_submit():
        rec_id = generate_record_id()
        record = MedicalRecord(
            record_id=rec_id,
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            visit_date=datetime.utcnow(),
            symptoms=form.symptoms.data.strip(),
            diagnosis=form.diagnosis.data.strip(),
            clinical_notes=form.clinical_notes.data.strip() if form.clinical_notes.data else None,
            treatment_plan=form.treatment_plan.data.strip(),
            follow_up_date=form.follow_up_date.data
        )
        db.session.add(record)
        db.session.commit()

        log_audit('CREATE_MEDICAL_RECORD', 'Medical Record', f"Created clinical encounter record {record.record_id} for Patient ID {record.patient_id}.")
        flash(f"Clinical record {record.record_id} saved successfully.", 'success')
        return redirect(url_for('patients.view_profile', patient_id=record.patient_id))

    return render_template('medical_records/form.html', form=form, title='New Clinical Consultation Record')

@medical_records_bp.route('/<int:record_id>')
@login_required
def view_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    return render_template('medical_records/detail.html', record=record)

@medical_records_bp.route('/vitals/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor', 'Nurse')
def record_vitals():
    form = VitalsForm()
    patients = Patient.query.order_by(Patient.first_name.asc()).all()
    form.patient_id.choices = [(p.id, f"{p.full_name} ({p.patient_id})") for p in patients]

    pre_patient = request.args.get('patient_id', type=int)
    if pre_patient and request.method == 'GET':
        form.patient_id.data = pre_patient

    if form.validate_on_submit():
        vitals = Vitals(
            patient_id=form.patient_id.data,
            recorded_by=current_user.full_name,
            recorded_at=datetime.utcnow(),
            temperature=form.temperature.data,
            bp_systolic=form.bp_systolic.data,
            bp_diastolic=form.bp_diastolic.data,
            heart_rate=form.heart_rate.data,
            respiratory_rate=form.respiratory_rate.data,
            spo2=form.spo2.data,
            weight_kg=form.weight_kg.data,
            height_cm=form.height_cm.data,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        vitals.calculate_bmi()
        db.session.add(vitals)
        db.session.commit()

        log_audit('RECORD_VITALS', 'Vitals', f"Recorded vital signs for Patient ID {vitals.patient_id}.")
        flash('Patient vital signs recorded successfully.', 'success')
        return redirect(url_for('patients.view_profile', patient_id=vitals.patient_id))

    return render_template('medical_records/vitals_form.html', form=form, title='Record Patient Vital Signs')
