from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.laboratory import LabTest, LabOrder, LabResult
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.forms.lab_forms import LabTestForm, LabOrderForm, LabResultForm
from app.utils.id_generator import generate_lab_test_code, generate_lab_order_id
from app.utils.audit import log_audit
from app.utils.notifications import create_notification
from app.utils.decorators import roles_required
from app.utils.helpers import export_csv_response

laboratory_bp = Blueprint('laboratory', __name__, url_prefix='/laboratory')

@laboratory_bp.route('/')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Lab Technician', 'Doctor', 'Nurse')
def index():
    status = request.args.get('status', '', type=str)
    priority = request.args.get('priority', '', type=str)
    search = request.args.get('search', '', type=str).strip()

    query = LabOrder.query
    if status:
        query = query.filter(LabOrder.status == status)
    if priority:
        query = query.filter(LabOrder.priority == priority)
    if search:
        search_fmt = f"%{search}%"
        query = query.join(Patient).filter(
            (LabOrder.order_id.ilike(search_fmt)) |
            (Patient.first_name.ilike(search_fmt)) |
            (Patient.last_name.ilike(search_fmt)) |
            (Patient.patient_id.ilike(search_fmt))
        )

    orders = query.order_by(LabOrder.order_date.desc()).all()
    
    # Counts
    pending_count = LabOrder.query.filter(LabOrder.status.in_(['Requested', 'Sample Collected', 'Processing'])).count()
    completed_count = LabOrder.query.filter_by(status='Completed').count()

    return render_template(
        'laboratory/index.html',
        orders=orders,
        status=status,
        priority=priority,
        search=search,
        pending_count=pending_count,
        completed_count=completed_count
    )

@laboratory_bp.route('/tests')
@login_required
def tests_catalog():
    tests = LabTest.query.order_by(LabTest.category.asc(), LabTest.test_name.asc()).all()
    return render_template('laboratory/tests_catalog.html', tests=tests)

@laboratory_bp.route('/tests/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Lab Technician')
def create_test():
    form = LabTestForm()
    if form.validate_on_submit():
        code = generate_lab_test_code()
        lab_test = LabTest(
            test_code=code,
            test_name=form.test_name.data.strip(),
            category=form.category.data,
            price=form.price.data,
            normal_range=form.normal_range.data.strip() if form.normal_range.data else None,
            unit=form.unit.data.strip() if form.unit.data else None,
            sample_type=form.sample_type.data,
            turnaround_hours=form.turnaround_hours.data or 24,
            description=form.description.data.strip() if form.description.data else None,
            status=form.status.data
        )
        db.session.add(lab_test)
        db.session.commit()

        log_audit('CREATE_LAB_TEST', 'Laboratory', f"Created lab test {lab_test.test_name} ({lab_test.test_code}).")
        flash(f"Lab test '{lab_test.test_name}' ({lab_test.test_code}) added to catalog.", 'success')
        return redirect(url_for('laboratory.tests_catalog'))

    return render_template('laboratory/test_form.html', form=form, title='Add Diagnostic Lab Test')

@laboratory_bp.route('/tests/<int:test_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Lab Technician')
def edit_test(test_id):
    lab_test = LabTest.query.get_or_404(test_id)
    form = LabTestForm(obj=lab_test)

    if form.validate_on_submit():
        lab_test.test_name = form.test_name.data.strip()
        lab_test.category = form.category.data
        lab_test.price = form.price.data
        lab_test.normal_range = form.normal_range.data.strip() if form.normal_range.data else None
        lab_test.unit = form.unit.data.strip() if form.unit.data else None
        lab_test.sample_type = form.sample_type.data
        lab_test.turnaround_hours = form.turnaround_hours.data or 24
        lab_test.description = form.description.data.strip() if form.description.data else None
        lab_test.status = form.status.data

        db.session.commit()
        log_audit('UPDATE_LAB_TEST', 'Laboratory', f"Updated lab test {lab_test.test_name}.")
        flash(f"Lab test '{lab_test.test_name}' updated successfully.", 'success')
        return redirect(url_for('laboratory.tests_catalog'))

    return render_template('laboratory/test_form.html', form=form, title=f"Edit Lab Test: {lab_test.test_name}", lab_test=lab_test)

