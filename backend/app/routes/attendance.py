from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.attendance import Attendance
from app.services.attendance_service import AttendanceService
from app.utils.decorators import admin_required
from app.utils.helpers import parse_date
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/import/csv', methods=['POST'])
@jwt_required()
@admin_required
def import_csv():
    if 'file' not in request.files:
        content = request.get_data(as_text=True)
        if not content:
            return jsonify({'error': 'CSV file or content required'}), 400
    else:
        file = request.files['file']
        content = file.read().decode('utf-8')

    result = AttendanceService.import_from_csv(content)
    return jsonify(result), 200


@attendance_bp.route('/import/api', methods=['POST'])
@jwt_required()
@admin_required
def import_api():
    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({'error': 'Expected array of attendance records'}), 400

    result = AttendanceService.import_from_api(data)
    return jsonify(result), 200


@attendance_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
def list_attendance():
    roll_no = request.args.get('roll_no')
    attendance_date = request.args.get('date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    result = AttendanceService.get_attendance_logs(roll_no, attendance_date, page, per_page)
    return jsonify(result), 200


@attendance_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_attendance():
    data = request.get_json()
    roll_no = data.get('roll_no')
    attendance_date = parse_date(data.get('attendance_date'))

    if not roll_no or not attendance_date:
        return jsonify({'error': 'roll_no and attendance_date are required'}), 400

    entry_time = None
    exit_time = None
    if data.get('entry_time'):
        entry_time = datetime.fromisoformat(data['entry_time'])
    if data.get('exit_time'):
        exit_time = datetime.fromisoformat(data['exit_time'])

    record = Attendance(
        roll_no=roll_no,
        entry_time=entry_time,
        exit_time=exit_time,
        attendance_date=attendance_date,
        status=data.get('status', 'outside'),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201
