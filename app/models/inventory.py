from datetime import datetime
from app.extensions import db

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'

    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(30), unique=True, nullable=False, index=True) # INV-ITM-001
    name = db.Column(db.String(120), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False) # Medical Equipment, Surgical Supplies, Consumables, Cleaning Supplies, PPE, Diagnostic Tools, Other
    quantity = db.Column(db.Integer, nullable=False, default=0)
    unit = db.Column(db.String(30), default='Units') # Units, Boxes, Packs, Rolls, Pairs, Sets
    minimum_stock = db.Column(db.Integer, default=10)
    location = db.Column(db.String(100), default='Main Storage') # Main Storage, ICU Ward, Emergency Room, Operation Theater
    supplier_name = db.Column(db.String(100), nullable=True)
    unit_price = db.Column(db.Float, default=0.0)
    purchase_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active') # Active, Low Stock, Out of Stock, Maintenance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = db.relationship('InventoryTransaction', backref='item', cascade='all, delete-orphan', lazy='dynamic')

    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_stock

    def __repr__(self):
        return f"<InventoryItem {self.name} ({self.item_code}) - Qty: {self.quantity}>"

class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transactions'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id', ondelete='CASCADE'), nullable=False)
    transaction_type = db.Column(db.String(30), nullable=False) # Stock In, Stock Out, Adjustment, Damaged/Disposed
    quantity = db.Column(db.Integer, nullable=False) # positive quantity
    unit_price = db.Column(db.Float, default=0.0)
    reference_note = db.Column(db.String(255), nullable=True) # Department issued to / Invoice ref
    performed_by = db.Column(db.String(100), nullable=True) # User/Staff name
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<InventoryTransaction {self.transaction_type} Qty:{self.quantity} for Item:{self.item_id}>"
