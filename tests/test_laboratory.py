import pytest
from datetime import date
from tests.conftest import login_user
from app.models import Patient, Doctor, LabTest, LabOrder, LabResult
from app.extensions import db

def test_laboratory_order_and_result_workflow(client, init_db):
    login_user(client, 'doctor@careplus.com', 'Doctor@123')
    
    pat = Patient(patient_id='PAT-TEST-LAB1', first_name='Lab', last_name='Subject', dob=date(1993, 9, 9), gender='Male', phone='+1 555-9090')
    db.session.add(pat)
    db.session.flush()

    test = LabTest(
        test_code='LAB-TEST-01',
        test_name='Serum Creatinine',
        category='Biochemistry',
        price=30.0,
        normal_range='0.7 - 1.3',
        unit='mg/dL',
        sample_type='Blood'
    )
    db.session.add(test)
    db.session.commit()

    doc = Doctor.query.first()

    # 1. Doctor creates Lab Order
    resp1 = client.post('/laboratory/order/new', data={
        'patient_id': pat.id,
        'doctor_id': doc.id,
        'lab_test_id': test.id,
        'priority': 'Urgent',
        'clinical_notes': 'Check baseline renal clearance'
    }, follow_redirects=True)

    assert resp1.status_code == 200
    assert b"submitted successfully" in resp1.data

    order = LabOrder.query.filter_by(patient_id=pat.id).first()
    assert order is not None
    assert order.status == 'Requested'

    # 2. Lab Tech enters findings and completes result
    client.get('/auth/logout')
    login_user(client, 'lab@careplus.com', 'Lab@123')
    resp2 = client.post(f'/laboratory/orders/{order.id}/result', data={
        'result_value': '1.1',
        'reference_range': '0.7 - 1.3',
        'unit': 'mg/dL',
        'status_flag': 'Normal',
        'technician_name': 'Marcus Vance',
        'verified_by': 'Dr. Pathologist',
        'remarks': 'Normal baseline renal value'
    }, follow_redirects=True)

    assert resp2.status_code == 200
    assert b"published successfully" in resp2.data

    db.session.refresh(order)
    assert order.status == 'Completed'
    assert order.result is not None
    assert order.result.result_value == '1.1'
    assert order.result.status_flag == 'Normal'
