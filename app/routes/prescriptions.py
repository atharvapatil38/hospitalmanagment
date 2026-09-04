from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.prescription import Prescription, PrescriptionItem
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.pharmacy import Medicine
from app.forms.clinical_forms import PrescriptionForm
from app.utils.id_generator import generate_prescription_id
from app.utils.audit import log_audit
from app.utils.decorators import roles_required

prescriptions_bp = Blueprint('prescriptions', __name__, url_prefix='/prescriptions')

@prescriptions_bp.route('/')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor', 'Nurse', 'Pharmacist')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    status = request.args.get('status', '', type=str)

    query = Prescription.query
    if search:
        search_fmt = f"%{search}%"
        query = query.join(Patient).filter(
            (Prescription.prescription_id.ilike(search_fmt)) |
            (Prescription.diagnosis.ilike(search_fmt)) |
            (Patient.first_name.ilike(search_fmt)) |
            (Patient.last_name.ilike(search_fmt)) |
            (Patient.patient_id.ilike(search_fmt))
        )
    if status:
        query = query.filter(Prescription.status == status)

    prescriptions = query.order_by(Prescription.prescription_date.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('prescriptions/index.html', prescriptions=prescriptions, search=search, status=status)

@prescriptions_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor')
def create():
    form = PrescriptionForm()
    patients = Patient.query.order_by(Patient.first_name.asc()).all()
    form.patient_id.choices = [(p.id, f"{p.full_name} ({p.patient_id}) - Age: {p.age}") for p in patients]

    doctors = Doctor.query.filter_by(status='Active').all()
    form.doctor_id.choices = [(d.id, f"{d.name} ({d.specialization})") for d in doctors]

    medicines = Medicine.query.filter_by(status='Active').order_by(Medicine.name.asc()).all()

    pre_patient = request.args.get('patient_id', type=int)
    if pre_patient and request.method == 'GET':
        form.patient_id.data = pre_patient

    if current_user.role_name == 'Doctor' and request.method == 'GET':
        doc = Doctor.query.filter_by(email=current_user.email).first()
        if doc:
            form.doctor_id.data = doc.id

    if form.validate_on_submit():
        med_names = request.form.getlist('med_name[]')
        dosages = request.form.getlist('dosage[]')
        frequencies = request.form.getlist('frequency[]')
        durations = request.form.getlist('duration[]')
        instructions = request.form.getlist('instructions[]')
        med_ids = request.form.getlist('med_id[]')

        if not med_names or len(med_names) == 0 or not med_names[0].strip():
            flash('Please add at least one medication item to this prescription.', 'danger')
            return render_template('prescriptions/form.html', form=form, medicines=medicines, title='Create Medical Prescription')

        rx_id = generate_prescription_id()
        prescription = Prescription(
            prescription_id=rx_id,
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            prescription_date=datetime.utcnow().date(),
            diagnosis=form.diagnosis.data.strip(),
            general_advice=form.general_advice.data.strip() if form.general_advice.data else None,
            status='Active'
        )
        db.session.add(prescription)
        db.session.flush()

        # Add items
        for i in range(len(med_names)):
            if med_names[i].strip():
                m_id = int(med_ids[i]) if (i < len(med_ids) and med_ids[i].isdigit() and int(med_ids[i]) > 0) else None
                item = PrescriptionItem(
                    prescription_id=prescription.id,
                    medicine_id=m_id,
                    medicine_name=med_names[i].strip(),
                    dosage=dosages[i].strip() if i < len(dosages) else '1 tablet',
                    frequency=frequencies[i].strip() if i < len(frequencies) else 'Twice Daily',
                    duration=durations[i].strip() if i < len(durations) else '5 Days',
                    instructions=instructions[i].strip() if i < len(instructions) else 'After food'
                )
                db.session.add(item)

        db.session.commit()
        log_audit('CREATE_PRESCRIPTION', 'Prescription', f"Issued prescription {prescription.prescription_id} for Patient ID {prescription.patient_id}.")
        flash(f"Prescription {prescription.prescription_id} generated successfully!", 'success')
        return redirect(url_for('prescriptions.print_rx', rx_id=prescription.id))

    return render_template('prescriptions/form.html', form=form, medicines=medicines, title='Create Medical Prescription')

@prescriptions_bp.route('/<int:rx_id>/print')
@login_required
def print_rx(rx_id):
    prescription = Prescription.query.get_or_404(rx_id)
    return render_template('prescriptions/print_rx.html', prescription=prescription)
