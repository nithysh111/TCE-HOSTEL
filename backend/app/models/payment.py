from datetime import datetime
from app.extensions import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(30), unique=True, nullable=False)
    roll_no = db.Column(db.String(20), nullable=False, index=True)
    fee_id = db.Column(db.Integer, db.ForeignKey('hostel_fees.id'), nullable=True)
    fine_id = db.Column(db.Integer, db.ForeignKey('fines.id'), nullable=True)
    razorpay_order_id = db.Column(db.String(100), unique=True, nullable=False)
    razorpay_payment_id = db.Column(db.String(100), unique=True, nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.Enum('Pending', 'Success', 'Failed', 'Refunded', name='payment_status'),
        default='Pending',
        nullable=False,
    )
    transaction_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    fee = db.relationship('HostelFee', backref='payments', lazy=True)
    fine = db.relationship('Fine', backref='payments', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'roll_no': self.roll_no,
            'fee_id': self.fee_id,
            'fine_id': self.fine_id,
            'fee_ref': self.fee.fee_id if self.fee else None,
            'fine_ref': self.fine.fine_id if self.fine else None,
            'razorpay_order_id': self.razorpay_order_id,
            'razorpay_payment_id': self.razorpay_payment_id,
            'amount': float(self.amount),
            'status': self.status,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
