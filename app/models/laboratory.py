from datetime import datetime
from app.extensions import db

class LabTest(db.Model):
    __tablename__ = 'lab_tests'

    id = db.Column(db.Integer, primary_key=True)
    test_code = db.Column(db.String(30), unique=True, nullable=False, index=True) # LAB-001
    test_name = db.Column(db.String(120), nullable=False, index=True) # e.g. "Complete Blood Count (CBC)"
    category = db.Column(db.String(50), nullable=False) # Hematology, Biochemistry, Microbiology, Radiology, Pathology, Immunology, Urine Analysis
    price = db.Column(db.Float, nullable=False, default=0.0)
    normal_range = db.Column(db.String(150), nullable=True) # e.g. "4.5 - 11.0 x 10^3/uL"
    unit = db.Column(db.String(50), nullable=True) # e.g. "mg/dL", "g/dL", "U/L"
    description = db.Column(db.Text, nullable=True)
    turnaround_hours = db.Column(db.Integer, default=24)
    sample_type = db.Column(db.String(50), default='Blood') # Blood, Urine, Stool, Sputum, Swab, Tissue, X-Ray
    status = db.Column(db.String(20), default='Active') # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    orders = db.relationship('LabOrder', backref='lab_test', lazy='dynamic')

    def __repr__(self):
        return f"<LabTest {self.test_name} ({self.test_code})>"

class LabOrder(db.Model):
    __tablename__ = 'lab_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(30), unique=True, nullable=False, index=True) # LBO-2026-0001
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='RESTRICT'), nullable=False)
    lab_test_id = db.Column(db.Integer, db.ForeignKey('lab_tests.id', ondelete='RESTRICT'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    priority = db.Column(db.String(20), default='Normal') # Normal, Urgent, Emergency
    status = db.Column(db.String(30), default='Requested', index=True) # Requested, Sample Collected, Processing, Completed, Cancelled
    sample_collected_at = db.Column(db.DateTime, nullable=True)
    clinical_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 1-to-1 Relationship with LabResult
    result = db.relationship('LabResult', backref='lab_order', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<LabOrder {self.order_id} - Test:{self.lab_test_id} Status:{self.status}>"

class LabResult(db.Model):
    __tablename__ = 'lab_results'

    id = db.Column(db.Integer, primary_key=True)
    lab_order_id = db.Column(db.Integer, db.ForeignKey('lab_orders.id', ondelete='CASCADE'), unique=True, nullable=False)
    result_value = db.Column(db.Text, nullable=False) # e.g. "14.2" or narrative description
    reference_range = db.Column(db.String(150), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    status_flag = db.Column(db.String(20), default='Normal') # Normal, High, Low, Critical, Abnormal
    technician_name = db.Column(db.String(120), nullable=False)
    verified_by = db.Column(db.String(120), nullable=True) # Doctor/Pathologist name
    remarks = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LabResult Order:{self.lab_order_id} Val:{self.result_value} Flag:{self.status_flag}>"
