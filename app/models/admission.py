from datetime import datetime
from app.extensions import db

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False, index=True) # e.g. "101", "ICU-1"
    room_type = db.Column(db.String(50), nullable=False) # General Ward, Semi Private, Private, ICU, Emergency
    floor = db.Column(db.String(20), default='1st Floor')
    daily_charge = db.Column(db.Float, default=100.0)
    total_beds = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='Available') # Available, Full, Maintenance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    beds = db.relationship('Bed', backref='room', cascade='all, delete-orphan', lazy='dynamic')
    admissions = db.relationship('Admission', backref='room', lazy='dynamic')

    @property
    def available_beds_count(self):
        return self.beds.filter_by(status='Available').count()

    @property
    def occupied_beds_count(self):
        return self.beds.filter_by(status='Occupied').count()

    def __repr__(self):
        return f"<Room {self.room_number} ({self.room_type})>"

class Bed(db.Model):
    __tablename__ = 'beds'

    id = db.Column(db.Integer, primary_key=True)
    bed_number = db.Column(db.String(20), nullable=False) # e.g. "Bed A", "Bed 101-1"
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='Available', index=True) # Available, Occupied, Reserved, Maintenance
    current_admission_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    admissions = db.relationship('Admission', foreign_keys='Admission.bed_id', backref='bed', lazy='dynamic')

    def __repr__(self):
        return f"<Bed {self.bed_number} in Room {self.room_id} - {self.status}>"

class Admission(db.Model):
    __tablename__ = 'admissions'

    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.String(30), unique=True, nullable=False, index=True) # ADM-2026-0001
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='RESTRICT'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='RESTRICT'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='RESTRICT'), nullable=False)
    bed_id = db.Column(db.Integer, db.ForeignKey('beds.id', ondelete='RESTRICT'), nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    discharge_date = db.Column(db.DateTime, nullable=True)
    reason_for_admission = db.Column(db.Text, nullable=False)
    initial_diagnosis = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Admitted', index=True) # Admitted, Discharged, Transferred
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='admissions')
    discharge_summary = db.relationship('DischargeSummary', backref='admission', uselist=False, cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='admission', lazy='dynamic')

    @property
    def length_of_stay_days(self):
        end_time = self.discharge_date if self.discharge_date else datetime.utcnow()
        delta = end_time - self.admission_date
        return max(1, delta.days)

    def __repr__(self):
        return f"<Admission {self.admission_id} - Pat:{self.patient_id} Bed:{self.bed_id}>"

class DischargeSummary(db.Model):
    __tablename__ = 'discharge_summaries'

    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey('admissions.id', ondelete='CASCADE'), unique=True, nullable=False)
    discharge_date = db.Column(db.DateTime, default=datetime.utcnow)
    condition_at_discharge = db.Column(db.String(50), default='Recovered') # Recovered, Improved, Transferred, Referred, Deceased
    final_diagnosis = db.Column(db.Text, nullable=False)
    treatment_summary = db.Column(db.Text, nullable=False)
    discharge_medications = db.Column(db.Text, nullable=True)
    advice_instructions = db.Column(db.Text, nullable=True)
    follow_up_date = db.Column(db.Date, nullable=True)
    doctor_signature = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DischargeSummary for Admission {self.admission_id}>"
