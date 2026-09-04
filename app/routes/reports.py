from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func
from app.extensions import db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.appointment import Appointment
from app.models.admission import Admission, Bed, Room
from app.models.billing import Invoice, Payment
from app.models.pharmacy import Medicine, PharmacySale
from app.models.laboratory import LabOrder
from app.utils.decorators import roles_required
from app.utils.helpers import export_csv_response

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Accountant', 'Doctor')
def index():
    report_type = request.args.get('type', 'revenue', type=str)
    start_date_str = request.args.get('start_date', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date_str = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

    data = {}

    if report_type == 'revenue':
        invoices = Invoice.query.filter(Invoice.invoice_date >= start_date, Invoice.invoice_date <= end_date).all()
        payments = Payment.query.filter(func.date(Payment.payment_date) >= start_date, func.date(Payment.payment_date) <= end_date).all()
        total_billed = sum(i.grand_total for i in invoices)
        total_collected = sum(p.amount for p in payments)
        total_outstanding = sum(i.balance_due for i in invoices)
        data = {
            'invoices': invoices,
            'payments': payments,
            'total_billed': total_billed,
            'total_collected': total_collected,
            'total_outstanding': total_outstanding
        }

    elif report_type == 'patients':
        patients = Patient.query.filter(func.date(Patient.registration_date) >= start_date, func.date(Patient.registration_date) <= end_date).all()
        male_count = sum(1 for p in patients if p.gender == 'Male')
        female_count = sum(1 for p in patients if p.gender == 'Female')
        data = {
            'patients': patients,
            'total': len(patients),
            'male_count': male_count,
            'female_count': female_count
        }

    elif report_type == 'appointments':
        appointments = Appointment.query.filter(Appointment.appointment_date >= start_date, Appointment.appointment_date <= end_date).all()
        completed = sum(1 for a in appointments if a.status == 'Completed')
        cancelled = sum(1 for a in appointments if a.status in ['Cancelled', 'No Show'])
        data = {
            'appointments': appointments,
            'total': len(appointments),
            'completed': completed,
            'cancelled': cancelled
        }

    elif report_type == 'admissions':
        admissions = Admission.query.filter(func.date(Admission.admission_date) >= start_date, func.date(Admission.admission_date) <= end_date).all()
        active_inpatients = sum(1 for a in admissions if a.status == 'Admitted')
        discharged = sum(1 for a in admissions if a.status == 'Discharged')
        data = {
            'admissions': admissions,
            'total': len(admissions),
            'active_inpatients': active_inpatients,
            'discharged': discharged
        }

    elif report_type == 'pharmacy':
        medicines = Medicine.query.all()
        low_stock = [m for m in medicines if m.is_low_stock]
        expired = [m for m in medicines if m.is_expired]
        sales = PharmacySale.query.filter(func.date(PharmacySale.sale_date) >= start_date, func.date(PharmacySale.sale_date) <= end_date).all()
        total_sales_amount = sum(s.net_amount for s in sales)
        data = {
            'medicines': medicines,
            'low_stock': low_stock,
            'expired': expired,
            'sales': sales,
            'total_sales_amount': total_sales_amount
        }

    elif report_type == 'laboratory':
        orders = LabOrder.query.filter(func.date(LabOrder.order_date) >= start_date, func.date(LabOrder.order_date) <= end_date).all()
        completed_orders = [o for o in orders if o.status == 'Completed']
        pending_orders = [o for o in orders if o.status != 'Completed']
        data = {
            'orders': orders,
            'total': len(orders),
            'completed_count': len(completed_orders),
            'pending_count': len(pending_orders)
        }

    return render_template(
        'reports/index.html',
        report_type=report_type,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        data=data
    )
