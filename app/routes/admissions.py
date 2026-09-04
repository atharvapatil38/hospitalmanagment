from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.admission import Admission, Room, Bed, DischargeSummary
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.forms.admission_forms import AdmissionForm, DischargeForm, BedTransferForm
from app.utils.id_generator import generate_admission_id
from app.utils.audit import log_audit
from app.utils.notifications import create_notification
from app.utils.decorators import roles_required

admissions_bp = Blueprint('admissions', __name__, url_prefix='/admissions')

@admissions_bp.route('/')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor', 'Nurse', 'Receptionist', 'Accountant')
def index():
    status_filter = request.args.get('status', 'Admitted', type=str)
    search = request.args.get('search', '', type=str).strip()

    query = Admission.query
    if status_filter and status_filter != 'All':
        query = query.filter(Admission.status == status_filter)

    if search:
        search_fmt = f"%{search}%"
        query = query.join(Patient).filter(
            (Admission.admission_id.ilike(search_fmt)) |
            (Patient.first_name.ilike(search_fmt)) |
            (Patient.last_name.ilike(search_fmt)) |
            (Patient.patient_id.ilike(search_fmt))
        )

    admissions = query.order_by(Admission.admission_date.desc()).all()
    active_count = Admission.query.filter_by(status='Admitted').count()
    discharged_count = Admission.query.filter_by(status='Discharged').count()

    return render_template(
        'admissions/index.html',
        admissions=admissions,
        status_filter=status_filter,
        search=search,
        active_count=active_count,
        discharged_count=discharged_count
    )

