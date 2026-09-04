import pytest
from datetime import date
from tests.conftest import login_user
from app.models import Patient
from app.extensions import db

def test_patient_registration_flow(client, init_db):
    login_user(client, 'reception@careplus.com', 'Reception@123')
    
    # Check registration form renders
    form_resp = client.get('/patients/new')
    assert form_resp.status_code == 200
    assert b"Register New Patient" in form_resp.data

    # Submit new patient registration
    resp = client.post('/patients/new', data={
        'first_name': 'Test',
        'last_name': 'Patient',
        'dob': '1990-05-15',
        'gender': 'Male',
        'blood_group': 'O+',
        'phone': '+1 (555) 999-1111',
        'email': 'test.patient@example.com',
        'address': '123 Test St',
        'city': 'New York',
        'state': 'NY',
        'zip_code': '10001',
        'emergency_contact_name': 'Jane Patient',
        'emergency_contact_phone': '+1 (555) 999-2222',
        'emergency_contact_relation': 'Spouse',
        'allergies': 'Penicillin',
        'existing_conditions': 'Hypertension',
        'medical_history': 'No prior surgeries'
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"created successfully" in resp.data

    # Verify patient in database
    pat = Patient.query.filter_by(email='test.patient@example.com').first()
    assert pat is not None
    assert pat.first_name == 'Test'
    assert pat.age > 0

def test_patient_search_and_filter(client, init_db):
    login_user(client, 'admin@careplus.com', 'Admin@123')
    
    # Create patient directly
    pat = Patient(
        patient_id='PAT-TEST-0001',
        first_name='Searchable',
        last_name='Subject',
        dob=date(1980, 1, 1),
        gender='Female',
        phone='+1 555-4321',
        status='Active'
    )
    db.session.add(pat)
    db.session.commit()

    resp = client.get('/patients/?search=Searchable')
    assert resp.status_code == 200
    assert b"Searchable Subject" in resp.data

def test_patient_profile_view(client, init_db):
    login_user(client, 'doctor@careplus.com', 'Doctor@123')
    pat = Patient(
        patient_id='PAT-TEST-0002',
        first_name='Profile',
        last_name='User',
        dob=date(1992, 3, 10),
        gender='Male',
        phone='+1 555-8888',
        status='Active'
    )
    db.session.add(pat)
    db.session.commit()

    resp = client.get(f'/patients/{pat.id}')
    assert resp.status_code == 200
    assert b"Profile User" in resp.data
    assert b"PAT-TEST-0002" in resp.data
