import pytest
from datetime import date, timedelta
from tests.conftest import login_user
from app.models import Patient, Doctor, Department, Appointment
from app.extensions import db

def test_appointment_booking_and_conflict_check(client, init_db):
    login_user(client, 'reception@careplus.com', 'Reception@123')
    
    pat = Patient(
        patient_id='PAT-TEST-APT1',
        first_name='Apt',
        last_name='Patient',
        dob=date(1995, 1, 1),
        gender='Male',
        phone='+1 555-1111'
    )
    db.session.add(pat)
    db.session.commit()

    doc = Doctor.query.first()
    dept = Department.query.first()
    apt_date = (date.today() + timedelta(days=2)).isoformat()

    # 1. Book first appointment
    resp1 = client.post('/appointments/book', data={
        'patient_id': pat.id,
        'doctor_id': doc.id,
        'department_id': dept.id,
        'appointment_date': apt_date,
        'appointment_time': '10:00',
        'appointment_type': 'General Consultation',
        'reason': 'Chest pain consultation'
    }, follow_redirects=True)

    assert resp1.status_code == 200
    assert b"Appointment booked successfully" in resp1.data

    # 2. Try to double-book the same doctor at the same date and time
    resp2 = client.post('/appointments/book', data={
        'patient_id': pat.id,
        'doctor_id': doc.id,
        'department_id': dept.id,
        'appointment_date': apt_date,
        'appointment_time': '10:00',
        'appointment_type': 'Follow-up',
        'reason': 'Double booking test'
    }, follow_redirects=True)

    assert resp2.status_code == 200
    assert b"Scheduling Conflict" in resp2.data

def test_appointment_status_update(client, init_db):
    login_user(client, 'doctor@careplus.com', 'Doctor@123')
    
    pat = Patient(patient_id='PAT-TEST-APT2', first_name='Status', last_name='Test', dob=date(1990, 1, 1), gender='Female', phone='+1 555-2222')
    db.session.add(pat)
    db.session.commit()

    doc = Doctor.query.first()
    apt = Appointment(
        appointment_id='APT-TEST-0001',
        patient_id=pat.id,
        doctor_id=doc.id,
        department_id=doc.department_id,
        appointment_date=date.today(),
        appointment_time='11:00',
        reason='Routine checkup',
        status='Scheduled'
    )
    db.session.add(apt)
    db.session.commit()

    # Update status to Completed
    resp = client.post(f'/appointments/{apt.id}/status', data={
        'status': 'Completed'
    }, follow_redirects=True)

    assert resp.status_code == 200
    db.session.refresh(apt)
    assert apt.status == 'Completed'
