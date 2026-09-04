from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange

class StaffForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Hospital Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Contact Phone', validators=[DataRequired(), Length(max=20)])
    role_title = SelectField('Staff Designation / Role', choices=[
        ('Nurse', 'Registered Nurse (RN) / Nursing Staff'),
        ('Receptionist', 'Front Desk Receptionist / Admission Staff'),
        ('Pharmacist', 'Hospital Pharmacist / Dispenser'),
        ('Lab Technician', 'Medical Laboratory Technologist'),
        ('Accountant', 'Billing Officer / Accountant'),
        ('General Staff', 'Ward Attendant / Support Staff')
    ], validators=[DataRequired()])
    department_id = SelectField('Assigned Department', coerce=int, validators=[Optional()])
    joining_date = DateField('Joining Date', validators=[DataRequired()])
    salary = FloatField('Monthly Salary (₹)', default=30000.0, validators=[NumberRange(min=0.0)])
    status = SelectField('Employment Status', choices=[
        ('Active', 'Active Duty'),
        ('On Leave', 'On Authorized Leave'),
        ('Resigned', 'Resigned'),
        ('Terminated', 'Terminated')
    ], default='Active')
    qualification = StringField('Educational / Nursing Qualifications', validators=[Optional(), Length(max=100)])
    address = TextAreaField('Residential Address', validators=[Optional()])
    submit = SubmitField('Save Staff Member')
