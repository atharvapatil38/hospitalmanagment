from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange

class HospitalSettingForm(FlaskForm):
    hospital_name = StringField('Hospital Official Name', validators=[DataRequired(), Length(max=150)])
    hospital_email = StringField('Hospital Contact Email', validators=[DataRequired(), Email(), Length(max=120)])
    hospital_phone = StringField('Hospital Helpline / Emergency Phone', validators=[DataRequired(), Length(max=30)])
    hospital_address = TextAreaField('Hospital Physical Address', validators=[DataRequired()])
    hospital_currency = StringField('Currency Symbol (e.g. ₹, $, €, £)', default='₹', validators=[DataRequired(), Length(max=10)])
    default_tax_rate = FloatField('Default Tax / VAT Rate (%)', default=5.0, validators=[NumberRange(min=0.0, max=100.0)])
    appointment_duration = IntegerField('Standard Appointment Slot Duration (Minutes)', default=30, validators=[NumberRange(min=5, max=120)])
    invoice_footer_note = TextAreaField('Invoice Footer Legal / Terms Note', validators=[Optional()])
    submit = SubmitField('Save System Settings')
