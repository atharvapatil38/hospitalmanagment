from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.billing import Invoice, InvoiceItem, Payment
from app.models.patient import Patient
from app.models.admission import Admission
from app.forms.billing_forms import InvoiceForm, PaymentForm
from app.utils.id_generator import generate_invoice_number, generate_payment_code
from app.utils.audit import log_audit
from app.utils.decorators import roles_required
from app.utils.helpers import export_csv_response, get_hospital_setting

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

@billing_bp.route('/')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Accountant', 'Receptionist')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    status = request.args.get('status', '', type=str)
    b_type = request.args.get('type', '', type=str)

    query = Invoice.query
    if search:
        search_fmt = f"%{search}%"
        query = query.join(Patient).filter(
            (Invoice.invoice_number.ilike(search_fmt)) |
            (Patient.first_name.ilike(search_fmt)) |
            (Patient.last_name.ilike(search_fmt)) |
            (Patient.patient_id.ilike(search_fmt))
        )
    if status:
        query = query.filter(Invoice.payment_status == status)
    if b_type:
        query = query.filter(Invoice.billing_type == b_type)

    invoices = query.order_by(Invoice.invoice_date.desc()).paginate(page=page, per_page=15, error_out=False)
    
    total_billed = sum(i.grand_total for i in Invoice.query.all())
    total_collected = sum(i.paid_amount for i in Invoice.query.all())
    total_outstanding = sum(i.balance_due for i in Invoice.query.all())

    return render_template(
        'billing/index.html',
        invoices=invoices,
        search=search,
        status=status,
        b_type=b_type,
        total_billed=total_billed,
        total_collected=total_collected,
        total_outstanding=total_outstanding
    )

@billing_bp.route('/export-csv')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Accountant')
def export_csv():
    invoices = Invoice.query.order_by(Invoice.invoice_date.desc()).all()
    headers = ['Invoice #', 'Patient Name', 'Patient ID', 'Type', 'Date', 'Subtotal (₹)', 'Discount (₹)', 'Tax (₹)', 'Grand Total (₹)', 'Paid (₹)', 'Balance (₹)', 'Status']
    rows = []
    for inv in invoices:
        rows.append([
            inv.invoice_number,
            inv.patient.full_name if inv.patient else '',
            inv.patient.patient_id if inv.patient else '',
            inv.billing_type,
            inv.invoice_date.strftime('%Y-%m-%d'),
            f"{inv.subtotal:0.2f}",
            f"{inv.discount_amount:0.2f}",
            f"{inv.tax_amount:0.2f}",
            f"{inv.grand_total:0.2f}",
            f"{inv.paid_amount:0.2f}",
            f"{inv.balance_due:0.2f}",
            inv.payment_status
        ])
    return export_csv_response('hospital_invoices_report', headers, rows)

