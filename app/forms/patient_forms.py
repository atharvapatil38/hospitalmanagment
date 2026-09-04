from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length

class PatientForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=60)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=60)])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[
        ('', '-- Select Blood Group --'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], validators=[Optional()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email Address', validators=[Optional(), Email(), Length(max=120)])
    address = TextAreaField('Residential Address', validators=[DataRequired()])
    city = StringField('City', validators=[Optional(), Length(max=60)])
    state = StringField('State / Province', validators=[Optional(), Length(max=60)])
    zip_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])

    # Emergency Contact
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional(), Length(max=100)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[Optional(), Length(max=20)])
    emergency_contact_relation = StringField('Relationship', validators=[Optional(), Length(max=50)])

    # Medical Info
    medical_history = TextAreaField('Medical & Surgical History', validators=[Optional()])
    allergies = TextAreaField('Known Allergies (Drugs, Food, etc.)', validators=[Optional()])
    existing_conditions = TextAreaField('Existing Chronic Conditions (Diabetes, HTN, etc.)', validators=[Optional()])
    department_id = SelectField('Preferred Department', coerce=int, validators=[Optional()])
    primary_doctor_id = SelectField('Primary Doctor', coerce=int, validators=[Optional()])
    status = SelectField('Patient Status', choices=[
        ('Active', 'Active'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
        ('Inactive', 'Inactive')
    ], default='Active')

    submit = SubmitField('Save Patient Record')
