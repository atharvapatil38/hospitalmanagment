import pytest
from datetime import date, datetime
from tests.conftest import login_user
from app.models import Patient, Doctor, Room, Bed, Admission, DischargeSummary
from app.extensions import db

def test_inpatient_admission_and_bed_occupancy(client, init_db):
    login_user(client, 'nurse@careplus.com', 'Nurse@123')
    
    pat = Patient(patient_id='PAT-TEST-ADM1', first_name='Inpatient', last_name='Test', dob=date(1982, 6, 15), gender='Male', phone='+1 555-3333')
    db.session.add(pat)
    db.session.commit()

    doc = Doctor.query.first()
    room = Room.query.first()
    bed = Bed.query.filter_by(room_id=room.id, status='Available').first()

    # Submit Admission
    resp = client.post('/admissions/admit', data={
        'patient_id': pat.id,
        'doctor_id': doc.id,
        'department_id': doc.department_id,
        'room_id': room.id,
        'bed_id': bed.id,
        'reason_for_admission': 'Severe acute asthma exacerbation',
        'initial_diagnosis': 'Status Asthmaticus'
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"admitted successfully" in resp.data

    # Verify Bed is now Occupied and Patient is Admitted
    db.session.refresh(bed)
    db.session.refresh(pat)
    assert bed.status == 'Occupied'
    assert pat.status == 'Admitted'

def test_patient_discharge_releases_bed(client, init_db):
    login_user(client, 'doctor@careplus.com', 'Doctor@123')
    
    pat = Patient(patient_id='PAT-TEST-ADM2', first_name='Discharge', last_name='Patient', dob=date(1975, 4, 10), gender='Female', phone='+1 555-4444', status='Admitted')
    db.session.add(pat)
    db.session.flush()

    room = Room.query.first()
    bed = Bed.query.filter_by(room_id=room.id).first()
    bed.status = 'Occupied'

    adm = Admission(
        admission_id='ADM-TEST-DISC1',
        patient_id=pat.id,
        doctor_id=Doctor.query.first().id,
        department_id=Doctor.query.first().department_id,
        room_id=room.id,
        bed_id=bed.id,
        admission_date=datetime.utcnow(),
        reason_for_admission='Post surgical observation',
        initial_diagnosis='Recovered post-op',
        status='Admitted'
    )
    db.session.add(adm)
    db.session.commit()

    # Discharge patient
    resp = client.post(f'/admissions/{adm.id}/discharge', data={
        'condition_at_discharge': 'Recovered',
        'final_diagnosis': 'Resolved appendicitis',
        'treatment_summary': 'Uncomplicated post-operative recovery, vitals stable.',
        'discharge_medications': 'Paracetamol 500mg SOS',
        'advice_instructions': 'Rest and follow-up in 10 days',
        'follow_up_date': date.today().isoformat(),
        'doctor_signature': 'Dr. Test Physician'
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"discharged successfully" in resp.data

    db.session.refresh(bed)
    db.session.refresh(pat)
    db.session.refresh(adm)

    assert bed.status == 'Available'
    assert pat.status == 'Discharged'
    assert adm.status == 'Discharged'