@billing_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Accountant', 'Receptionist')
def create():
    form = InvoiceForm()
    patients = Patient.query.order_by(Patient.first_name.asc()).all()
    form.patient_id.choices = [(p.id, f"{p.full_name} ({p.patient_id})") for p in patients]

    admissions = Admission.query.order_by(Admission.admission_date.desc()).all()
    form.admission_id.choices = [(0, '-- None / Outpatient --')] + [(a.id, f"{a.admission_id} - {a.patient.full_name} (Room {a.room.room_number})") for a in admissions]

    pre_patient = request.args.get('patient_id', type=int)
    if pre_patient and request.method == 'GET':
        form.patient_id.data = pre_patient

    pre_admission = request.args.get('admission_id', type=int)
    if pre_admission and request.method == 'GET':
        form.admission_id.data = pre_admission
        form.billing_type.data = 'Inpatient'

    if request.method == 'GET':
        default_tax = float(get_hospital_setting('default_tax_rate', '5.0') or 5.0)
        form.tax_rate.data = default_tax

    if form.validate_on_submit():
        item_types = request.form.getlist('item_type[]')
        item_names = request.form.getlist('item_name[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')

        if not item_names or len(item_names) == 0 or not item_names[0].strip():
            flash('Please include at least one billing line item.', 'danger')
            return render_template('billing/form.html', form=form, title='Generate Patient Invoice')

        inv_num = generate_invoice_number()
        invoice = Invoice(
            invoice_number=inv_num,
            patient_id=form.patient_id.data,
            admission_id=form.admission_id.data if (form.admission_id.data and form.admission_id.data > 0) else None,
            invoice_date=form.invoice_date.data,
            due_date=form.due_date.data,
            billing_type=form.billing_type.data,
            discount_type=form.discount_type.data,
            discount_value=form.discount_value.data or 0.0,
            tax_rate=form.tax_rate.data or 0.0,
            notes=form.notes.data.strip() if form.notes.data else None,
            created_by=current_user.full_name
        )
        db.session.add(invoice)
        db.session.flush()

        for i in range(len(item_names)):
            if item_names[i].strip():
                qty = int(quantities[i]) if (i < len(quantities) and quantities[i].isdigit()) else 1
                price = float(unit_prices[i]) if (i < len(unit_prices) and unit_prices[i]) else 0.0
                i_type = item_types[i] if i < len(item_types) else 'General'
                
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_type=i_type,
                    item_name=item_names[i].strip(),
                    quantity=qty,
                    unit_price=price,
                    total_price=round(qty * price, 2)
                )
                db.session.add(item)

        invoice.recalculate()
        db.session.commit()

        log_audit('CREATE_INVOICE', 'Billing', f"Generated invoice {invoice.invoice_number} for Patient ID {invoice.patient_id}. Total: ₹{invoice.grand_total}.")
        flash(f"Invoice '{invoice.invoice_number}' created successfully!", 'success')
        return redirect(url_for('billing.view_invoice', inv_id=invoice.id))

    return render_template('billing/form.html', form=form, title='Generate Patient Invoice')

@billing_bp.route('/<int:inv_id>')
@login_required
def view_invoice(inv_id):
    invoice = Invoice.query.get_or_404(inv_id)
    payment_form = PaymentForm()
    if request.method == 'GET':
        payment_form.amount.data = invoice.balance_due

    return render_template('billing/invoice_detail.html', invoice=invoice, payment_form=payment_form)

@billing_bp.route('/<int:inv_id>/print')
@login_required
def print_invoice(inv_id):
    invoice = Invoice.query.get_or_404(inv_id)
    return render_template('billing/print_invoice.html', invoice=invoice)

@billing_bp.route('/<int:inv_id>/payments', methods=['POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Accountant', 'Receptionist')
def record_payment(inv_id):
    invoice = Invoice.query.get_or_404(inv_id)
    form = PaymentForm()

    if form.validate_on_submit():
        pay_amount = form.amount.data
        if pay_amount <= 0:
            flash('Payment amount must be greater than zero.', 'danger')
            return redirect(url_for('billing.view_invoice', inv_id=invoice.id))

        if pay_amount > invoice.balance_due + 0.01:
            flash(f"Payment amount (₹{pay_amount:0.2f}) cannot exceed the outstanding balance (₹{invoice.balance_due:0.2f}).", 'danger')
            return redirect(url_for('billing.view_invoice', inv_id=invoice.id))

        pay_code = generate_payment_code()
        payment = Payment(
            payment_code=pay_code,
            invoice_id=invoice.id,
            patient_id=invoice.patient_id,
            payment_date=datetime.utcnow(),
            amount=pay_amount,
            payment_method=form.payment_method.data,
            transaction_reference=form.transaction_reference.data.strip() if form.transaction_reference.data else None,
            received_by=current_user.full_name,
            receipt_notes=form.receipt_notes.data.strip() if form.receipt_notes.data else None
        )
        db.session.add(payment)
        db.session.flush()

        invoice.recalculate()
        db.session.commit()

        log_audit('RECORD_PAYMENT', 'Billing', f"Recorded payment {payment.payment_code} of ₹{payment.amount} for Invoice {invoice.invoice_number} via {payment.payment_method}.")
        flash(f"Payment of ₹{payment.amount:0.2f} recorded successfully (Receipt #{payment.payment_code}).", 'success')
        return redirect(url_for('billing.view_invoice', inv_id=invoice.id))

    flash('Invalid payment information submitted.', 'danger')
    return redirect(url_for('billing.view_invoice', inv_id=invoice.id))

@billing_bp.route('/payments/<int:payment_id>/receipt')
@login_required
def print_receipt(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return render_template('billing/print_receipt.html', payment=payment)
