from datetime import datetime
from app.extensions import db


class FoodWastage(db.Model):
    __tablename__ = 'food_wastage'

    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(
        db.Enum('Breakfast', 'Lunch', 'Dinner', name='wastage_meal_type'),
        nullable=False
    )
    prepared_quantity = db.Column(db.Integer, nullable=False)
    consumed_quantity = db.Column(db.Integer, nullable=False)
    wasted_quantity = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('report_date', 'meal_type', name='unique_wastage_date_meal'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'meal_type': self.meal_type,
            'prepared_quantity': self.prepared_quantity,
            'consumed_quantity': self.consumed_quantity,
            'wasted_quantity': self.wasted_quantity,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
