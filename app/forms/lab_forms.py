from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class LabTestForm(FlaskForm):
    test_name = StringField('Investigation / Test Name', validators=[DataRequired(), Length(max=120)])
    category = SelectField('Laboratory Department', choices=[
        ('Hematology', 'Hematology'),
        ('Biochemistry', 'Biochemistry & Clinical Pathology'),
        ('Microbiology', 'Microbiology & Serology'),
        ('Radiology', 'Radiology & Imaging (X-Ray/CT/USG)'),
        ('Pathology', 'Histopathology & Cytology'),
        ('Immunology', 'Immunology & Hormones'),
        ('Urine Analysis', 'Clinical Microscopy & Urinalysis')
    ], validators=[DataRequired()])
    price = FloatField('Standard Test Fee (₹)', validators=[DataRequired(), NumberRange(min=0.0)])
    normal_range = StringField('Normal Reference Range', validators=[Optional(), Length(max=150)])
    unit = StringField('Unit of Measurement (e.g. mg/dL, g/dL, %)', validators=[Optional(), Length(max=50)])
    sample_type = SelectField('Sample Specimen Required', choices=[
        ('Blood', 'Blood (Serum / Plasma / Whole)'),
        ('Urine', 'Urine (Random / 24-hr)'),
        ('Stool', 'Stool / Fecal'),
        ('Sputum', 'Sputum'),
        ('Swab', 'Nasopharyngeal / Throat Swab'),
        ('Tissue', 'Biopsy / Tissue Specimen'),
        ('Fluid', 'CSF / Pleural / Ascitic Fluid'),
        ('X-Ray', 'Radiographic Film / Image'),
        ('None', 'Non-invasive / Physical Scan')
    ], default='Blood')
    turnaround_hours = IntegerField('Estimated Turnaround Time (Hours)', default=24, validators=[NumberRange(min=1)])
    description = TextAreaField('Test Methodology & Clinical Utility', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    ], default='Active')
    submit = SubmitField('Save Lab Test')

class LabOrderForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    doctor_id = SelectField('Ordering Doctor', coerce=int, validators=[DataRequired()])
    lab_test_id = SelectField('Lab Test to Order', coerce=int, validators=[DataRequired()])
    priority = SelectField('Order Priority', choices=[
        ('Normal', 'Routine / Normal (24-48 hrs)'),
        ('Urgent', 'Urgent (Within 4-6 hrs)'),
        ('Emergency', 'STAT / Emergency (Within 1 hr)')
    ], default='Normal')
    clinical_notes = TextAreaField('Clinical Indication / Suspected Condition', validators=[Optional()])
    submit = SubmitField('Submit Lab Investigation Request')

class LabResultForm(FlaskForm):
    result_value = TextAreaField('Result Value / Findings', validators=[DataRequired()])
    reference_range = StringField('Reference Range', validators=[Optional(), Length(max=150)])
    unit = StringField('Measurement Unit', validators=[Optional(), Length(max=50)])
    status_flag = SelectField('Clinical Flag', choices=[
        ('Normal', 'Normal Range'),
        ('High', 'Above Normal (High)'),
        ('Low', 'Below Normal (Low)'),
        ('Critical', 'Panic / Critical Value (Notify Doctor Immediately)'),
        ('Abnormal', 'Abnormal Finding / Inconclusive')
    ], default='Normal')
    technician_name = StringField('Testing Medical Technologist', validators=[DataRequired(), Length(max=120)])
    verified_by = StringField('Pathologist / Verifying Consultant', validators=[Optional(), Length(max=120)])
    remarks = TextAreaField('Technologist Remarks & Observations', validators=[Optional()])
    submit = SubmitField('Publish Verified Lab Result')
