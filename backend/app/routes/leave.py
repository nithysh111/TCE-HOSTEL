from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.leave_request import LeaveRequest
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.helpers import parse_date, get_current_user_id

leave_bp = Blueprint('leave', __name__)


@leave_bp.route('/', methods=['GET'])
@jwt_required()
def list_leave_requests():
    user = User.query.get(get_current_user_id())
    status = request.args.get('status')

    query = LeaveRequest.query
    if user.role == 'student':
        query = query.filter_by(roll_no=user.roll_no)
    if status:
        query = query.filter_by(status=status)

    requests = query.order_by(LeaveRequest.created_at.desc()).all()
    return jsonify({'items': [r.to_dict() for r in requests]}), 200


@leave_bp.route('/', methods=['POST'])
@jwt_required()
def create_leave_request():
    user = User.query.get(get_current_user_id())

    if user.role != 'student' or not user.roll_no:
        return jsonify({'error': 'Only students can submit leave requests'}), 403

    data = request.get_json()
    start_date = parse_date(data.get('start_date'))
    end_date = parse_date(data.get('end_date'))
    reason = data.get('reason', '')
    leave_type = data.get('leave_type', 'regular')

    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date are required'}), 400
    if end_date < start_date:
        return jsonify({'error': 'end_date must be after start_date'}), 400

    leave_req = LeaveRequest(
        roll_no=user.roll_no,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        leave_type=leave_type,
        status='pending',
    )
    db.session.add(leave_req)
    db.session.commit()
    return jsonify(leave_req.to_dict()), 201


@leave_bp.route('/<int:leave_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def update_leave_status(leave_id):
    leave_req = LeaveRequest.query.get(leave_id)
    if not leave_req:
        return jsonify({'error': 'Leave request not found'}), 404

    data = request.get_json()
    status = data.get('status')
    if status not in ('pending', 'approved', 'rejected'):
        return jsonify({'error': 'Invalid status'}), 400

    leave_req.status = status
    db.session.commit()
    return jsonify(leave_req.to_dict()), 200
