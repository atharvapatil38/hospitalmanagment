from datetime import datetime
from app.extensions import db

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(30), unique=True, nullable=False, index=True) # INV-2026-0001
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    admission_id = db.Column(db.Integer, db.ForeignKey('admissions.id', ondelete='SET NULL'), nullable=True)
    invoice_date = db.Column(db.Date, default=datetime.utcnow().date, index=True)
    due_date = db.Column(db.Date, nullable=True)
    billing_type = db.Column(db.String(30), default='Outpatient') # Outpatient, Inpatient, Pharmacy, Laboratory, General

    # Calculations
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    discount_type = db.Column(db.String(20), default='Fixed') # Fixed, Percentage
    discount_value = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=5.0) # 5%
    tax_amount = db.Column(db.Float, default=0.0)
    grand_total = db.Column(db.Float, nullable=False, default=0.0)
    paid_amount = db.Column(db.Float, nullable=False, default=0.0)
    balance_due = db.Column(db.Float, nullable=False, default=0.0)
    payment_status = db.Column(db.String(20), default='Unpaid', index=True) # Unpaid, Partially Paid, Paid

    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(100), nullable=True) # Staff/Accountant name
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', cascade='all, delete-orphan', lazy='dynamic')
    payments = db.relationship('Payment', backref='invoice', cascade='all, delete-orphan', lazy='dynamic')

    def recalculate(self):
        self.subtotal = sum(item.total_price for item in self.items.all())

        if self.discount_type == 'Percentage':
            self.discount_amount = round((self.subtotal * (self.discount_value / 100.0)), 2)
        else:
            self.discount_amount = round(min(self.discount_value, self.subtotal), 2)

        taxable_amount = max(0.0, self.subtotal - self.discount_amount)
        self.tax_amount = round((taxable_amount * (self.tax_rate / 100.0)), 2)
        self.grand_total = round(taxable_amount + self.tax_amount, 2)

        self.paid_amount = round(sum(p.amount for p in self.payments.all()), 2)
        self.balance_due = round(max(0.0, self.grand_total - self.paid_amount), 2)

        if self.balance_due <= 0.001 and self.grand_total > 0:
            self.payment_status = 'Paid'
        elif self.paid_amount > 0:
            self.payment_status = 'Partially Paid'
        else:
            self.payment_status = 'Unpaid'

    def __repr__(self):
        return f"<Invoice {self.invoice_number} - Pat:{self.patient_id} Total:{self.grand_total} Status:{self.payment_status}>"

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)
    item_type = db.Column(db.String(50), default='General') # Consultation, Room Charge, Lab Test, Medicine, Procedure, Nursing, General
    item_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    total_price = db.Column(db.Float, nullable=False, default=0.0)

    def calculate_total(self):
        self.total_price = round(self.quantity * self.unit_price, 2)
        return self.total_price

    def __repr__(self):
        return f"<InvoiceItem {self.item_name} Qty:{self.quantity} Unit:{self.unit_price}>"

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    payment_code = db.Column(db.String(30), unique=True, nullable=False, index=True) # PAY-2026-0001
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(30), nullable=False, default='Cash') # Cash, Card, UPI, Bank Transfer, Cheque
    transaction_reference = db.Column(db.String(100), nullable=True) # Cheque/Txn/UPI ref
    received_by = db.Column(db.String(100), nullable=True) # Accountant/Receptionist name
    receipt_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Payment {self.payment_code} - Inv:{self.invoice_id} Amount:{self.amount} via {self.payment_method}>"
