from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.pharmacy import Medicine, MedicineBatch, PharmacySale, PharmacySaleItem
from app.models.prescription import Prescription
from app.models.patient import Patient
from app.forms.pharmacy_forms import MedicineForm, StockAdjustmentForm
from app.utils.id_generator import generate_medicine_code, generate_pharmacy_sale_code
from app.utils.audit import log_audit
from app.utils.notifications import create_notification
from app.utils.decorators import roles_required
from app.utils.helpers import export_csv_response

pharmacy_bp = Blueprint('pharmacy', __name__, url_prefix='/pharmacy')

@pharmacy_bp.route('/')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Pharmacist', 'Doctor', 'Nurse')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    category = request.args.get('category', '', type=str)
    stock_filter = request.args.get('filter', '', type=str)

    query = Medicine.query
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Medicine.name.ilike(search_fmt)) |
            (Medicine.generic_name.ilike(search_fmt)) |
            (Medicine.medicine_code.ilike(search_fmt)) |
            (Medicine.batch_number.ilike(search_fmt))
        )
    if category:
        query = query.filter(Medicine.category == category)
    if stock_filter == 'low':
        query = query.filter(Medicine.quantity_in_stock <= Medicine.minimum_stock_alert)
    elif stock_filter == 'expired':
        query = query.filter(Medicine.expiry_date < date.today())
    elif stock_filter == 'out':
        query = query.filter(Medicine.quantity_in_stock == 0)

    medicines = query.order_by(Medicine.name.asc()).paginate(page=page, per_page=15, error_out=False)
    
    total_meds = Medicine.query.count()
    low_stock_count = Medicine.query.filter(Medicine.quantity_in_stock <= Medicine.minimum_stock_alert, Medicine.status == 'Active').count()
    expired_count = Medicine.query.filter(Medicine.expiry_date < date.today(), Medicine.status == 'Active').count()

    return render_template(
        'pharmacy/index.html',
        medicines=medicines,
        search=search,
        category=category,
        stock_filter=stock_filter,
        total_meds=total_meds,
        low_stock_count=low_stock_count,
        expired_count=expired_count
    )

@pharmacy_bp.route('/export-csv')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Pharmacist')
def export_csv():
    medicines = Medicine.query.order_by(Medicine.name.asc()).all()
    headers = ['Medicine Code', 'Brand Name', 'Generic Name', 'Category', 'Manufacturer', 'Batch #', 'Expiry Date', 'Cost (₹)', 'Price (₹)', 'In Stock', 'Min Alert']
    rows = []
    for m in medicines:
        rows.append([
            m.medicine_code,
            m.name,
            m.generic_name,
            m.category,
            m.manufacturer,
            m.batch_number,
            m.expiry_date.strftime('%Y-%m-%d') if m.expiry_date else '',
            f"{m.purchase_price:0.2f}",
            f"{m.selling_price:0.2f}",
            m.quantity_in_stock,
            m.minimum_stock_alert
        ])
    return export_csv_response('pharmacy_inventory_report', headers, rows)

@pharmacy_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Pharmacist')
def create():
    form = MedicineForm()
    if form.validate_on_submit():
        code = generate_medicine_code()
        med = Medicine(
            medicine_code=code,
            name=form.name.data.strip(),
            generic_name=form.generic_name.data.strip(),
            category=form.category.data,
            manufacturer=form.manufacturer.data.strip(),
            batch_number=form.batch_number.data.strip(),
            expiry_date=form.expiry_date.data,
            purchase_price=form.purchase_price.data,
            selling_price=form.selling_price.data,
            quantity_in_stock=form.quantity_in_stock.data,
            minimum_stock_alert=form.minimum_stock_alert.data,
            supplier_name=form.supplier_name.data.strip() if form.supplier_name.data else None,
            storage_conditions=form.storage_conditions.data.strip() if form.storage_conditions.data else None,
            side_effects=form.side_effects.data.strip() if form.side_effects.data else None,
            status=form.status.data
        )
        db.session.add(med)
        db.session.flush()

        # Create initial batch
        if form.quantity_in_stock.data > 0:
            batch = MedicineBatch(
                medicine_id=med.id,
                batch_number=med.batch_number,
                expiry_date=med.expiry_date,
                quantity=med.quantity_in_stock,
                purchase_price=med.purchase_price,
                selling_price=med.selling_price
            )
            db.session.add(batch)

        db.session.commit()
        log_audit('CREATE_MEDICINE', 'Pharmacy', f"Added medicine {med.name} ({med.medicine_code}) with {med.quantity_in_stock} stock.")
        flash(f"Medicine '{med.name}' ({med.medicine_code}) registered successfully.", 'success')
        return redirect(url_for('pharmacy.index'))

    return render_template('pharmacy/form.html', form=form, title='Add Pharmaceutical Medicine')

