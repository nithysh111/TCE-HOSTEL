from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.occupancy_service import OccupancyService
from app.utils.decorators import admin_required
from app.utils.helpers import parse_date

occupancy_bp = Blueprint('occupancy', __name__)


@occupancy_bp.route('/summary', methods=['GET'])
@jwt_required()
@admin_required
def occupancy_summary():
    target_date = parse_date(request.args.get('date'))
    summary = OccupancyService.get_occupancy_summary(target_date)
    return jsonify(summary), 200


@occupancy_bp.route('/inside', methods=['GET'])
@jwt_required()
@admin_required
def students_inside():
    target_date = parse_date(request.args.get('date'))
    students = OccupancyService.get_students_by_status('inside', target_date)
    return jsonify({'items': students, 'count': len(students)}), 200


@occupancy_bp.route('/outside', methods=['GET'])
@jwt_required()
@admin_required
def students_outside():
    target_date = parse_date(request.args.get('date'))
    students = OccupancyService.get_students_by_status('outside', target_date)
    return jsonify({'items': students, 'count': len(students)}), 200


@occupancy_bp.route('/on-leave', methods=['GET'])
@jwt_required()
@admin_required
def students_on_leave():
    target_date = parse_date(request.args.get('date'))
    students = OccupancyService.get_students_by_status('on_leave', target_date)
    return jsonify({'items': students, 'count': len(students)}), 200


@occupancy_bp.route('/trend', methods=['GET'])
@jwt_required()
@admin_required
def occupancy_trend():
    days = request.args.get('days', 30, type=int)
    trend = OccupancyService.get_occupancy_trend(days)
    return jsonify({'items': trend}), 200


@occupancy_bp.route('/weekly', methods=['GET'])
@jwt_required()
@admin_required
def weekly_occupancy():
    data = OccupancyService.get_weekly_occupancy()
    return jsonify({'items': data}), 200


@occupancy_bp.route('/monthly', methods=['GET'])
@jwt_required()
@admin_required
def monthly_occupancy():
    data = OccupancyService.get_monthly_occupancy()
    return jsonify({'items': data}), 200
