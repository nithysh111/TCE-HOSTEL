import json
from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.fine import Fine, FINE_REASONS
from app.models.student import Student
from app.models.user import User
from app.models.fine_audit_log import FineAuditLog
from app.utils.decorators import admin_required
from app.utils.helpers import generate_fine_id, get_current_user_id, parse_date
from app.services.fee_service import FeeService
from app.services.notification_service import NotificationService

fines_bp = Blueprint('fines', __name__)

VALID_STATUSES = ['Pending', 'Paid', 'Overdue']


def _log_fine_action(fine, action, changed_by, old_data=None, new_data=None):
    log = FineAuditLog(
        fine_id=fine.fine_id,
        action=action,
        changed_by=changed_by,
        old_data=json.dumps(old_data) if old_data else None,
        new_data=json.dumps(new_data) if new_data else None,
    )
    db.session.add(log)


@fines_bp.route('/', methods=['GET'])
@jwt_required()
def list_fines():
    user = User.query.get(get_current_user_id())
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    FeeService.refresh_all_statuses()
    query = Fine.query
    if user.role == 'student':
        query = query.filter_by(roll_no=user.roll_no)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Fine.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'items': [f.to_dict() for f in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    }), 200


@fines_bp.route('/reasons', methods=['GET'])
@jwt_required()
def list_fine_reasons():
    return jsonify({'reasons': FINE_REASONS}), 200


@fines_bp.route('/<fine_id>', methods=['GET'])
@jwt_required()
def get_fine(fine_id):
    fine = Fine.query.filter_by(fine_id=fine_id).first()
    if not fine:
        return jsonify({'error': 'Fine not found'}), 404

    user = User.query.get(get_current_user_id())
    if user.role == 'student' and fine.roll_no != user.roll_no:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(fine.to_dict()), 200


@fines_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_fine():
    user = User.query.get(get_current_user_id())
    data = request.get_json()
    roll_no = data.get('roll_no', '').strip()
    fine_amount = data.get('fine_amount')
    fine_reason = data.get('fine_reason')
    due_date = parse_date(data.get('due_date'))
    issued_date = parse_date(data.get('issued_date')) or date.today()

    if not roll_no or fine_amount is None or not fine_reason or not due_date:
        return jsonify({'error': 'roll_no, fine_amount, fine_reason, and due_date are required'}), 400
    if fine_reason not in FINE_REASONS:
        return jsonify({'error': f'Invalid fine reason. Must be one of: {FINE_REASONS}'}), 400

    student = Student.query.filter_by(roll_no=roll_no).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    fine = Fine(
        fine_id=generate_fine_id(),
        roll_no=roll_no,
        student_name=student.name,
        fine_amount=fine_amount,
        fine_reason=fine_reason,
        fine_description=data.get('fine_description', ''),
        issued_date=issued_date,
        due_date=due_date,
        status='Pending',
        created_by=user.email,
    )
    db.session.add(fine)
    _log_fine_action(fine, 'created', user.email, new_data=fine.to_dict())
    NotificationService.notify_fine_created(fine)
    db.session.commit()
    return jsonify(fine.to_dict()), 201


@fines_bp.route('/<fine_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_fine(fine_id):
    user = User.query.get(get_current_user_id())
    fine = Fine.query.filter_by(fine_id=fine_id).first()
    if not fine:
        return jsonify({'error': 'Fine not found'}), 404

    old_data = fine.to_dict()
    data = request.get_json()

    if 'fine_amount' in data:
        fine.fine_amount = data['fine_amount']
    if 'fine_reason' in data:
        if data['fine_reason'] not in FINE_REASONS:
            return jsonify({'error': f'Invalid fine reason'}), 400
        fine.fine_reason = data['fine_reason']
    if 'fine_description' in data:
        fine.fine_description = data['fine_description']
    if 'due_date' in data:
        fine.due_date = parse_date(data['due_date'])
    if 'issued_date' in data:
        fine.issued_date = parse_date(data['issued_date'])
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return jsonify({'error': f'Invalid status'}), 400
        fine.status = data['status']

    _log_fine_action(fine, 'updated', user.email, old_data=old_data, new_data=fine.to_dict())
    db.session.commit()
    return jsonify(fine.to_dict()), 200


@fines_bp.route('/<fine_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_fine(fine_id):
    user = User.query.get(get_current_user_id())
    fine = Fine.query.filter_by(fine_id=fine_id).first()
    if not fine:
        return jsonify({'error': 'Fine not found'}), 404
    if fine.status == 'Paid':
        return jsonify({'error': 'Cannot delete a paid fine'}), 400

    old_data = fine.to_dict()
    _log_fine_action(fine, 'deleted', user.email, old_data=old_data)
    db.session.delete(fine)
    db.session.commit()
    return jsonify({'message': 'Fine deleted'}), 200


@fines_bp.route('/<fine_id>/mark-paid', methods=['PUT'])
@jwt_required()
@admin_required
def mark_fine_paid(fine_id):
    user = User.query.get(get_current_user_id())
    fine = Fine.query.filter_by(fine_id=fine_id).first()
    if not fine:
        return jsonify({'error': 'Fine not found'}), 404

    old_data = fine.to_dict()
    fine.status = 'Paid'
    _log_fine_action(fine, 'marked_paid', user.email, old_data=old_data, new_data=fine.to_dict())
    NotificationService.notify_fine_paid(fine)
    db.session.commit()
    return jsonify(fine.to_dict()), 200


@fines_bp.route('/<fine_id>/audit', methods=['GET'])
@jwt_required()
@admin_required
def fine_audit_history(fine_id):
    logs = FineAuditLog.query.filter_by(fine_id=fine_id).order_by(
        FineAuditLog.created_at.desc()
    ).all()
    return jsonify({'items': [l.to_dict() for l in logs]}), 200
