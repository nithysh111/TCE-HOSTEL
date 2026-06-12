from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.leave_request import LeaveRequest
from app.services.occupancy_service import OccupancyService
from app.utils.decorators import admin_required
from app.utils.helpers import parse_date
from datetime import date

students_bp = Blueprint('students', __name__)


@students_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
def list_students():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    department = request.args.get('department')
    hostel_block = request.args.get('hostel_block')

    query = Student.query
    if department:
        query = query.filter(Student.department == department)
    if hostel_block:
        query = query.filter(Student.hostel_block == hostel_block)

    pagination = query.order_by(Student.roll_no).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'items': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    }), 200


@students_bp.route('/search/<roll_no>', methods=['GET'])
@jwt_required()
@admin_required
def search_student(roll_no):
    student = Student.query.filter_by(roll_no=roll_no).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    target_date = date.today()
    on_leave = roll_no in OccupancyService.get_students_on_leave(target_date)

    latest = Attendance.query.filter_by(
        roll_no=roll_no, attendance_date=target_date
    ).order_by(Attendance.id.desc()).first()

    if on_leave:
        occupancy_status = 'on_leave'
    elif latest:
        occupancy_status = latest.status
    else:
        occupancy_status = 'outside'

    data = student.to_dict(include_occupancy=True, occupancy_status=occupancy_status)
    return jsonify(data), 200


@students_bp.route('/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(student.to_dict()), 200


@students_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_student():
    data = request.get_json()
    required = ['roll_no', 'name', 'department', 'year', 'gender']
    if not all(data.get(f) for f in required):
        return jsonify({'error': 'Missing required fields'}), 400

    if Student.query.filter_by(roll_no=data['roll_no']).first():
        return jsonify({'error': 'Roll number already exists'}), 409

    student = Student(
        roll_no=data['roll_no'],
        name=data['name'],
        department=data['department'],
        year=int(data['year']),
        gender=data['gender'],
        phone_number=data.get('phone_number'),
        parent_contact=data.get('parent_contact'),
        room_number=data.get('room_number'),
        hostel_block=data.get('hostel_block'),
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201


@students_bp.route('/<int:student_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json()
    for field in ['name', 'department', 'year', 'gender', 'phone_number',
                  'parent_contact', 'room_number', 'hostel_block']:
        if field in data:
            setattr(student, field, data[field])

    db.session.commit()
    return jsonify(student.to_dict()), 200


@students_bp.route('/rooms', methods=['GET'])
@jwt_required()
@admin_required
def room_allocations():
    students = Student.query.filter(
        Student.room_number.isnot(None)
    ).order_by(Student.hostel_block, Student.room_number).all()

    rooms = {}
    for s in students:
        key = f"{s.hostel_block or 'Unassigned'}-{s.room_number}"
        if key not in rooms:
            rooms[key] = {
                'hostel_block': s.hostel_block,
                'room_number': s.room_number,
                'students': [],
            }
        rooms[key]['students'].append(s.to_dict())

    return jsonify(list(rooms.values())), 200
