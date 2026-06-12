from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.complaint import Complaint
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.helpers import generate_complaint_id, get_current_user_id

complaints_bp = Blueprint('complaints', __name__)

VALID_CATEGORIES = [
    'Electrical Issue', 'Room Cleaning', 'WiFi Issue',
    'Food Quality Issue', 'Water Issue', 'Other'
]
VALID_STATUSES = ['Open', 'In Progress', 'Resolved']


@complaints_bp.route('/', methods=['GET'])
@jwt_required()
def list_complaints():
    user = User.query.get(get_current_user_id())
    status = request.args.get('status')
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Complaint.query
    if user.role == 'student':
        query = query.filter_by(roll_no=user.roll_no)
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)

    pagination = query.order_by(Complaint.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'items': [c.to_dict() for c in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    }), 200


@complaints_bp.route('/<complaint_id>', methods=['GET'])
@jwt_required()
def get_complaint(complaint_id):
    complaint = Complaint.query.filter_by(complaint_id=complaint_id).first()
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    user = User.query.get(get_current_user_id())
    if user.role == 'student' and complaint.roll_no != user.roll_no:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(complaint.to_dict()), 200


@complaints_bp.route('/', methods=['POST'])
@jwt_required()
def create_complaint():
    user = User.query.get(get_current_user_id())

    if user.role != 'student' or not user.roll_no:
        return jsonify({'error': 'Only students can submit complaints'}), 403

    data = request.get_json()
    category = data.get('category')
    description = data.get('description', '').strip()

    if not category or not description:
        return jsonify({'error': 'Category and description are required'}), 400
    if category not in VALID_CATEGORIES:
        return jsonify({'error': f'Invalid category. Must be one of: {VALID_CATEGORIES}'}), 400

    complaint = Complaint(
        complaint_id=generate_complaint_id(),
        roll_no=user.roll_no,
        category=category,
        description=description,
        status='Open',
    )
    db.session.add(complaint)
    db.session.commit()
    return jsonify(complaint.to_dict()), 201


@complaints_bp.route('/<complaint_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def update_complaint_status(complaint_id):
    complaint = Complaint.query.filter_by(complaint_id=complaint_id).first()
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    data = request.get_json()
    status = data.get('status')
    if status not in VALID_STATUSES:
        return jsonify({'error': f'Invalid status. Must be one of: {VALID_STATUSES}'}), 400

    complaint.status = status
    db.session.commit()
    return jsonify(complaint.to_dict()), 200