@laboratory_bp.route('/order/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Doctor', 'Nurse')
def create_order():
    form = LabOrderForm()
    patients = Patient.query.order_by(Patient.first_name.asc()).all()
    form.patient_id.choices = [(p.id, f"{p.full_name} ({p.patient_id})") for p in patients]

    doctors = Doctor.query.filter_by(status='Active').all()
    form.doctor_id.choices = [(d.id, f"{d.name} ({d.specialization})") for d in doctors]

    tests = LabTest.query.filter_by(status='Active').order_by(LabTest.test_name.asc()).all()
    form.lab_test_id.choices = [(t.id, f"{t.test_name} - ₹{t.price:0.2f} ({t.category})") for t in tests]

    pre_patient = request.args.get('patient_id', type=int)
    if pre_patient and request.method == 'GET':
        form.patient_id.data = pre_patient

    if current_user.role_name == 'Doctor' and request.method == 'GET':
        doc = Doctor.query.filter_by(email=current_user.email).first()
        if doc:
            form.doctor_id.data = doc.id

    if form.validate_on_submit():
        order_code = generate_lab_order_id()
        selected_test = LabTest.query.get(form.lab_test_id.data)

        order = LabOrder(
            order_id=order_code,
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            lab_test_id=form.lab_test_id.data,
            priority=form.priority.data,
            clinical_notes=form.clinical_notes.data.strip() if form.clinical_notes.data else None,
            status='Requested'
        )
        db.session.add(order)
        db.session.commit()

        log_audit('ORDER_LAB_TEST', 'Laboratory', f"Ordered test {selected_test.test_name} ({order.order_id}) for Patient ID {order.patient_id}.")
        create_notification(
            title=f"New Lab Order: {selected_test.test_name}",
            message=f"Order {order.order_id} requested ({order.priority} priority) for {order.patient.full_name}.",
            target_role='Lab Technician',
            notification_type='warning' if order.priority != 'Normal' else 'info',
            link=url_for('laboratory.index')
        )

        flash(f"Laboratory investigation request '{order.order_id}' submitted successfully.", 'success')
        return redirect(url_for('laboratory.index'))

    return render_template('laboratory/order_form.html', form=form, title='Request Diagnostic Investigation')

@laboratory_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Lab Technician')
def update_order_status(order_id):
    order = LabOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')

    if new_status in ['Sample Collected', 'Processing', 'Cancelled']:
        order.status = new_status
        if new_status == 'Sample Collected':
            order.sample_collected_at = datetime.utcnow()
        db.session.commit()

        log_audit('UPDATE_LAB_ORDER_STATUS', 'Laboratory', f"Lab Order {order.order_id} status changed to {new_status}.")
        flash(f"Lab Order {order.order_id} marked as '{new_status}'.", 'info')

    return redirect(url_for('laboratory.index'))

@laboratory_bp.route('/orders/<int:order_id>/result', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Lab Technician')
def enter_result(order_id):
    order = LabOrder.query.get_or_404(order_id)
    existing_result = order.result
    form = LabResultForm(obj=existing_result)

    if request.method == 'GET' and not existing_result:
        form.reference_range.data = order.lab_test.normal_range
        form.unit.data = order.lab_test.unit
        form.technician_name.data = current_user.full_name

    if form.validate_on_submit():
        if not existing_result:
            result = LabResult(
                lab_order_id=order.id,
                result_value=form.result_value.data.strip(),
                reference_range=form.reference_range.data.strip() if form.reference_range.data else None,
                unit=form.unit.data.strip() if form.unit.data else None,
                status_flag=form.status_flag.data,
                technician_name=form.technician_name.data.strip(),
                verified_by=form.verified_by.data.strip() if form.verified_by.data else None,
                remarks=form.remarks.data.strip() if form.remarks.data else None,
                completed_at=datetime.utcnow()
            )
            db.session.add(result)
        else:
            existing_result.result_value = form.result_value.data.strip()
            existing_result.reference_range = form.reference_range.data.strip() if form.reference_range.data else None
            existing_result.unit = form.unit.data.strip() if form.unit.data else None
            existing_result.status_flag = form.status_flag.data
            existing_result.technician_name = form.technician_name.data.strip()
            existing_result.verified_by = form.verified_by.data.strip() if form.verified_by.data else None
            existing_result.remarks = form.remarks.data.strip() if form.remarks.data else None

        order.status = 'Completed'
        db.session.commit()

        log_audit('PUBLISH_LAB_RESULT', 'Laboratory', f"Published test results for {order.order_id} ({order.lab_test.test_name}). Flag: {form.status_flag.data}.")
        
        # If critical flag, send urgent notification
        if form.status_flag.data == 'Critical':
            create_notification(
                title=f"CRITICAL LAB ALERT: {order.patient.full_name}",
                message=f"Critical test finding for {order.lab_test.test_name} on Order {order.order_id}. Immediate clinical action required.",
                target_role='Doctor',
                notification_type='danger',
                link=url_for('laboratory.print_report', order_id=order.id)
            )

        flash(f"Laboratory result for '{order.order_id}' published successfully!", 'success')
        return redirect(url_for('laboratory.print_report', order_id=order.id))

    return render_template('laboratory/result_form.html', form=form, order=order)

@laboratory_bp.route('/orders/<int:order_id>/report')
@login_required
def print_report(order_id):
    order = LabOrder.query.get_or_404(order_id)
    if not order.result:
        flash('Results have not been published for this test order yet.', 'warning')
        return redirect(url_for('laboratory.index'))
    return render_template('laboratory/print_report.html', order=order)
