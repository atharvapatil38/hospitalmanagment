import pytest
from datetime import date
from tests.conftest import login_user
from app.models import Patient, Doctor, Prescription, PrescriptionItem
from app.extensions import db

def test_create_prescription_multi_item(client, init_db):
    login_user(client, 'doctor@careplus.com', 'Doctor@123')
    
    pat = Patient(patient_id='PAT-TEST-RX1', first_name='Rx', last_name='Patient', dob=date(1991, 2, 2), gender='Male', phone='+1 555-5555')
    db.session.add(pat)
    db.session.commit()

    doc = Doctor.query.first()

    resp = client.post('/prescriptions/new', data={
        'patient_id': pat.id,
        'doctor_id': doc.id,
        'diagnosis': 'Acute Bacterial Sinusitis',
        'general_advice': 'Take full course of antibiotics and hydrate.',
        'med_name[]': ['Amoxicillin 500mg', 'Paracetamol 500mg'],
        'med_id[]': ['0', '0'],
        'dosage[]': ['500 mg', '500 mg'],
        'frequency[]': ['Twice daily', 'Thrice daily'],
        'duration[]': ['7 days', '3 days'],
        'instructions[]': ['After meals', 'As needed for pain']
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"generated successfully" in resp.data

    rx = Prescription.query.filter_by(patient_id=pat.id).first()
    assert rx is not None
    assert rx.items.count() == 2
    assert rx.diagnosis == 'Acute Bacterial Sinusitis'

def test_print_prescription_view(client, init_db):
    login_user(client, 'doctor@careplus.com', 'Doctor@123')
    
    pat = Patient(patient_id='PAT-TEST-RX2', first_name='Print', last_name='Rx', dob=date(1988, 8, 8), gender='Female', phone='+1 555-6666')
    db.session.add(pat)
    db.session.commit()

    doc = Doctor.query.first()
    rx = Prescription(
        prescription_id='RX-TEST-0001',
        patient_id=pat.id,
        doctor_id=doc.id,
        diagnosis='Migraine Headache'
    )
    db.session.add(rx)
    db.session.flush()

    item = PrescriptionItem(
        prescription_id=rx.id,
        medicine_name='Sumatriptan 50mg',
        dosage='50 mg',
        frequency='SOS',
        duration='3 days'
    )
    db.session.add(item)
    db.session.commit()

    resp = client.get(f'/prescriptions/{rx.id}/print')
    assert resp.status_code == 200
    assert b"Medical Prescription Slip" in resp.data
    assert b"Sumatriptan 50mg" in resp.data
