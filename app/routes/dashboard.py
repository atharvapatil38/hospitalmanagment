from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.admission import Admission, Bed, Room
from app.models.laboratory import LabOrder
from app.models.billing import Invoice, Payment
from app.models.pharmacy import Medicine
from app.models.user import AuditLog, Notification
from app.utils.helpers import format_currency

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()

    # Base Metrics
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.filter_by(status='Active').count()
    available_doctors = Doctor.query.filter_by(status='Active', availability_status='Available').count()
    
    # Appointments
    today_appointments_count = Appointment.query.filter_by(appointment_date=today).count()
    pending_appointments_count = Appointment.query.filter_by(status='Scheduled').count()
    
    # Beds & Admissions
    total_beds = Bed.query.count()
    occupied_beds = Bed.query.filter_by(status='Occupied').count()
    available_beds = Bed.query.filter_by(status='Available').count()
    bed_occupancy_rate = round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0.0

    # Laboratory
    pending_lab_tests = LabOrder.query.filter(LabOrder.status.in_(['Requested', 'Sample Collected', 'Processing'])).count()

    # Revenue
    today_revenue_val = db_get_today_revenue(today)
    pending_invoices_amount = db_get_pending_revenue()

    # Pharmacy
    low_stock_count = Medicine.query.filter(Medicine.quantity_in_stock <= Medicine.minimum_stock_alert, Medicine.status == 'Active').count()
    expired_meds_count = Medicine.query.filter(Medicine.expiry_date < today, Medicine.status == 'Active').count()

    # Lists for Widgets
    recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    today_appointments = Appointment.query.filter_by(appointment_date=today).order_by(Appointment.appointment_time.asc()).limit(6).all()
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
    low_stock_medicines = Medicine.query.filter(Medicine.quantity_in_stock <= Medicine.minimum_stock_alert, Medicine.status == 'Active').limit(5).all()
    recent_audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(6).all()

    # Doctor-specific data if logged in as Doctor
    doctor_data = {}
    if current_user.role_name == 'Doctor':
        doc = Doctor.query.filter_by(email=current_user.email).first()
        if doc:
            doctor_data['doctor'] = doc
            doctor_data['my_today_appointments'] = Appointment.query.filter_by(doctor_id=doc.id, appointment_date=today).all()
            doctor_data['my_pending_appointments'] = Appointment.query.filter_by(doctor_id=doc.id, status='Scheduled').count()
            doctor_data['my_patients_count'] = Patient.query.filter_by(primary_doctor_id=doc.id).count()
            doctor_data['my_admitted_patients'] = Admission.query.filter_by(doctor_id=doc.id, status='Admitted').count()

    stats = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'available_doctors': available_doctors,
        'today_appointments': today_appointments_count,
        'pending_appointments': pending_appointments_count,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'bed_occupancy_rate': bed_occupancy_rate,
        'pending_lab_tests': pending_lab_tests,
        'today_revenue': format_currency(today_revenue_val),
        'today_revenue_raw': today_revenue_val,
        'pending_invoices_amount': format_currency(pending_invoices_amount),
        'low_stock_count': low_stock_count,
        'expired_meds_count': expired_meds_count
    }

    return render_template(
        'dashboard/index.html',
        stats=stats,
        recent_patients=recent_patients,
        today_appointments=today_appointments,
        recent_payments=recent_payments,
        low_stock_medicines=low_stock_medicines,
        recent_audit_logs=recent_audit_logs,
        doctor_data=doctor_data
    )

def db_get_today_revenue(today):
    from app.extensions import db
    try:
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        res = db.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_date >= today_start,
            Payment.payment_date <= today_end
        ).scalar()
        return float(res or 0.0)
    except Exception:
        return 0.0

def db_get_pending_revenue():
    from app.extensions import db
    try:
        res = db.session.query(func.sum(Invoice.balance_due)).filter(
            Invoice.payment_status.in_(['Unpaid', 'Partially Paid'])
        ).scalar()
        return float(res or 0.0)
    except Exception:
        return 0.0
