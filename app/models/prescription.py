from datetime import datetime
from app.extensions import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.String(30), unique=True, nullable=False, index=True) # RX-2026-0001
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='RESTRICT'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id', ondelete='SET NULL'), nullable=True)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id', ondelete='SET NULL'), nullable=True)
    prescription_date = db.Column(db.Date, default=datetime.utcnow().date, index=True)
    diagnosis = db.Column(db.String(255), nullable=False)
    general_advice = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active') # Active, Dispensed, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('PrescriptionItem', backref='prescription', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f"<Prescription {self.prescription_id} - Pat:{self.patient_id} Doc:{self.doctor_id}>"

class PrescriptionItem(db.Model):
    __tablename__ = 'prescription_items'

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id', ondelete='CASCADE'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id', ondelete='SET NULL'), nullable=True)
    medicine_name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(50), nullable=False) # e.g. "500 mg", "1 tablet", "10 ml"
    frequency = db.Column(db.String(50), nullable=False) # e.g. "Twice daily (1-0-1)", "Once daily at night"
    duration = db.Column(db.String(50), nullable=False) # e.g. "5 days", "2 weeks", "1 month"
    instructions = db.Column(db.String(200), default='After food') # Before food, After food, As needed
    is_dispensed = db.Column(db.Boolean, default=False)

    # Medicine link
    medicine = db.relationship('Medicine', backref='prescription_items')

    def __repr__(self):
        return f"<PrescriptionItem {self.medicine_name} ({self.dosage}) for Rx {self.prescription_id}>"
