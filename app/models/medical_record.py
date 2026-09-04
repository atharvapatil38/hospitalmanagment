from datetime import datetime
from app.extensions import db

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.String(30), unique=True, nullable=False, index=True) # MED-2026-0001
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='RESTRICT'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id', ondelete='SET NULL'), nullable=True)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    symptoms = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    clinical_notes = db.Column(db.Text, nullable=True)
    treatment_plan = db.Column(db.Text, nullable=False)
    follow_up_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vitals = db.relationship('Vitals', backref='medical_record', cascade='all, delete-orphan', lazy='dynamic')
    prescriptions = db.relationship('Prescription', backref='medical_record', lazy='dynamic')

    def __repr__(self):
        return f"<MedicalRecord {self.record_id} - Pat:{self.patient_id} Doc:{self.doctor_id}>"

class Vitals(db.Model):
    __tablename__ = 'vitals'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id', ondelete='SET NULL'), nullable=True)
    recorded_by = db.Column(db.String(100), nullable=True) # Staff/Nurse/Doctor name
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Vital Sign Measurements
    temperature = db.Column(db.Float, nullable=True) # in °F (e.g. 98.6)
    bp_systolic = db.Column(db.Integer, nullable=True) # mmHg (e.g. 120)
    bp_diastolic = db.Column(db.Integer, nullable=True) # mmHg (e.g. 80)
    heart_rate = db.Column(db.Integer, nullable=True) # bpm (e.g. 72)
    respiratory_rate = db.Column(db.Integer, nullable=True) # breaths/min (e.g. 16)
    spo2 = db.Column(db.Float, nullable=True) # % (e.g. 98.0)
    weight_kg = db.Column(db.Float, nullable=True) # kg (e.g. 70.5)
    height_cm = db.Column(db.Float, nullable=True) # cm (e.g. 175)
    bmi = db.Column(db.Float, nullable=True) # kg/m^2
    notes = db.Column(db.String(255), nullable=True)

    @property
    def blood_pressure_str(self):
        if self.bp_systolic and self.bp_diastolic:
            return f"{self.bp_systolic}/{self.bp_diastolic} mmHg"
        return "N/A"

    def calculate_bmi(self):
        if self.weight_kg and self.height_cm and self.height_cm > 0:
            height_m = self.height_cm / 100.0
            self.bmi = round(self.weight_kg / (height_m * height_m), 1)
            return self.bmi
        return None

    def __repr__(self):
        return f"<Vitals Pat:{self.patient_id} at {self.recorded_at}>"
