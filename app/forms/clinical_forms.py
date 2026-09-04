from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class MedicalRecordForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    doctor_id = SelectField('Consulting Doctor', coerce=int, validators=[DataRequired()])
    symptoms = TextAreaField('Presenting Symptoms / Chief Complaints', validators=[DataRequired()])
    diagnosis = TextAreaField('Clinical Diagnosis (ICD/Condition)', validators=[DataRequired()])
    clinical_notes = TextAreaField('Physical Examination & Clinical Notes', validators=[Optional()])
    treatment_plan = TextAreaField('Treatment Plan & Clinical Management', validators=[DataRequired()])
    follow_up_date = DateField('Follow-up Review Date', validators=[Optional()])
    submit = SubmitField('Save Clinical Record')

class VitalsForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    temperature = FloatField('Body Temperature (°F)', validators=[Optional(), NumberRange(min=85.0, max=115.0)])
    bp_systolic = IntegerField('Blood Pressure - Systolic (mmHg)', validators=[Optional(), NumberRange(min=50, max=260)])
    bp_diastolic = IntegerField('Blood Pressure - Diastolic (mmHg)', validators=[Optional(), NumberRange(min=30, max=160)])
    heart_rate = IntegerField('Heart Rate / Pulse (bpm)', validators=[Optional(), NumberRange(min=30, max=220)])
    respiratory_rate = IntegerField('Respiratory Rate (breaths/min)', validators=[Optional(), NumberRange(min=8, max=60)])
    spo2 = FloatField('Oxygen Saturation - SpO2 (%)', validators=[Optional(), NumberRange(min=50.0, max=100.0)])
    weight_kg = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=0.5, max=400.0)])
    height_cm = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=20.0, max=250.0)])
    notes = StringField('Nursing / Triage Notes', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Record Vitals')

class PrescriptionForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    doctor_id = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    diagnosis = StringField('Diagnosis / Indications', validators=[DataRequired(), Length(max=255)])
    general_advice = TextAreaField('General Advice, Dietary Restrictions, Lifestyle Suggestions', validators=[Optional()])
    submit = SubmitField('Create Prescription')
