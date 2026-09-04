from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.patients import patients_bp
from app.routes.doctors import doctors_bp
from app.routes.departments import departments_bp
from app.routes.appointments import appointments_bp
from app.routes.admissions import admissions_bp
from app.routes.rooms_beds import rooms_beds_bp
from app.routes.medical_records import medical_records_bp
from app.routes.prescriptions import prescriptions_bp
from app.routes.pharmacy import pharmacy_bp
from app.routes.laboratory import laboratory_bp
from app.routes.billing import billing_bp
from app.routes.inventory import inventory_bp
from app.routes.staff import staff_bp
from app.routes.reports import reports_bp
from app.routes.notifications import notifications_bp
from app.routes.settings import settings_bp
from app.routes.audit import audit_bp
from app.routes.api import api_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'patients_bp',
    'doctors_bp',
    'departments_bp',
    'appointments_bp',
    'admissions_bp',
    'rooms_beds_bp',
    'medical_records_bp',
    'prescriptions_bp',
    'pharmacy_bp',
    'laboratory_bp',
    'billing_bp',
    'inventory_bp',
    'staff_bp',
    'reports_bp',
    'notifications_bp',
    'settings_bp',
    'audit_bp',
    'api_bp',
]
