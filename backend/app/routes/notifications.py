from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.notification import Notification
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.helpers import get_current_user_id
from app.services.notification_service import NotificationService

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def list_notifications():
    user = User.query.get(get_current_user_id())
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if user.role == 'student':
        NotificationService.run_reminder_checks()

    query = Notification.query
    if user.role == 'student':
        query = query.filter_by(roll_no=user.roll_no)
    elif request.args.get('roll_no'):
        query = query.filter_by(roll_no=request.args.get('roll_no'))
    if unread_only:
        query = query.filter_by(is_read=False)

    pagination = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    unread_count = Notification.query.filter_by(
        roll_no=user.roll_no, is_read=False
    ).count() if user.role == 'student' else 0

    return jsonify({
        'items': [n.to_dict() for n in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'unread_count': unread_count,
    }), 200


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_read(notification_id):
    user = User.query.get(get_current_user_id())
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    if user.role == 'student' and notification.roll_no != user.roll_no:
        return jsonify({'error': 'Access denied'}), 403

    notification.is_read = True
    db.session.commit()
    return jsonify(notification.to_dict()), 200


@notifications_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    user = User.query.get(get_current_user_id())
    if user.role != 'student' or not user.roll_no:
        return jsonify({'error': 'Only students can mark all as read'}), 403

    Notification.query.filter_by(roll_no=user.roll_no, is_read=False).update(
        {'is_read': True}
    )
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'}), 200


@notifications_bp.route('/run-reminders', methods=['POST'])
@jwt_required()
@admin_required
def run_reminders():
    NotificationService.run_reminder_checks()
    return jsonify({'message': 'Reminder checks completed'}), 200
