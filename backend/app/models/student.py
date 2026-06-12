from datetime import datetime
from app.extensions import db


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', name='gender_type'), nullable=False)
    phone_number = db.Column(db.String(15))
    parent_contact = db.Column(db.String(15))
    room_number = db.Column(db.String(20))
    hostel_block = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_occupancy=False, occupancy_status=None):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'roll_no': self.roll_no,
            'name': self.name,
            'department': self.department,
            'year': self.year,
            'gender': self.gender,
            'phone_number': self.phone_number,
            'parent_contact': self.parent_contact,
            'room_number': self.room_number,
            'hostel_block': self.hostel_block,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_occupancy:
            data['occupancy_status'] = occupancy_status or 'unknown'
        return data