@pharmacy_bp.route('/<int:med_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Pharmacist')
def edit(med_id):
    med = Medicine.query.get_or_404(med_id)
    form = MedicineForm(obj=med)

    if form.validate_on_submit():
        med.name = form.name.data.strip()
        med.generic_name = form.generic_name.data.strip()
        med.category = form.category.data
        med.manufacturer = form.manufacturer.data.strip()
        med.batch_number = form.batch_number.data.strip()
        med.expiry_date = form.expiry_date.data
        med.purchase_price = form.purchase_price.data
        med.selling_price = form.selling_price.data
        med.quantity_in_stock = form.quantity_in_stock.data
        med.minimum_stock_alert = form.minimum_stock_alert.data
        med.supplier_name = form.supplier_name.data.strip() if form.supplier_name.data else None
        med.storage_conditions = form.storage_conditions.data.strip() if form.storage_conditions.data else None
        med.side_effects = form.side_effects.data.strip() if form.side_effects.data else None
        med.status = form.status.data

        db.session.commit()
        log_audit('UPDATE_MEDICINE', 'Pharmacy', f"Updated details for {med.name} ({med.medicine_code}).")
        flash(f"Medicine '{med.name}' updated successfully.", 'success')
        return redirect(url_for('pharmacy.index'))

    return render_template('pharmacy/form.html', form=form, title=f"Edit Medicine: {med.name}", med=med)

@pharmacy_bp.route('/<int:med_id>/adjust-stock', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Pharmacist')
def adjust_stock(med_id):
    med = Medicine.query.get_or_404(med_id)
    form = StockAdjustmentForm()

    if form.validate_on_submit():
        qty = form.quantity.data
        op = form.transaction_type.data

        if op == 'Stock In':
            med.quantity_in_stock += qty
            if form.batch_number.data:
                batch = MedicineBatch(
                    medicine_id=med.id,
                    batch_number=form.batch_number.data.strip(),
                    expiry_date=form.expiry_date.data or med.expiry_date,
                    quantity=qty,
                    purchase_price=form.unit_price.data or med.purchase_price,
                    selling_price=med.selling_price
                )
                db.session.add(batch)
        elif op in ['Stock Out', 'Damaged']:
            if qty > med.quantity_in_stock:
                flash(f"Cannot deduct {qty} units. Current stock is only {med.quantity_in_stock}.", 'danger')
                return render_template('pharmacy/stock_adjust.html', form=form, med=med)
            med.quantity_in_stock -= qty

        db.session.commit()

        # Check if stock dropped below alert threshold
        if med.is_low_stock:
            create_notification(
                title=f"Low Stock Alert: {med.name}",
                message=f"Stock for {med.name} ({med.medicine_code}) dropped to {med.quantity_in_stock} units (Threshold: {med.minimum_stock_alert}).",
                target_role='Pharmacist',
                notification_type='warning',
                link=url_for('pharmacy.index', filter='low')
            )

        log_audit('ADJUST_PHARMACY_STOCK', 'Pharmacy', f"{op} {qty} units for {med.name}. Note: {form.reference_note.data}")
        flash(f"Stock adjusted successfully! Current available stock: {med.quantity_in_stock} units.", 'success')
        return redirect(url_for('pharmacy.index'))

    return render_template('pharmacy/stock_adjust.html', form=form, med=med)

@pharmacy_bp.route('/dispense/<int:rx_id>', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Pharmacist')
def dispense_prescription(rx_id):
    rx = Prescription.query.get_or_404(rx_id)
    if request.method == 'POST':
        # Auto-decrement matching medicine stocks
        total_sale = 0.0
        sale_code = generate_pharmacy_sale_code()
        sale = PharmacySale(
            sale_code=sale_code,
            patient_id=rx.patient_id,
            prescription_id=rx.id,
            customer_name=rx.patient.full_name,
            payment_method=request.form.get('payment_method', 'Cash'),
            sold_by=current_user.full_name
        )
        db.session.add(sale)
        db.session.flush()

        for item in rx.items.all():
            if item.medicine_id:
                med = Medicine.query.get(item.medicine_id)
                if med and med.quantity_in_stock > 0:
                    med.quantity_in_stock = max(0, med.quantity_in_stock - 1)
                    item_price = med.selling_price
                    total_sale += item_price
                    sale_item = PharmacySaleItem(
                        sale_id=sale.id,
                        medicine_id=med.id,
                        quantity=1,
                        unit_price=item_price,
                        total_price=item_price
                    )
                    db.session.add(sale_item)
            item.is_dispensed = True

        sale.subtotal = total_sale
        sale.net_amount = total_sale
        rx.status = 'Dispensed'

        db.session.commit()
        log_audit('DISPENSE_PRESCRIPTION', 'Pharmacy', f"Dispensed Prescription {rx.prescription_id} for {rx.patient.full_name}.")
        flash(f"Prescription {rx.prescription_id} has been dispensed and stock updated successfully!", 'success')
        return redirect(url_for('prescriptions.index'))

    return render_template('pharmacy/dispense.html', rx=rx)
