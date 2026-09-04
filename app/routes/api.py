from datetime import datetime, date, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import func
from app.extensions import db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.appointment import Appointment
from app.models.admission import Room, Bed, Admission
from app.models.billing import Invoice, Payment
from app.models.pharmacy import Medicine

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/dashboard-charts')
@login_required
def dashboard_charts():
    today = date.today()

    # 1. Monthly Revenue (Past 6 months)
    revenue_labels = []
    revenue_data = []
    for i in range(5, -1, -1):
        # Calculate year and month
        month = (today.month - i - 1) % 12 + 1
        year = today.year + ((today.month - i - 1) // 12)
        month_name = datetime(year, month, 1).strftime('%b %Y')
        revenue_labels.append(month_name)

        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)

        rev = db.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_date >= start,
            Payment.payment_date < end
        ).scalar() or 0.0
        revenue_data.append(round(float(rev), 2))

    # 2. Patient Registrations (Past 6 months)
    patient_trend_data = []
    for i in range(5, -1, -1):
        month = (today.month - i - 1) % 12 + 1
        year = today.year + ((today.month - i - 1) // 12)
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)

        count = Patient.query.filter(
            Patient.registration_date >= start,
            Patient.registration_date < end
        ).count()
        patient_trend_data.append(count)

    # 3. Department Distribution
    dept_labels = []
    dept_data = []
    departments = Department.query.filter_by(status='Active').all()
    for d in departments:
        dept_labels.append(d.name)
        dept_data.append(d.patients.count())

    # 4. Bed Occupancy
    occupied_beds = Bed.query.filter_by(status='Occupied').count()
    available_beds = Bed.query.filter_by(status='Available').count()
    maintenance_beds = Bed.query.filter_by(status='Maintenance').count()
    reserved_beds = Bed.query.filter_by(status='Reserved').count()

    # 5. Appointment Status Distribution
    apt_scheduled = Appointment.query.filter_by(status='Scheduled').count()
    apt_confirmed = Appointment.query.filter_by(status='Confirmed').count()
    apt_completed = Appointment.query.filter_by(status='Completed').count()
    apt_cancelled = Appointment.query.filter(Appointment.status.in_(['Cancelled', 'No Show'])).count()

    return jsonify({
        'revenue': {
            'labels': revenue_labels,
            'data': revenue_data
        },
        'patient_trend': {
            'labels': revenue_labels,
            'data': patient_trend_data
        },
        'departments': {
            'labels': dept_labels,
            'data': dept_data
        },
        'beds': {
            'labels': ['Occupied', 'Available', 'Maintenance', 'Reserved'],
            'data': [occupied_beds, available_beds, maintenance_beds, reserved_beds]
        },
        'appointments': {
            'labels': ['Scheduled', 'Confirmed', 'Completed', 'Cancelled/No-Show'],
            'data': [apt_scheduled, apt_confirmed, apt_completed, apt_cancelled]
        }
    })

@api_bp.route('/rooms/<int:room_id>/available-beds')
@login_required
def get_available_beds(room_id):
    beds = Bed.query.filter_by(room_id=room_id, status='Available').all()
    return jsonify([{'id': b.id, 'bed_number': b.bed_number} for b in beds])

@api_bp.route('/medicines/<int:medicine_id>')
@login_required
def get_medicine_info(medicine_id):
    med = Medicine.query.get_or_404(medicine_id)
    return jsonify({
        'id': med.id,
        'name': med.name,
        'generic_name': med.generic_name,
        'selling_price': med.selling_price,
        'quantity_in_stock': med.quantity_in_stock,
        'category': med.category
    })

@api_bp.route('/omnisearch')
@login_required
def omnisearch():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'results': []})

    results = []
    pattern = f"%{q}%"

    # Search Patients
    patients = Patient.query.filter(
        (Patient.first_name.ilike(pattern)) |
        (Patient.last_name.ilike(pattern)) |
        (Patient.patient_id.ilike(pattern)) |
        (Patient.phone.ilike(pattern))
    ).limit(4).all()
    for p in patients:
        results.append({
            'category': 'Patients',
            'title': f"{p.full_name} ({p.patient_id})",
            'subtitle': f"Phone: {p.phone} • Status: {p.status}",
            'url': f"/patients/{p.id}"
        })

    # Search Doctors
    doctors = Doctor.query.filter(
        (Doctor.name.ilike(pattern)) |
        (Doctor.specialization.ilike(pattern)) |
        (Doctor.doctor_code.ilike(pattern))
    ).limit(4).all()
    for d in doctors:
        results.append({
            'category': 'Doctors',
            'title': f"{d.name} ({d.specialization})",
            'subtitle': f"Dept: {d.department.name if d.department else 'N/A'} • {d.doctor_code}",
            'url': f"/doctors/{d.id}"
        })

    # Search Medicines
    medicines = Medicine.query.filter(
        (Medicine.name.ilike(pattern)) |
        (Medicine.generic_name.ilike(pattern)) |
        (Medicine.medicine_code.ilike(pattern))
    ).limit(4).all()
    for m in medicines:
        results.append({
            'category': 'Pharmacy',
            'title': f"{m.name} ({m.medicine_code})",
            'subtitle': f"Stock: {m.quantity_in_stock} • {m.generic_name}",
            'url': f"/pharmacy/?search={m.medicine_code}"
        })

    # Search Invoices
    invoices = Invoice.query.filter(
        Invoice.invoice_number.ilike(pattern)
    ).limit(3).all()
    for inv in invoices:
        results.append({
            'category': 'Billing',
            'title': f"Invoice {inv.invoice_number}",
            'subtitle': f"Patient: {inv.patient.full_name if inv.patient else ''} • Total: ₹{inv.grand_total:0.2f} ({inv.payment_status})",
            'url': f"/billing/{inv.id}"
        })

    return jsonify({'results': results})
