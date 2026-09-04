from datetime import datetime
import random
import string
from app.extensions import db

def _get_year():
    return datetime.utcnow().strftime('%Y')

def generate_patient_id():
    from app.models.patient import Patient
    year = _get_year()
    count = Patient.query.count() + 1
    # Check uniqueness
    while True:
        candidate = f"PAT-{year}-{count:04d}"
        if not Patient.query.filter_by(patient_id=candidate).first():
            return candidate
        count += 1

def generate_doctor_code():
    from app.models.doctor import Doctor
    count = Doctor.query.count() + 1
    while True:
        candidate = f"DOC-{count:03d}"
        if not Doctor.query.filter_by(doctor_code=candidate).first():
            return candidate
        count += 1

def generate_staff_code():
    from app.models.staff import Staff
    count = Staff.query.count() + 1
    while True:
        candidate = f"STF-{count:03d}"
        if not Staff.query.filter_by(staff_code=candidate).first():
            return candidate
        count += 1

def generate_appointment_id():
    from app.models.appointment import Appointment
    year = _get_year()
    count = Appointment.query.count() + 1
    while True:
        candidate = f"APT-{year}-{count:04d}"
        if not Appointment.query.filter_by(appointment_id=candidate).first():
            return candidate
        count += 1

def generate_admission_id():
    from app.models.admission import Admission
    year = _get_year()
    count = Admission.query.count() + 1
    while True:
        candidate = f"ADM-{year}-{count:04d}"
        if not Admission.query.filter_by(admission_id=candidate).first():
            return candidate
        count += 1

def generate_record_id():
    from app.models.medical_record import MedicalRecord
    year = _get_year()
    count = MedicalRecord.query.count() + 1
    while True:
        candidate = f"MED-{year}-{count:04d}"
        if not MedicalRecord.query.filter_by(record_id=candidate).first():
            return candidate
        count += 1

def generate_prescription_id():
    from app.models.prescription import Prescription
    year = _get_year()
    count = Prescription.query.count() + 1
    while True:
        candidate = f"RX-{year}-{count:04d}"
        if not Prescription.query.filter_by(prescription_id=candidate).first():
            return candidate
        count += 1

def generate_medicine_code():
    from app.models.pharmacy import Medicine
    count = Medicine.query.count() + 1
    while True:
        candidate = f"MED-{count:04d}"
        if not Medicine.query.filter_by(medicine_code=candidate).first():
            return candidate
        count += 1

def generate_pharmacy_sale_code():
    from app.models.pharmacy import PharmacySale
    year = _get_year()
    count = PharmacySale.query.count() + 1
    while True:
        candidate = f"PHR-{year}-{count:04d}"
        if not PharmacySale.query.filter_by(sale_code=candidate).first():
            return candidate
        count += 1

def generate_lab_test_code():
    from app.models.laboratory import LabTest
    count = LabTest.query.count() + 1
    while True:
        candidate = f"LAB-{count:03d}"
        if not LabTest.query.filter_by(test_code=candidate).first():
            return candidate
        count += 1

def generate_lab_order_id():
    from app.models.laboratory import LabOrder
    year = _get_year()
    count = LabOrder.query.count() + 1
    while True:
        candidate = f"LBO-{year}-{count:04d}"
        if not LabOrder.query.filter_by(order_id=candidate).first():
            return candidate
        count += 1

def generate_invoice_number():
    from app.models.billing import Invoice
    year = _get_year()
    count = Invoice.query.count() + 1
    while True:
        candidate = f"INV-{year}-{count:04d}"
        if not Invoice.query.filter_by(invoice_number=candidate).first():
            return candidate
        count += 1

def generate_payment_code():
    from app.models.billing import Payment
    year = _get_year()
    count = Payment.query.count() + 1
    while True:
        candidate = f"PAY-{year}-{count:04d}"
        if not Payment.query.filter_by(payment_code=candidate).first():
            return candidate
        count += 1

def generate_inventory_code():
    from app.models.inventory import InventoryItem
    count = InventoryItem.query.count() + 1
    while True:
        candidate = f"INV-ITM-{count:03d}"
        if not InventoryItem.query.filter_by(item_code=candidate).first():
            return candidate
        count += 1
