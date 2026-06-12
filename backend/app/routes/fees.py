from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.hostel_fee import HostelFee
from app.models.student import Student
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.helpers import generate_fee_id, get_current_user_id, parse_date
from app.services.fee_service import FeeService
from app.services.notification_service import NotificationService

fees_bp = Blueprint('fees', __name__)

VALID_STATUSES = ['Pending', 'Paid', 'Overdue']


@fees_bp.route('/', methods=['GET'])
@jwt_required()
def list_fees():
    user = User.query.get(get_current_user_id())
    status = request.args.get('status')
    academic_year = request.args.get('academic_year')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    FeeService.refresh_all_statuses()
    query = HostelFee.query
    if user.role == 'student':
        query = query.filter_by(roll_no=user.roll_no)
    if status:
        query = query.filter_by(status=status)
    if academic_year:
        query = query.filter_by(academic_year=academic_year)

    pagination = query.order_by(HostelFee.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'items': [FeeService.enrich_fee(f) for f in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    }), 200


@fees_bp.route('/summary', methods=['GET'])
@jwt_required()
def fee_summary():
    user = User.query.get(get_current_user_id())
    if user.role == 'student':
        roll_no = user.roll_no
    else:
        roll_no = request.args.get('roll_no')
        if not roll_no:
            return jsonify({'error': 'roll_no is required for admin'}), 400
    return jsonify(FeeService.get_student_summary(roll_no)), 200


@fees_bp.route('/<fee_id>', methods=['GET'])
@jwt_required()
def get_fee(fee_id):
    fee = HostelFee.query.filter_by(fee_id=fee_id).first()
    if not fee:
        return jsonify({'error': 'Fee not found'}), 404

    user = User.query.get(get_current_user_id())
    if user.role == 'student' and fee.roll_no != user.roll_no:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(FeeService.enrich_fee(fee)), 200


@fees_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_fee():
    data = request.get_json()
    roll_no = data.get('roll_no', '').strip()
    academic_year = data.get('academic_year', '').strip()
    fee_amount = data.get('fee_amount')
    due_date = parse_date(data.get('due_date'))

    if not roll_no or not academic_year or fee_amount is None or not due_date:
        return jsonify({'error': 'roll_no, academic_year, fee_amount, and due_date are required'}), 400

    student = Student.query.filter_by(roll_no=roll_no).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    fee = HostelFee(
        fee_id=generate_fee_id(),
        roll_no=roll_no,
        academic_year=academic_year,
        hostel_block=data.get('hostel_block') or student.hostel_block,
        room_number=data.get('room_number') or student.room_number,
        fee_amount=fee_amount,
        due_date=due_date,
        status='Pending',
    )
    db.session.add(fee)
    NotificationService.notify_fee_created(fee)
    db.session.commit()
    return jsonify(FeeService.enrich_fee(fee)), 201


@fees_bp.route('/assign-bulk', methods=['POST'])
@jwt_required()
@admin_required
def assign_bulk_fees():
    data = request.get_json()
    academic_year = data.get('academic_year', '').strip()
    fee_amount = data.get('fee_amount')
    due_date = parse_date(data.get('due_date'))
    hostel_block = data.get('hostel_block')
    roll_numbers = data.get('roll_numbers', [])

    if not academic_year or fee_amount is None or not due_date:
        return jsonify({'error': 'academic_year, fee_amount, and due_date are required'}), 400

    if roll_numbers:
        students = Student.query.filter(Student.roll_no.in_(roll_numbers)).all()
    elif hostel_block:
        students = Student.query.filter_by(hostel_block=hostel_block).all()
    else:
        students = Student.query.all()

    created = []
    for student in students:
        fee = HostelFee(
            fee_id=generate_fee_id(),
            roll_no=student.roll_no,
            academic_year=academic_year,
            hostel_block=student.hostel_block,
            room_number=student.room_number,
            fee_amount=fee_amount,
            due_date=due_date,
            status='Pending',
        )
        db.session.add(fee)
        NotificationService.notify_fee_created(fee)
        created.append(fee)

    db.session.commit()
    return jsonify({
        'message': f'Assigned fees to {len(created)} students',
        'items': [FeeService.enrich_fee(f) for f in created],
    }), 201


@fees_bp.route('/<fee_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_fee(fee_id):
    fee = HostelFee.query.filter_by(fee_id=fee_id).first()
    if not fee:
        return jsonify({'error': 'Fee not found'}), 404

    data = request.get_json()
    if 'fee_amount' in data:
        fee.fee_amount = data['fee_amount']
    if 'due_date' in data:
        fee.due_date = parse_date(data['due_date'])
    if 'academic_year' in data:
        fee.academic_year = data['academic_year']
    if 'hostel_block' in data:
        fee.hostel_block = data['hostel_block']
    if 'room_number' in data:
        fee.room_number = data['room_number']
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return jsonify({'error': f'Invalid status. Must be one of: {VALID_STATUSES}'}), 400
        fee.status = data['status']

    db.session.commit()
    return jsonify(FeeService.enrich_fee(fee)), 200


@fees_bp.route('/<fee_id>/mark-paid', methods=['PUT'])
@jwt_required()
@admin_required
def mark_fee_paid(fee_id):
    fee = HostelFee.query.filter_by(fee_id=fee_id).first()
    if not fee:
        return jsonify({'error': 'Fee not found'}), 404

    fee.status = 'Paid'
    db.session.commit()
    return jsonify(FeeService.enrich_fee(fee)), 200
