from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class AppointmentForm(FlaskForm):
    patient_id = SelectField('Select Patient', coerce=int, validators=[DataRequired()])
    doctor_id = SelectField('Select Doctor', coerce=int, validators=[DataRequired()])
    department_id = SelectField('Select Department', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Appointment Date', validators=[DataRequired()])
    appointment_time = SelectField('Time Slot', choices=[
        ('09:00', '09:00 AM'),
        ('09:30', '09:30 AM'),
        ('10:00', '10:00 AM'),
        ('10:30', '10:30 AM'),
        ('11:00', '11:00 AM'),
        ('11:30', '11:30 AM'),
        ('12:00', '12:00 PM'),
        ('12:30', '12:30 PM'),
        ('14:00', '02:00 PM'),
        ('14:30', '02:30 PM'),
        ('15:00', '03:00 PM'),
        ('15:30', '03:30 PM'),
        ('16:00', '04:00 PM'),
        ('16:30', '04:30 PM'),
    ], validators=[DataRequired()])
    appointment_type = SelectField('Appointment Type', choices=[
        ('General Consultation', 'General Consultation'),
        ('Follow-up', 'Follow-up'),
        ('Emergency', 'Emergency Consultation'),
        ('Routine Checkup', 'Routine Checkup'),
        ('Second Opinion', 'Second Opinion')
    ], default='General Consultation')
    reason = TextAreaField('Reason for Visit / Chief Complaint', validators=[DataRequired(), Length(max=500)])
    notes = TextAreaField('Additional Notes', validators=[Optional()])

    submit = SubmitField('Book Appointment')

class AppointmentStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Scheduled', 'Scheduled'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No Show', 'No Show')
    ], validators=[DataRequired()])
    notes = TextAreaField('Staff Notes', validators=[Optional()])
    cancellation_reason = StringField('Cancellation Reason (if applicable)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Update Status')
