from datetime import datetime
from app.extensions import db


class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.String(20), unique=True, nullable=False)
    roll_no = db.Column(db.String(20), nullable=False, index=True)
    category = db.Column(
        db.Enum(
            'Electrical Issue', 'Room Cleaning', 'WiFi Issue',
            'Food Quality Issue', 'Water Issue', 'Other',
            name='complaint_category'
        ),
        nullable=False
    )
    description = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum('Open', 'In Progress', 'Resolved', name='complaint_status'),
        default='Open',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'roll_no': self.roll_no,
            'category': self.category,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
