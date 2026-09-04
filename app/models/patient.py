from datetime import datetime
from app.extensions import db

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(30), unique=True, nullable=False, index=True) # PAT-2026-0001
    first_name = db.Column(db.String(60), nullable=False, index=True)
    last_name = db.Column(db.String(60), nullable=False, index=True)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(15), nullable=False) # Male, Female, Other
    blood_group = db.Column(db.String(10), nullable=True) # A+, A-, B+, B-, AB+, AB-, O+, O-
    phone = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(60), nullable=True)
    state = db.Column(db.String(60), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)

    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    emergency_contact_relation = db.Column(db.String(50), nullable=True)

    # Clinical Info
    medical_history = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    existing_conditions = db.Column(db.Text, nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    primary_doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)

    status = db.Column(db.String(20), default='Active', index=True) # Active, Admitted, Discharged, Inactive
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    primary_doctor = db.relationship('Doctor', foreign_keys=[primary_doctor_id], backref='assigned_patients')
    appointments = db.relationship('Appointment', backref='patient', cascade='all, delete-orphan', lazy='dynamic')
    admissions = db.relationship('Admission', backref='patient', cascade='all, delete-orphan', lazy='dynamic')
    medical_records = db.relationship('MedicalRecord', backref='patient', cascade='all, delete-orphan', lazy='dynamic')
    vitals_records = db.relationship('Vitals', backref='patient', cascade='all, delete-orphan', lazy='dynamic')
    prescriptions = db.relationship('Prescription', backref='patient', cascade='all, delete-orphan', lazy='dynamic')
    lab_orders = db.relationship('LabOrder', backref='patient', cascade='all, delete-orphan', lazy='dynamic')
    invoices = db.relationship('Invoice', backref='patient', cascade='all, delete-orphan', lazy='dynamic')
    payments = db.relationship('Payment', backref='patient', cascade='all, delete-orphan', lazy='dynamic')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        if self.dob:
            today = datetime.utcnow().date()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None

    def __repr__(self):
        return f"<Patient {self.full_name} ({self.patient_id})>"
