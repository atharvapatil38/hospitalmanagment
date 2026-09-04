from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class InvoiceForm(FlaskForm):
    patient_id = SelectField('Bill To Patient', coerce=int, validators=[DataRequired()])
    admission_id = SelectField('Linked Inpatient Admission (Optional)', coerce=int, validators=[Optional()])
    invoice_date = DateField('Invoice Date', validators=[DataRequired()])
    due_date = DateField('Payment Due Date', validators=[Optional()])
    billing_type = SelectField('Billing Category', choices=[
        ('Outpatient', 'Outpatient Consultation & Services (OPD)'),
        ('Inpatient', 'Inpatient Hospitalization & Room (IPD)'),
        ('Pharmacy', 'Pharmacy & Medication Dispensing'),
        ('Laboratory', 'Diagnostic & Laboratory Investigations'),
        ('Emergency', 'Emergency Room Services'),
        ('General', 'General Hospital Services')
    ], default='Outpatient', validators=[DataRequired()])
    discount_type = SelectField('Discount Type', choices=[
        ('Fixed', 'Flat Amount Discount (₹)'),
        ('Percentage', 'Percentage Discount (%)')
    ], default='Fixed')
    discount_value = FloatField('Discount Value', default=0.0, validators=[NumberRange(min=0.0)])
    tax_rate = FloatField('Tax Rate (%)', default=5.0, validators=[NumberRange(min=0.0, max=100.0)])
    notes = TextAreaField('Invoice Remarks / Payment Terms', validators=[Optional()])
    submit = SubmitField('Generate Invoice')

class PaymentForm(FlaskForm):
    amount = FloatField('Payment Amount (₹)', validators=[DataRequired(), NumberRange(min=0.01)])
    payment_method = SelectField('Payment Method', choices=[
        ('Cash', 'Cash Settlement'),
        ('Card', 'Debit / Credit Card (POS)'),
        ('UPI', 'UPI / QR Code Transfer'),
        ('Bank Transfer', 'Direct Bank / Wire Transfer (NEFT/RTGS/ACH)'),
        ('Insurance', 'Insurance Third-Party (TPA) Settlement'),
        ('Cheque', 'Bank Demand Draft / Cheque')
    ], default='Cash', validators=[DataRequired()])
    transaction_reference = StringField('Transaction / Auth Ref # / Cheque #', validators=[Optional(), Length(max=100)])
    receipt_notes = TextAreaField('Receipt Remarks / Payer Details', validators=[Optional()])
    submit = SubmitField('Record & Print Payment Receipt')
