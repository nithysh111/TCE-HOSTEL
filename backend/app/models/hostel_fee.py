from datetime import datetime, date
from app.extensions import db


class HostelFee(db.Model):
    __tablename__ = 'hostel_fees'

    id = db.Column(db.Integer, primary_key=True)
    fee_id = db.Column(db.String(30), unique=True, nullable=False)
    roll_no = db.Column(db.String(20), nullable=False, index=True)
    academic_year = db.Column(db.String(20), nullable=False)
    hostel_block = db.Column(db.String(50))
    room_number = db.Column(db.String(20))
    fee_amount = db.Column(db.Numeric(10, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.Enum('Pending', 'Paid', 'Overdue', name='hostel_fee_status'),
        default='Pending',
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def refresh_status(self):
        if self.status == 'Paid':
            return
        if self.due_date and self.due_date < date.today():
            self.status = 'Overdue'
        elif self.status == 'Overdue' and self.due_date >= date.today():
            self.status = 'Pending'

    def to_dict(self, student_name=None):
        self.refresh_status()
        return {
            'id': self.id,
            'fee_id': self.fee_id,
            'roll_no': self.roll_no,
            'student_name': student_name,
            'academic_year': self.academic_year,
            'hostel_block': self.hostel_block,
            'room_number': self.room_number,
            'fee_amount': float(self.fee_amount),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
