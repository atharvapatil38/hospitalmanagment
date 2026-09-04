from datetime import datetime
from app.extensions import db

class Staff(db.Model):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)
    staff_code = db.Column(db.String(30), unique=True, nullable=False, index=True) # STF-2026-001
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role_title = db.Column(db.String(50), nullable=False) # Nurse, Receptionist, Pharmacist, Lab Technician, Accountant, General Staff
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    joining_date = db.Column(db.Date, nullable=False)
    salary = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Active') # Active, On Leave, Resigned, Terminated
    address = db.Column(db.Text, nullable=True)
    qualification = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User link
    user = db.relationship('User', backref=db.backref('staff_profile', uselist=False))

    def __repr__(self):
        return f"<Staff {self.name} ({self.role_title})>"
