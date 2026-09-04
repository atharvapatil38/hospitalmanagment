from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.inventory import InventoryItem, InventoryTransaction
from app.forms.inventory_forms import InventoryItemForm, InventoryTransactionForm
from app.utils.id_generator import generate_inventory_code
from app.utils.audit import log_audit
from app.utils.notifications import create_notification
from app.utils.decorators import roles_required
from app.utils.helpers import export_csv_response

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Pharmacist', 'Nurse')
def index():
    category = request.args.get('category', '', type=str)
    search = request.args.get('search', '', type=str).strip()
    status = request.args.get('status', '', type=str)

    query = InventoryItem.query
    if category:
        query = query.filter(InventoryItem.category == category)
    if status == 'low':
        query = query.filter(InventoryItem.quantity <= InventoryItem.minimum_stock)
    elif status:
        query = query.filter(InventoryItem.status == status)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (InventoryItem.name.ilike(search_fmt)) |
            (InventoryItem.item_code.ilike(search_fmt)) |
            (InventoryItem.location.ilike(search_fmt))
        )

    items = query.order_by(InventoryItem.name.asc()).all()
    total_items = InventoryItem.query.count()
    low_stock_items = InventoryItem.query.filter(InventoryItem.quantity <= InventoryItem.minimum_stock).count()

    return render_template('inventory/index.html', items=items, category=category, search=search, status=status, total_items=total_items, low_stock_items=low_stock_items)

@inventory_bp.route('/export-csv')
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def export_csv():
    items = InventoryItem.query.order_by(InventoryItem.name.asc()).all()
    headers = ['Item Code', 'Item Name', 'Category', 'Stock Qty', 'Unit', 'Min Stock', 'Location', 'Unit Price (₹)', 'Status']
    rows = []
    for item in items:
        rows.append([
            item.item_code,
            item.name,
            item.category,
            item.quantity,
            item.unit,
            item.minimum_stock,
            item.location,
            f"{item.unit_price:0.2f}",
            item.status
        ])
    return export_csv_response('hospital_inventory_supplies', headers, rows)

@inventory_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def create():
    form = InventoryItemForm()
    if form.validate_on_submit():
        code = generate_inventory_code()
        item = InventoryItem(
            item_code=code,
            name=form.name.data.strip(),
            category=form.category.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            minimum_stock=form.minimum_stock.data,
            location=form.location.data.strip(),
            supplier_name=form.supplier_name.data.strip() if form.supplier_name.data else None,
            unit_price=form.unit_price.data or 0.0,
            purchase_date=form.purchase_date.data,
            expiry_date=form.expiry_date.data,
            description=form.description.data.strip() if form.description.data else None,
            status=form.status.data
        )
        db.session.add(item)
        db.session.flush()

        if item.quantity > 0:
            txn = InventoryTransaction(
                item_id=item.id,
                transaction_type='Stock In',
                quantity=item.quantity,
                unit_price=item.unit_price,
                reference_note='Initial Stock Intake',
                performed_by=current_user.full_name
            )
            db.session.add(txn)

        db.session.commit()
        log_audit('CREATE_INVENTORY_ITEM', 'Inventory', f"Added supply item {item.name} ({item.item_code}) with {item.quantity} {item.unit}.")
        flash(f"Supply item '{item.name}' added successfully.", 'success')
        return redirect(url_for('inventory.index'))

    return render_template('inventory/form.html', form=form, title='Add Hospital Supply / Inventory Item')

@inventory_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def edit(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    form = InventoryItemForm(obj=item)

    if form.validate_on_submit():
        item.name = form.name.data.strip()
        item.category = form.category.data
        item.quantity = form.quantity.data
        item.unit = form.unit.data
        item.minimum_stock = form.minimum_stock.data
        item.location = form.location.data.strip()
        item.supplier_name = form.supplier_name.data.strip() if form.supplier_name.data else None
        item.unit_price = form.unit_price.data or 0.0
        item.purchase_date = form.purchase_date.data
        item.expiry_date = form.expiry_date.data
        item.description = form.description.data.strip() if form.description.data else None
        item.status = form.status.data

        db.session.commit()
        log_audit('UPDATE_INVENTORY_ITEM', 'Inventory', f"Updated supply item {item.name} ({item.item_code}).")
        flash(f"Supply item '{item.name}' updated successfully.", 'success')
        return redirect(url_for('inventory.index'))

    return render_template('inventory/form.html', form=form, title=f"Edit Supply Item: {item.name}", item=item)

@inventory_bp.route('/<int:item_id>/adjust', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def adjust_stock(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    form = InventoryTransactionForm()

    if form.validate_on_submit():
        op = form.transaction_type.data
        qty = form.quantity.data

        if op == 'Stock In':
            item.quantity += qty
        elif op in ['Stock Out', 'Damaged/Disposed']:
            if qty > item.quantity:
                flash(f"Cannot issue {qty} {item.unit}. Available stock is {item.quantity} {item.unit}.", 'danger')
                return render_template('inventory/adjust.html', form=form, item=item)
            item.quantity -= qty

        txn = InventoryTransaction(
            item_id=item.id,
            transaction_type=op,
            quantity=qty,
            unit_price=form.unit_price.data or item.unit_price,
            reference_note=form.reference_note.data.strip(),
            performed_by=current_user.full_name
        )
        db.session.add(txn)
        db.session.commit()

        if item.is_low_stock:
            create_notification(
                title=f"Supply Low Stock: {item.name}",
                message=f"Current stock of {item.name} is {item.quantity} {item.unit} (Alert threshold: {item.minimum_stock}).",
                target_role='Hospital Admin',
                notification_type='warning',
                link=url_for('inventory.index', status='low')
            )

        log_audit('ADJUST_INVENTORY_STOCK', 'Inventory', f"{op} {qty} {item.unit} for {item.name}. Note: {form.reference_note.data}")
        flash(f"Stock transaction logged. Updated stock: {item.quantity} {item.unit}.", 'success')
        return redirect(url_for('inventory.index'))

    return render_template('inventory/adjust.html', form=form, item=item)
