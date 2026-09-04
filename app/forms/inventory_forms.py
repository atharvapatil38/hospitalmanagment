from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class InventoryItemForm(FlaskForm):
    name = StringField('Hospital Supply / Equipment Name', validators=[DataRequired(), Length(max=120)])
    category = SelectField('Supply Category', choices=[
        ('Medical Equipment', 'Medical Equipment & Devices'),
        ('Surgical Supplies', 'Surgical Instruments & Sutures'),
        ('Consumables', 'General Medical Consumables (Syringes/Gauze/Gloves)'),
        ('Cleaning Supplies', 'Sanitation & Disinfection Supplies'),
        ('PPE', 'Personal Protective Equipment (PPE)'),
        ('Diagnostic Tools', 'Diagnostic Kits & Reagents'),
        ('Other', 'Other Hospital Logistics')
    ], validators=[DataRequired()])
    quantity = IntegerField('Current Quantity in Stock', validators=[DataRequired(), NumberRange(min=0)])
    unit = SelectField('Unit of Measure', choices=[
        ('Units', 'Units / Pieces'),
        ('Boxes', 'Boxes'),
        ('Packs', 'Packs'),
        ('Rolls', 'Rolls'),
        ('Bottles', 'Bottles / Gallons'),
        ('Pairs', 'Pairs'),
        ('Sets', 'Sets / Kits')
    ], default='Units')
    minimum_stock = IntegerField('Minimum Reorder Level Alert', default=10, validators=[DataRequired(), NumberRange(min=1)])
    location = StringField('Storage Location / Ward', default='Central Medical Supply Depot', validators=[DataRequired(), Length(max=100)])
    supplier_name = StringField('Vendor / Manufacturer', validators=[Optional(), Length(max=100)])
    unit_price = FloatField('Unit Acquisition Cost (₹)', default=0.0, validators=[NumberRange(min=0.0)])
    purchase_date = DateField('Purchase / Stock-In Date', validators=[Optional()])
    expiry_date = DateField('Shelf-life / Expiry Date (if applicable)', validators=[Optional()])
    description = TextAreaField('Item Specifications / Asset Details', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Active', 'Active & Available'),
        ('Low Stock', 'Low Stock Reorder'),
        ('Out of Stock', 'Out of Stock'),
        ('Maintenance', 'Under Maintenance / Sterilization')
    ], default='Active')
    submit = SubmitField('Save Inventory Item')

class InventoryTransactionForm(FlaskForm):
    transaction_type = SelectField('Stock Transaction', choices=[
        ('Stock In', 'Stock In (New Procurement / Restock)'),
        ('Stock Out', 'Stock Out (Issue to Ward / OT / Department)'),
        ('Adjustment', 'Stock Audit Adjustment'),
        ('Damaged/Disposed', 'Scrap / Expired / Damaged Disposal')
    ], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    unit_price = FloatField('Unit Price (₹)', default=0.0, validators=[Optional(), NumberRange(min=0.0)])
    reference_note = StringField('Department Issued To / PO # / Reason', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Record Transaction')
