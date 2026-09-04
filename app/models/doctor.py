from datetime import datetime
from app.extensions import db

class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    doctor_code = db.Column(db.String(30), unique=True, nullable=False, index=True) # e.g. DOC-2026-001
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False) # e.g. MBBS, MD (Cardiology)
    experience_years = db.Column(db.Integer, default=0)
    consultation_fee = db.Column(db.Float, default=50.0)
    availability_status = db.Column(db.String(20), default='Available') # Available, On Leave, Busy
    available_days = db.Column(db.String(100), default='Mon,Tue,Wed,Thu,Fri')
    available_time_start = db.Column(db.String(10), default='09:00')
    available_time_end = db.Column(db.String(10), default='17:00')
    bio = db.Column(db.Text, nullable=True)
    room_number = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='Active') # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User link
    user = db.relationship('User', backref=db.backref('doctor_profile', uselist=False))

    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic')
    admissions = db.relationship('Admission', backref='doctor', lazy='dynamic')
    medical_records = db.relationship('MedicalRecord', backref='doctor', lazy='dynamic')
    prescriptions = db.relationship('Prescription', backref='doctor', lazy='dynamic')
    lab_orders = db.relationship('LabOrder', backref='doctor', lazy='dynamic')
    schedules = db.relationship('DoctorSchedule', backref='doctor', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f"<Doctor {self.name} ({self.doctor_code})>"

class DoctorSchedule(db.Model):
    __tablename__ = 'doctor_schedules'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False) # Monday, Tuesday...
    start_time = db.Column(db.String(10), nullable=False) # e.g. 09:00
    end_time = db.Column(db.String(10), nullable=False) # e.g. 13:00
    max_patients = db.Column(db.Integer, default=20)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<DoctorSchedule {self.doctor_id} {self.day_of_week} {self.start_time}-{self.end_time}>"
