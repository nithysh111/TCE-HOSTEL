from datetime import datetime, date
from app.extensions import db


FINE_REASONS = [
    'Late Hostel Entry',
    'Property Damage',
    'Mess Rule Violation',
    'Room Maintenance Fine',
    'Disciplinary Fine',
    'Other Custom Fine',
]


class Fine(db.Model):
    __tablename__ = 'fines'

    id = db.Column(db.Integer, primary_key=True)
    fine_id = db.Column(db.String(30), unique=True, nullable=False)
    roll_no = db.Column(db.String(20), nullable=False, index=True)
    student_name = db.Column(db.String(100), nullable=False)
    fine_amount = db.Column(db.Numeric(10, 2), nullable=False)
    fine_reason = db.Column(
        db.Enum(*FINE_REASONS, name='fine_reason'),
        nullable=False,
    )
    fine_description = db.Column(db.Text)
    issued_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.Enum('Pending', 'Paid', 'Overdue', name='fine_status'),
        default='Pending',
        nullable=False,
    )
    created_by = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def refresh_status(self):
        if self.status == 'Paid':
            return
        if self.due_date and self.due_date < date.today():
            self.status = 'Overdue'
        elif self.status == 'Overdue' and self.due_date >= date.today():
            self.status = 'Pending'

    def to_dict(self):
        self.refresh_status()
        return {
            'id': self.id,
            'fine_id': self.fine_id,
            'roll_no': self.roll_no,
            'student_name': self.student_name,
            'fine_amount': float(self.fine_amount),
            'fine_reason': self.fine_reason,
            'fine_description': self.fine_description,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
