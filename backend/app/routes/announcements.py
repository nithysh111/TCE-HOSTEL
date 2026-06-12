from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import date
from app.extensions import db
from app.models.announcement import Announcement
from app.utils.decorators import admin_required
from app.utils.helpers import parse_date

announcements_bp = Blueprint('announcements', __name__)


@announcements_bp.route('/', methods=['GET'])
@jwt_required()
def list_announcements():
    active_only = request.args.get('active', 'true').lower() == 'true'
    query = Announcement.query

    if active_only:
        today = date.today()
        query = query.filter(
            db.or_(
                Announcement.expiry_date.is_(None),
                Announcement.expiry_date >= today
            )
        )

    announcements = query.order_by(
        Announcement.priority.desc(),
        Announcement.created_at.desc()
    ).all()
    return jsonify({'items': [a.to_dict() for a in announcements]}), 200


@announcements_bp.route('/<int:announcement_id>', methods=['GET'])
@jwt_required()
def get_announcement(announcement_id):
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return jsonify({'error': 'Announcement not found'}), 404
    return jsonify(announcement.to_dict()), 200


@announcements_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_announcement():
    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()

    if not title or not description:
        return jsonify({'error': 'Title and description are required'}), 400

    announcement = Announcement(
        title=title,
        description=description,
        priority=data.get('priority', 'medium'),
        expiry_date=parse_date(data.get('expiry_date')),
    )
    db.session.add(announcement)
    db.session.commit()
    return jsonify(announcement.to_dict()), 201


@announcements_bp.route('/<int:announcement_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_announcement(announcement_id):
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return jsonify({'error': 'Announcement not found'}), 404

    data = request.get_json()
    for field in ['title', 'description', 'priority']:
        if field in data:
            setattr(announcement, field, data[field])
    if 'expiry_date' in data:
        announcement.expiry_date = parse_date(data['expiry_date'])

    db.session.commit()
    return jsonify(announcement.to_dict()), 200


@announcements_bp.route('/<int:announcement_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_announcement(announcement_id):
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return jsonify({'error': 'Announcement not found'}), 404

    db.session.delete(announcement)
    db.session.commit()
    return jsonify({'message': 'Announcement deleted successfully'}), 200
