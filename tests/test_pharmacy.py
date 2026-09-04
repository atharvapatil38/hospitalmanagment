import pytest
from datetime import date, timedelta
from tests.conftest import login_user
from app.models import Medicine, MedicineBatch, Prescription, PrescriptionItem, Patient, Doctor
from app.extensions import db

def test_add_medicine_and_batch(client, init_db):
    login_user(client, 'pharmacy@careplus.com', 'Pharmacy@123')
    
    exp_date = (date.today() + timedelta(days=180)).isoformat()
    resp = client.post('/pharmacy/new', data={
        'name': 'Cefixime 200mg',
        'generic_name': 'Cefixime Trihydrate',
        'category': 'Tablet',
        'manufacturer': 'Cipla Ltd',
        'batch_number': 'CEF-TEST-99',
        'expiry_date': exp_date,
        'purchase_price': '5.00',
        'selling_price': '10.00',
        'quantity_in_stock': '100',
        'minimum_stock_alert': '20',
        'supplier_name': 'MedGlobal',
        'status': 'Active'
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"registered successfully" in resp.data

    med = Medicine.query.filter_by(name='Cefixime 200mg').first()
    assert med is not None
    assert med.quantity_in_stock == 100
    assert med.batches.count() == 1

def test_stock_adjustment_in_out(client, init_db):
    login_user(client, 'pharmacy@careplus.com', 'Pharmacy@123')
    
    med = Medicine(
        medicine_code='MED-TEST-0001',
        name='Test Amoxicillin',
        generic_name='Amoxicillin',
        category='Capsule',
        manufacturer='PharmaCorp',
        batch_number='AMX-001',
        purchase_price=2.0,
        selling_price=5.0,
        quantity_in_stock=50,
        minimum_stock_alert=10,
        expiry_date=date.today() + timedelta(days=180),
        status='Active'
    )
    db.session.add(med)
    db.session.commit()

    # Stock In 25 units
    client.post(f'/pharmacy/{med.id}/adjust-stock', data={
        'transaction_type': 'Stock In',
        'quantity': 25,
        'batch_number': 'BATCH-NEW-01',
        'reference_note': 'Received restock supplier shipment'
    }, follow_redirects=True)

    db.session.refresh(med)
    assert med.quantity_in_stock == 75

    # Stock Out 10 units
    client.post(f'/pharmacy/{med.id}/adjust-stock', data={
        'transaction_type': 'Stock Out',
        'quantity': 10,
        'reference_note': 'Damaged seal discard'
    }, follow_redirects=True)

    db.session.refresh(med)
    assert med.quantity_in_stock == 65
