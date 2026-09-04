from datetime import datetime
from app.extensions import db

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    head_doctor_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    doctors = db.relationship('Doctor', backref='department', lazy='dynamic')
    staff = db.relationship('Staff', backref='department', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='department', lazy='dynamic')
    patients = db.relationship('Patient', backref='department', lazy='dynamic')

    def __repr__(self):
        return f"<Department {self.name} ({self.code})>"
