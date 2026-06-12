from datetime import datetime
from app.extensions import db


class FoodPrediction(db.Model):
    __tablename__ = 'food_predictions'

    id = db.Column(db.Integer, primary_key=True)
    prediction_date = db.Column(db.Date, unique=True, nullable=False)
    predicted_breakfast = db.Column(db.Integer, nullable=False)
    predicted_lunch = db.Column(db.Integer, nullable=False)
    predicted_dinner = db.Column(db.Integer, nullable=False)
    actual_breakfast = db.Column(db.Integer, nullable=True)
    actual_lunch = db.Column(db.Integer, nullable=True)
    actual_dinner = db.Column(db.Integer, nullable=True)
    total_students = db.Column(db.Integer)
    students_inside = db.Column(db.Integer)
    students_outside = db.Column(db.Integer)
    students_on_leave = db.Column(db.Integer)
    is_weekend = db.Column(db.Boolean, default=False)
    is_holiday = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'predicted_breakfast': self.predicted_breakfast,
            'predicted_lunch': self.predicted_lunch,
            'predicted_dinner': self.predicted_dinner,
            'actual_breakfast': self.actual_breakfast,
            'actual_lunch': self.actual_lunch,
            'actual_dinner': self.actual_dinner,
            'total_students': self.total_students,
            'students_inside': self.students_inside,
            'students_outside': self.students_outside,
            'students_on_leave': self.students_on_leave,
            'is_weekend': self.is_weekend,
            'is_holiday': self.is_holiday,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
