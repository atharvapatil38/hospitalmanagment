from datetime import datetime
from app.extensions import db

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.String(30), unique=True, nullable=False, index=True) # APT-2026-0001
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='RESTRICT'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    appointment_time = db.Column(db.String(10), nullable=False) # e.g. "10:30"
    appointment_type = db.Column(db.String(30), default='General Consultation') # General Consultation, Follow-up, Emergency, Routine Checkup
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Scheduled', index=True) # Scheduled, Confirmed, Completed, Cancelled, No Show
    notes = db.Column(db.Text, nullable=True)
    cancellation_reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Link to medical record or prescription if generated
    medical_records = db.relationship('MedicalRecord', backref='appointment', lazy='dynamic')
    prescriptions = db.relationship('Prescription', backref='appointment', lazy='dynamic')

    def __repr__(self):
        return f"<Appointment {self.appointment_id} - Pat:{self.patient_id} Doc:{self.doctor_id} Date:{self.appointment_date}>"
