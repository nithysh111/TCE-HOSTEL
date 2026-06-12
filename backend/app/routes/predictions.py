import sys
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import date
from app.extensions import db
from app.models.food_prediction import FoodPrediction
from app.models.food_wastage import FoodWastage
from app.services.occupancy_service import OccupancyService
from app.utils.decorators import admin_required
from app.utils.helpers import parse_date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ml'))
from prediction_service import FoodPredictionService

predictions_bp = Blueprint('predictions', __name__)
prediction_service = FoodPredictionService()


@predictions_bp.route('/food', methods=['GET'])
@jwt_required()
@admin_required
def get_food_prediction():
    target_date = parse_date(request.args.get('date')) or date.today()
    is_holiday = request.args.get('is_holiday', 'false').lower() == 'true'

    summary = OccupancyService.get_occupancy_summary(target_date)
    is_weekend = target_date.weekday() >= 5

    predictions = prediction_service.predict(
        total_students=summary['total_students'],
        students_inside=summary['students_inside'],
        students_outside=summary['students_outside'],
        leave_requests=summary['students_on_leave'],
        is_weekend=is_weekend,
        is_holiday=is_holiday,
    )

    existing = FoodPrediction.query.filter_by(prediction_date=target_date).first()
    if existing:
        existing.predicted_breakfast = predictions['predicted_breakfast']
        existing.predicted_lunch = predictions['predicted_lunch']
        existing.predicted_dinner = predictions['predicted_dinner']
        existing.total_students = summary['total_students']
        existing.students_inside = summary['students_inside']
        existing.students_outside = summary['students_outside']
        existing.students_on_leave = summary['students_on_leave']
        existing.is_weekend = is_weekend
        existing.is_holiday = is_holiday
        record = existing
    else:
        record = FoodPrediction(
            prediction_date=target_date,
            predicted_breakfast=predictions['predicted_breakfast'],
            predicted_lunch=predictions['predicted_lunch'],
            predicted_dinner=predictions['predicted_dinner'],
            total_students=summary['total_students'],
            students_inside=summary['students_inside'],
            students_outside=summary['students_outside'],
            students_on_leave=summary['students_on_leave'],
            is_weekend=is_weekend,
            is_holiday=is_holiday,
        )
        db.session.add(record)

    db.session.commit()

    result = record.to_dict()
    result['occupancy'] = summary
    result['model_loaded'] = prediction_service.is_loaded
    if prediction_service.is_loaded:
        result['model_metrics'] = prediction_service.get_metrics()
    return jsonify(result), 200


@predictions_bp.route('/food/history', methods=['GET'])
@jwt_required()
@admin_required
def food_prediction_history():
    days = request.args.get('days', 30, type=int)
    from datetime import timedelta
    start_date = date.today() - timedelta(days=days)

    predictions = FoodPrediction.query.filter(
        FoodPrediction.prediction_date >= start_date
    ).order_by(FoodPrediction.prediction_date).all()

    return jsonify({'items': [p.to_dict() for p in predictions]}), 200


@predictions_bp.route('/wastage', methods=['GET'])
@jwt_required()
@admin_required
def list_wastage():
    report_date = parse_date(request.args.get('date'))
    query = FoodWastage.query
    if report_date:
        query = query.filter_by(report_date=report_date)

    records = query.order_by(FoodWastage.report_date.desc()).limit(90).all()
    return jsonify({'items': [r.to_dict() for r in records]}), 200


@predictions_bp.route('/wastage', methods=['POST'])
@jwt_required()
@admin_required
def create_wastage():
    data = request.get_json()
    report_date = parse_date(data.get('report_date'))
    meal_type = data.get('meal_type')
    prepared = data.get('prepared_quantity')
    consumed = data.get('consumed_quantity')

    if not all([report_date, meal_type, prepared is not None, consumed is not None]):
        return jsonify({'error': 'report_date, meal_type, prepared_quantity, consumed_quantity required'}), 400

    wasted = max(0, int(prepared) - int(consumed))

    existing = FoodWastage.query.filter_by(report_date=report_date, meal_type=meal_type).first()
    if existing:
        existing.prepared_quantity = int(prepared)
        existing.consumed_quantity = int(consumed)
        existing.wasted_quantity = wasted
        existing.notes = data.get('notes')
        record = existing
    else:
        record = FoodWastage(
            report_date=report_date,
            meal_type=meal_type,
            prepared_quantity=int(prepared),
            consumed_quantity=int(consumed),
            wasted_quantity=wasted,
            notes=data.get('notes'),
        )
        db.session.add(record)

    db.session.commit()
    return jsonify(record.to_dict()), 201
