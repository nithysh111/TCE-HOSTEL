from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from datetime import date, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.complaint import Complaint
from app.models.leave_request import LeaveRequest
from app.models.food_prediction import FoodPrediction
from app.models.food_wastage import FoodWastage
from app.services.occupancy_service import OccupancyService
from app.services.fee_service import FeeService
from app.utils.decorators import admin_required

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def dashboard_analytics():
    summary = OccupancyService.get_occupancy_summary()
    occupancy_trend = OccupancyService.get_occupancy_trend(30)

    open_complaints = Complaint.query.filter_by(status='Open').count()
    in_progress_complaints = Complaint.query.filter_by(status='In Progress').count()
    resolved_complaints = Complaint.query.filter_by(status='Resolved').count()

    pending_leaves = LeaveRequest.query.filter_by(status='pending').count()
    approved_leaves = LeaveRequest.query.filter_by(status='approved').count()

    today = date.today()
    today_prediction = FoodPrediction.query.filter_by(prediction_date=today).first()

    thirty_days_ago = today - timedelta(days=30)
    wastage_records = FoodWastage.query.filter(
        FoodWastage.report_date >= thirty_days_ago
    ).all()

    total_wasted = sum(r.wasted_quantity for r in wastage_records)
    total_prepared = sum(r.prepared_quantity for r in wastage_records)
    wastage_percentage = round((total_wasted / total_prepared * 100), 2) if total_prepared else 0

    complaint_by_category = db.session.query(
        Complaint.category, func.count(Complaint.id)
    ).group_by(Complaint.category).all()

    return jsonify({
        'occupancy': summary,
        'occupancy_trend': occupancy_trend,
        'complaints': {
            'open': open_complaints,
            'in_progress': in_progress_complaints,
            'resolved': resolved_complaints,
            'by_category': {cat: count for cat, count in complaint_by_category},
        },
        'leaves': {
            'pending': pending_leaves,
            'approved': approved_leaves,
        },
        'food_prediction': today_prediction.to_dict() if today_prediction else None,
        'wastage': {
            'total_wasted': total_wasted,
            'total_prepared': total_prepared,
            'wastage_percentage': wastage_percentage,
            'records': [r.to_dict() for r in wastage_records[-30:]],
        },
    }), 200


@analytics_bp.route('/complaints', methods=['GET'])
@jwt_required()
@admin_required
def complaint_analytics():
    by_status = db.session.query(
        Complaint.status, func.count(Complaint.id)
    ).group_by(Complaint.status).all()

    by_category = db.session.query(
        Complaint.category, func.count(Complaint.id)
    ).group_by(Complaint.category).all()

    return jsonify({
        'by_status': {s: c for s, c in by_status},
        'by_category': {cat: c for cat, c in by_category},
    }), 200


@analytics_bp.route('/leave', methods=['GET'])
@jwt_required()
@admin_required
def leave_analytics():
    by_status = db.session.query(
        LeaveRequest.status, func.count(LeaveRequest.id)
    ).group_by(LeaveRequest.status).all()

    by_type = db.session.query(
        LeaveRequest.leave_type, func.count(LeaveRequest.id)
    ).group_by(LeaveRequest.leave_type).all()

    return jsonify({
        'by_status': {s: c for s, c in by_status},
        'by_type': {t: c for t, c in by_type},
    }), 200


@analytics_bp.route('/fees-fines', methods=['GET'])
@jwt_required()
@admin_required
def fees_fines_analytics():
    return jsonify(FeeService.get_admin_analytics()), 200
