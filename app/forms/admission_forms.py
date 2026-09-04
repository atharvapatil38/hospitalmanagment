from flask_wtf import FlaskForm
from wtforms import StringField, DateField, DateTimeField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from datetime import datetime

class AdmissionForm(FlaskForm):
    patient_id = SelectField('Select Patient', coerce=int, validators=[DataRequired()])
    doctor_id = SelectField('Attending Doctor', coerce=int, validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    room_id = SelectField('Room', coerce=int, validators=[DataRequired()])
    bed_id = SelectField('Bed', coerce=int, validators=[DataRequired()])
    reason_for_admission = TextAreaField('Reason for Inpatient Admission', validators=[DataRequired()])
    initial_diagnosis = TextAreaField('Initial Clinical Diagnosis', validators=[DataRequired()])
    submit = SubmitField('Admit Patient')

class DischargeForm(FlaskForm):
    condition_at_discharge = SelectField('Condition at Discharge', choices=[
        ('Recovered', 'Fully Recovered'),
        ('Improved', 'Improved / Stable'),
        ('Transferred', 'Transferred to Another Facility'),
        ('Referred', 'Referred to Higher Center'),
        ('Deceased', 'Deceased')
    ], default='Improved', validators=[DataRequired()])
    final_diagnosis = TextAreaField('Final Diagnosis', validators=[DataRequired()])
    treatment_summary = TextAreaField('Summary of Treatment & Procedures Given', validators=[DataRequired()])
    discharge_medications = TextAreaField('Discharge Medications & Dosages', validators=[Optional()])
    advice_instructions = TextAreaField('Post-Discharge Instructions & Diet Advice', validators=[Optional()])
    follow_up_date = DateField('Follow-up Review Date', validators=[Optional()])
    doctor_signature = StringField('Discharging Doctor Name / Signature', validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Confirm Discharge & Generate Summary')

class BedTransferForm(FlaskForm):
    new_room_id = SelectField('Target Room', coerce=int, validators=[DataRequired()])
    new_bed_id = SelectField('Target Available Bed', coerce=int, validators=[DataRequired()])
    transfer_reason = TextAreaField('Reason for Bed Transfer', validators=[DataRequired()])
    submit = SubmitField('Complete Bed Transfer')
