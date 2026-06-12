from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.utils.helpers import get_current_user_id

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(identity=str(user.id))
    response = {'access_token': token, 'user': user.to_dict()}

    if user.role == 'student' and user.student:
        response['student'] = user.student.to_dict()

    return jsonify(response), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')
    roll_no = data.get('roll_no', '').strip()
    name = data.get('name', '').strip()
    department = data.get('department', '').strip()
    year = data.get('year')
    gender = data.get('gender', 'Other')

    if not all([email, password, roll_no, name, department, year]):
        return jsonify({'error': 'All required fields must be provided'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    if User.query.filter_by(roll_no=roll_no).first():
        return jsonify({'error': 'Roll number already registered'}), 409
    if Student.query.filter_by(roll_no=roll_no).first():
        return jsonify({'error': 'Student roll number already exists'}), 409

    user = User(email=email, roll_no=roll_no, role='student')
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    student = Student(
        user_id=user.id,
        roll_no=roll_no,
        name=name,
        department=department,
        year=int(year),
        gender=gender,
        phone_number=data.get('phone_number'),
        parent_contact=data.get('parent_contact'),
        room_number=data.get('room_number'),
        hostel_block=data.get('hostel_block'),
    )
    db.session.add(student)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': token,
        'user': user.to_dict(),
        'student': student.to_dict(),
    }), 201


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user = User.query.get(get_current_user_id())
    if not user:
        return jsonify({'error': 'User not found'}), 404

    response = {'user': user.to_dict()}
    if user.student:
        response['student'] = user.student.to_dict()
    return jsonify(response), 200
