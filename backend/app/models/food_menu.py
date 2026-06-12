from datetime import datetime
from app.extensions import db


class FoodMenu(db.Model):
    __tablename__ = 'food_menus'

    id = db.Column(db.Integer, primary_key=True)
    menu_date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(
        db.Enum('Breakfast', 'Lunch', 'Dinner', name='meal_type'),
        nullable=False
    )
    menu_title = db.Column(db.String(200), nullable=False)
    menu_items = db.Column(db.Text, nullable=False)
    is_special = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('menu_date', 'meal_type', name='unique_menu_date_meal'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'menu_date': self.menu_date.isoformat() if self.menu_date else None,
            'meal_type': self.meal_type,
            'menu_title': self.menu_title,
            'menu_items': self.menu_items,
            'is_special': self.is_special,
            'description': self.description,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
