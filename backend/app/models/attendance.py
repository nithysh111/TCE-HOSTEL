from datetime import datetime
from app.extensions import db


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), nullable=False, index=True)
    entry_time = db.Column(db.DateTime, nullable=True)
    exit_time = db.Column(db.DateTime, nullable=True)
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(
        db.Enum('inside', 'outside', 'on_leave', name='attendance_status'),
        default='outside',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'roll_no': self.roll_no,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