@admissions_bp.route('/admit', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Receptionist', 'Doctor', 'Nurse')
def admit():
    form = AdmissionForm()
    
    # Choices
    patients = Patient.query.filter(Patient.status != 'Admitted').order_by(Patient.first_name.asc()).all()
    form.patient_id.choices = [(p.id, f"{p.full_name} ({p.patient_id}) - {p.gender}, Age: {p.age}") for p in patients]

    doctors = Doctor.query.filter_by(status='Active').all()
    form.doctor_id.choices = [(d.id, f"{d.name} ({d.specialization})") for d in doctors]

    depts = Department.query.filter_by(status='Active').all()
    form.department_id.choices = [(dept.id, dept.name) for dept in depts]

    rooms = Room.query.filter_by(status='Available').all()
    form.room_id.choices = [(r.id, f"Room {r.room_number} ({r.room_type}) - ₹{r.daily_charge}/day") for r in rooms]

    available_beds = Bed.query.filter_by(status='Available').all()
    form.bed_id.choices = [(b.id, f"Room {b.room.room_number} - {b.bed_number}") for b in available_beds]

    # Pre-populate patient if passed in URL
    pre_patient = request.args.get('patient_id', type=int)
    if pre_patient and request.method == 'GET':
        form.patient_id.data = pre_patient

    if form.validate_on_submit():
        bed = Bed.query.get(form.bed_id.data)
        if not bed or bed.status != 'Available':
            flash('The selected bed is no longer available. Please select another bed.', 'danger')
            return render_template('admissions/form.html', form=form, title='Inpatient Admission')

        patient = Patient.query.get(form.patient_id.data)
        adm_id = generate_admission_id()
        admission = Admission(
            admission_id=adm_id,
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            department_id=form.department_id.data,
            room_id=form.room_id.data,
            bed_id=form.bed_id.data,
            admission_date=datetime.utcnow(),
            reason_for_admission=form.reason_for_admission.data.strip(),
            initial_diagnosis=form.initial_diagnosis.data.strip(),
            status='Admitted'
        )
        db.session.add(admission)
        db.session.flush() # get admission.id

        # Update Bed status
        bed.status = 'Occupied'
        bed.current_admission_id = admission.id

        # Update Patient status
        patient.status = 'Admitted'

        # Check Room fullness
        if bed.room.available_beds_count == 0:
            bed.room.status = 'Full'

        db.session.commit()

        log_audit('ADMIT_PATIENT', 'Inpatient', f"Admitted patient {patient.full_name} ({admission.admission_id}) to Room {bed.room.room_number}, {bed.bed_number}.")
        create_notification(
            title=f"Patient Admitted: {patient.full_name}",
            message=f"Patient admitted to Room {bed.room.room_number}, {bed.bed_number} under Dr. {admission.doctor.name}.",
            target_role='Nurse',
            link=url_for('admissions.index')
        )

        flash(f"Patient '{patient.full_name}' admitted successfully! Admission ID: {admission.admission_id}", 'success')
        return redirect(url_for('admissions.index'))

    return render_template('admissions/form.html', form=form, title='Inpatient Admission')

@admissions_bp.route('/<int:adm_id>/discharge', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor', 'Nurse')
def discharge(adm_id):
    admission = Admission.query.get_or_404(adm_id)
    if admission.status != 'Admitted':
        flash('This patient admission is already discharged.', 'info')
        return redirect(url_for('admissions.view_summary', adm_id=admission.id))

    form = DischargeForm()
    if request.method == 'GET':
        form.final_diagnosis.data = admission.initial_diagnosis
        form.doctor_signature.data = f"Dr. {admission.doctor.name}"

    if form.validate_on_submit():
        discharge_time = datetime.utcnow()
        admission.discharge_date = discharge_time
        admission.status = 'Discharged'

        summary = DischargeSummary(
            admission_id=admission.id,
            discharge_date=discharge_time,
            condition_at_discharge=form.condition_at_discharge.data,
            final_diagnosis=form.final_diagnosis.data.strip(),
            treatment_summary=form.treatment_summary.data.strip(),
            discharge_medications=form.discharge_medications.data.strip() if form.discharge_medications.data else None,
            advice_instructions=form.advice_instructions.data.strip() if form.advice_instructions.data else None,
            follow_up_date=form.follow_up_date.data,
            doctor_signature=form.doctor_signature.data.strip()
        )
        db.session.add(summary)

        # Release Bed
        if admission.bed:
            admission.bed.status = 'Available'
            admission.bed.current_admission_id = None
            if admission.room and admission.room.status == 'Full':
                admission.room.status = 'Available'

        # Update Patient status
        admission.patient.status = 'Discharged'

        db.session.commit()

        log_audit('DISCHARGE_PATIENT', 'Inpatient', f"Discharged patient {admission.patient.full_name} from Admission {admission.admission_id}.")
        flash(f"Patient '{admission.patient.full_name}' discharged successfully. Bed {admission.bed.bed_number} is now released.", 'success')
        return redirect(url_for('admissions.view_summary', adm_id=admission.id))

    return render_template('admissions/discharge_form.html', form=form, admission=admission)

@admissions_bp.route('/<int:adm_id>/transfer', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor', 'Nurse')
def transfer_bed(adm_id):
    admission = Admission.query.get_or_404(adm_id)
    if admission.status != 'Admitted':
        flash('Cannot transfer bed for a discharged patient.', 'danger')
        return redirect(url_for('admissions.index'))

    form = BedTransferForm()
    rooms = Room.query.all()
    form.new_room_id.choices = [(r.id, f"Room {r.room_number} ({r.room_type})") for r in rooms]
    available_beds = Bed.query.filter_by(status='Available').all()
    form.new_bed_id.choices = [(b.id, f"Room {b.room.room_number} - {b.bed_number}") for b in available_beds]

    if form.validate_on_submit():
        new_bed = Bed.query.get(form.new_bed_id.data)
        if not new_bed or new_bed.status != 'Available':
            flash('Selected target bed is no longer available.', 'danger')
            return render_template('admissions/transfer_form.html', form=form, admission=admission)

        old_bed = admission.bed
        if old_bed:
            old_bed.status = 'Available'
            old_bed.current_admission_id = None

        new_bed.status = 'Occupied'
        new_bed.current_admission_id = admission.id

        admission.room_id = new_bed.room_id
        admission.bed_id = new_bed.id

        db.session.commit()

        log_audit('TRANSFER_BED', 'Inpatient', f"Transferred patient {admission.patient.full_name} to Room {new_bed.room.room_number}, {new_bed.bed_number}. Reason: {form.transfer_reason.data}")
        flash(f"Patient successfully transferred to Room {new_bed.room.room_number}, {new_bed.bed_number}.", 'success')
        return redirect(url_for('admissions.index'))

    return render_template('admissions/transfer_form.html', form=form, admission=admission)

@admissions_bp.route('/<int:adm_id>/summary')
@login_required
def view_summary(adm_id):
    admission = Admission.query.get_or_404(adm_id)
    summary = admission.discharge_summary
    return render_template('admissions/discharge_summary.html', admission=admission, summary=summary)
