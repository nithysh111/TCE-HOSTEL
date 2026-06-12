import json
from datetime import datetime
from app.extensions import db


class FineAuditLog(db.Model):
    __tablename__ = 'fine_audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    fine_id = db.Column(db.String(30), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)
    changed_by = db.Column(db.String(120), nullable=False)
    old_data = db.Column(db.Text)
    new_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'fine_id': self.fine_id,
            'action': self.action,
            'changed_by': self.changed_by,
            'old_data': json.loads(self.old_data) if self.old_data else None,
            'new_data': json.loads(self.new_data) if self.new_data else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
