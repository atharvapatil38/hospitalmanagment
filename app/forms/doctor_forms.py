from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class DoctorForm(FlaskForm):
    name = StringField('Full Name (e.g. Dr. John Doe)', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    specialization = StringField('Specialization', validators=[DataRequired(), Length(max=100)])
    qualification = StringField('Medical Qualifications (MBBS, MD, MS, FRCS)', validators=[DataRequired(), Length(max=100)])
    experience_years = IntegerField('Years of Experience', default=5, validators=[NumberRange(min=0, max=60)])
    consultation_fee = FloatField('Consultation Fee (₹)', default=500.0, validators=[NumberRange(min=0.0)])
    availability_status = SelectField('Availability Status', choices=[
        ('Available', 'Available'),
        ('On Leave', 'On Leave'),
        ('Busy', 'Busy')
    ], default='Available')
    available_days = StringField('Available Days (e.g. Mon,Tue,Wed,Thu,Fri)', default='Mon,Tue,Wed,Thu,Fri', validators=[DataRequired()])
    available_time_start = StringField('Shift Start Time (HH:MM)', default='09:00', validators=[DataRequired()])
    available_time_end = StringField('Shift End Time (HH:MM)', default='17:00', validators=[DataRequired()])
    room_number = StringField('Consultation Room Number', validators=[Optional(), Length(max=20)])
    bio = TextAreaField('Doctor Biography / Profile Summary', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    ], default='Active')

    submit = SubmitField('Save Doctor')
