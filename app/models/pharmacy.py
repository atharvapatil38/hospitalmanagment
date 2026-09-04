from datetime import datetime
from app.extensions import db

class Medicine(db.Model):
    __tablename__ = 'medicines'

    id = db.Column(db.Integer, primary_key=True)
    medicine_code = db.Column(db.String(30), unique=True, nullable=False, index=True) # MED-2026-0001
    name = db.Column(db.String(120), nullable=False, index=True) # Brand name: e.g. "Augmentin 625"
    generic_name = db.Column(db.String(120), nullable=False, index=True) # Generic: e.g. "Amoxicillin + Clavulanic Acid"
    category = db.Column(db.String(50), nullable=False) # Tablet, Capsule, Syrup, Injection, Ointment, Drops, Inhaler, IV Fluid
    manufacturer = db.Column(db.String(100), nullable=False)
    batch_number = db.Column(db.String(50), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    purchase_price = db.Column(db.Float, nullable=False, default=0.0)
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    quantity_in_stock = db.Column(db.Integer, nullable=False, default=0)
    minimum_stock_alert = db.Column(db.Integer, nullable=False, default=20)
    supplier_name = db.Column(db.String(100), nullable=True)
    side_effects = db.Column(db.Text, nullable=True)
    storage_conditions = db.Column(db.String(100), default='Store in a cool, dry place')
    status = db.Column(db.String(20), default='Active') # Active, Discontinued
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    batches = db.relationship('MedicineBatch', backref='medicine', cascade='all, delete-orphan', lazy='dynamic')
    sale_items = db.relationship('PharmacySaleItem', backref='medicine', lazy='dynamic')

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.minimum_stock_alert

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < datetime.utcnow().date()
        return False

    @property
    def is_expiring_soon(self):
        if self.expiry_date:
            today = datetime.utcnow().date()
            delta = (self.expiry_date - today).days
            return 0 <= delta <= 30
        return False

    def __repr__(self):
        return f"<Medicine {self.name} ({self.medicine_code}) - Stock: {self.quantity_in_stock}>"

class MedicineBatch(db.Model):
    __tablename__ = 'medicine_batches'

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False)
    batch_number = db.Column(db.String(50), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    purchase_price = db.Column(db.Float, nullable=False, default=0.0)
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    received_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<MedicineBatch {self.batch_number} - Med:{self.medicine_id} Qty:{self.quantity}>"

class PharmacySale(db.Model):
    __tablename__ = 'pharmacy_sales'

    id = db.Column(db.Integer, primary_key=True)
    sale_code = db.Column(db.String(30), unique=True, nullable=False, index=True) # PHR-2026-0001
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='SET NULL'), nullable=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id', ondelete='SET NULL'), nullable=True)
    customer_name = db.Column(db.String(100), nullable=True)
    subtotal = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    net_amount = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(30), default='Cash') # Cash, Card, UPI
    sold_by = db.Column(db.String(100), nullable=True) # Pharmacist name
    sale_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    items = db.relationship('PharmacySaleItem', backref='sale', cascade='all, delete-orphan', lazy='dynamic')
    patient = db.relationship('Patient', backref='pharmacy_purchases')
    prescription = db.relationship('Prescription', backref='pharmacy_sales')

    def __repr__(self):
        return f"<PharmacySale {self.sale_code} - Total: {self.net_amount}>"

class PharmacySaleItem(db.Model):
    __tablename__ = 'pharmacy_sale_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('pharmacy_sales.id', ondelete='CASCADE'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id', ondelete='RESTRICT'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    total_price = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"<PharmacySaleItem Sale:{self.sale_id} Med:{self.medicine_id} Qty:{self.quantity}>"
