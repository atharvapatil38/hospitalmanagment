from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='role_ref', lazy='dynamic')

    def __repr__(self):
        return f"<Role {self.name}>"

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role_name(self):
        return self.role_ref.name if self.role_ref else 'User'

    def has_role(self, *role_names):
        return self.role_name in role_names

    def is_super_admin(self):
        return self.role_name == 'Super Admin'

    def is_hospital_admin(self):
        return self.role_name in ['Super Admin', 'Hospital Admin']

    def is_doctor(self):
        return self.role_name == 'Doctor'

    def is_nurse(self):
        return self.role_name == 'Nurse'

    def is_receptionist(self):
        return self.role_name == 'Receptionist'

    def is_pharmacist(self):
        return self.role_name == 'Pharmacist'

    def is_lab_technician(self):
        return self.role_name == 'Lab Technician'

    def is_accountant(self):
        return self.role_name == 'Accountant'

    def __repr__(self):
        return f"<User {self.username} ({self.role_name})>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False, index=True) # e.g., 'CREATE', 'UPDATE', 'DELETE', 'LOGIN'
    module = db.Column(db.String(50), nullable=False, index=True)  # e.g., 'Patient', 'Billing', 'Pharmacy'
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.module} by User {self.user_id}>"

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    target_role = db.Column(db.String(50), nullable=True) # If null, specific to user_id; if set, for entire role
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    notification_type = db.Column(db.String(20), default='info') # info, warning, success, danger
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Notification {self.title}>"

class HospitalSetting(db.Model):
    __tablename__ = 'hospital_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_setting(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set_setting(cls, key, value, description=None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            if description:
                setting.description = description
        else:
            setting = cls(key=key, value=str(value), description=description)
            db.session.add(setting)
        db.session.commit()
        return setting
