import pytest
from datetime import date
from tests.conftest import login_user
from app.models import Patient, Invoice, InvoiceItem, Payment
from app.extensions import db

def test_invoice_creation_and_auto_calculation(client, init_db):
    login_user(client, 'accountant@careplus.com', 'Account@123')
    
    pat = Patient(patient_id='PAT-TEST-BILL1', first_name='Billing', last_name='Test', dob=date(1989, 7, 7), gender='Male', phone='+1 555-7777')
    db.session.add(pat)
    db.session.commit()

    # Create Invoice with 2 items: 1x $100, 2x $50, 10% discount, 5% tax
    # Subtotal: $200. Discount (10%): $20. Subtotal after disc: $180. Tax (5% of $180): $9. Grand Total: $189.00
    resp = client.post('/billing/new', data={
        'patient_id': pat.id,
        'billing_type': 'Outpatient',
        'invoice_date': date.today().isoformat(),
        'discount_type': 'Percentage',
        'discount_value': '10.0',
        'tax_rate': '5.0',
        'item_type[]': ['Consultation', 'Lab Test'],
        'item_name[]': ['Specialist Consultation', 'Lipid Panel'],
        'quantity[]': ['1', '2'],
        'unit_price[]': ['100.00', '50.00']
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"created successfully" in resp.data

    inv = Invoice.query.filter_by(patient_id=pat.id).first()
    assert inv is not None
    assert inv.subtotal == 200.0
    assert inv.discount_amount == 20.0
    assert inv.tax_amount == 9.0
    assert inv.grand_total == 189.0
    assert inv.balance_due == 189.0
    assert inv.payment_status == 'Unpaid'

def test_record_payment_and_settlement(client, init_db):
    login_user(client, 'accountant@careplus.com', 'Account@123')
    
    pat = Patient(patient_id='PAT-TEST-BILL2', first_name='Pay', last_name='Test', dob=date(1984, 4, 4), gender='Female', phone='+1 555-8888')
    db.session.add(pat)
    db.session.flush()

    inv = Invoice(
        invoice_number='INV-TEST-0001',
        patient_id=pat.id,
        invoice_date=date.today(),
        billing_type='Outpatient',
        tax_rate=0.0
    )
    db.session.add(inv)
    db.session.flush()

    item = InvoiceItem(invoice_id=inv.id, item_type='Consultation', item_name='Consultation Fee', quantity=1, unit_price=100.0, total_price=100.0)
    db.session.add(item)
    inv.recalculate()
    db.session.commit()

    # 1. Partial payment: $40
    client.post(f'/billing/{inv.id}/payments', data={
        'amount': '40.00',
        'payment_method': 'Cash',
        'transaction_reference': 'CASH-001'
    }, follow_redirects=True)

    db.session.refresh(inv)
    assert inv.paid_amount == 40.0
    assert inv.balance_due == 60.0
    assert inv.payment_status == 'Partially Paid'

    # 2. Final payment: $60
    client.post(f'/billing/{inv.id}/payments', data={
        'amount': '60.00',
        'payment_method': 'Card',
        'transaction_reference': 'CARD-999'
    }, follow_redirects=True)

    db.session.refresh(inv)
    assert inv.paid_amount == 100.0
    assert inv.balance_due == 0.0
    assert inv.payment_status == 'Paid'
