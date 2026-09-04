from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class MedicineForm(FlaskForm):
    name = StringField('Brand / Trade Name', validators=[DataRequired(), Length(max=120)])
    generic_name = StringField('Generic Formula / Composition', validators=[DataRequired(), Length(max=120)])
    category = SelectField('Dosage Form / Category', choices=[
        ('Tablet', 'Tablet'),
        ('Capsule', 'Capsule'),
        ('Syrup', 'Syrup / Suspension'),
        ('Injection', 'Injection / IV Ampoule'),
        ('Ointment', 'Ointment / Gel / Cream'),
        ('Drops', 'Eye / Ear Drops'),
        ('Inhaler', 'Inhaler / Respules'),
        ('IV Fluid', 'IV Infusion / Saline'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    manufacturer = StringField('Pharmaceutical Manufacturer', validators=[DataRequired(), Length(max=100)])
    batch_number = StringField('Batch / Lot Number', validators=[DataRequired(), Length(max=50)])
    expiry_date = DateField('Expiry Date', validators=[DataRequired()])
    purchase_price = FloatField('Purchase Cost (₹)', validators=[DataRequired(), NumberRange(min=0.0)])
    selling_price = FloatField('Retail / Selling Price (₹)', validators=[DataRequired(), NumberRange(min=0.0)])
    quantity_in_stock = IntegerField('Initial Stock Units', validators=[DataRequired(), NumberRange(min=0)])
    minimum_stock_alert = IntegerField('Low-Stock Threshold Alert', default=20, validators=[DataRequired(), NumberRange(min=1)])
    supplier_name = StringField('Supplier / Distributor', validators=[Optional(), Length(max=100)])
    storage_conditions = StringField('Storage Instructions', default='Store below 25°C in a dry place', validators=[Optional(), Length(max=100)])
    side_effects = TextAreaField('Side Effects & Warnings', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Active', 'Active'),
        ('Discontinued', 'Discontinued')
    ], default='Active')
    submit = SubmitField('Save Medicine')

class StockAdjustmentForm(FlaskForm):
    transaction_type = SelectField('Operation Type', choices=[
        ('Stock In', 'Stock In (Purchase / Restock)'),
        ('Stock Out', 'Stock Out (Adjustment / Scrap)'),
        ('Damaged', 'Damaged / Expired Removal')
    ], validators=[DataRequired()])
    quantity = IntegerField('Quantity (Units)', validators=[DataRequired(), NumberRange(min=1)])
    batch_number = StringField('Batch Number', validators=[Optional(), Length(max=50)])
    expiry_date = DateField('Batch Expiry Date (for Stock In)', validators=[Optional()])
    unit_price = FloatField('Unit Cost (₹)', validators=[Optional(), NumberRange(min=0.0)])
    reference_note = StringField('Reference Note / Supplier / Reason', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Update Stock')
