from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import date, timedelta
from app.extensions import db
from app.models.food_menu import FoodMenu
from app.utils.decorators import admin_required
from app.utils.helpers import parse_date, save_menu_image

menus_bp = Blueprint('menus', __name__)


@menus_bp.route('/', methods=['GET'])
@jwt_required()
def list_menus():
    menu_date = parse_date(request.args.get('date'))
    meal_type = request.args.get('meal_type')
    special_only = request.args.get('special', 'false').lower() == 'true'

    query = FoodMenu.query
    if menu_date:
        query = query.filter(FoodMenu.menu_date == menu_date)
    if meal_type:
        query = query.filter(FoodMenu.meal_type == meal_type)
    if special_only:
        query = query.filter(FoodMenu.is_special == True)

    menus = query.order_by(FoodMenu.menu_date.desc(), FoodMenu.meal_type).all()
    return jsonify({'items': [m.to_dict() for m in menus]}), 200


@menus_bp.route('/today', methods=['GET'])
@jwt_required()
def today_menu():
    today = date.today()
    menus = FoodMenu.query.filter_by(menu_date=today).order_by(FoodMenu.meal_type).all()
    return jsonify({'date': today.isoformat(), 'items': [m.to_dict() for m in menus]}), 200


@menus_bp.route('/weekly', methods=['GET'])
@jwt_required()
def weekly_menu():
    start = parse_date(request.args.get('start')) or date.today()
    end = start + timedelta(days=6)
    menus = FoodMenu.query.filter(
        FoodMenu.menu_date >= start,
        FoodMenu.menu_date <= end
    ).order_by(FoodMenu.menu_date, FoodMenu.meal_type).all()
    return jsonify({
        'start_date': start.isoformat(),
        'end_date': end.isoformat(),
        'items': [m.to_dict() for m in menus],
    }), 200


@menus_bp.route('/special', methods=['GET'])
@jwt_required()
def special_menus():
    menus = FoodMenu.query.filter_by(is_special=True).order_by(
        FoodMenu.menu_date.desc()
    ).limit(20).all()
    return jsonify({'items': [m.to_dict() for m in menus]}), 200


@menus_bp.route('/<int:menu_id>', methods=['GET'])
@jwt_required()
def get_menu(menu_id):
    menu = FoodMenu.query.get(menu_id)
    if not menu:
        return jsonify({'error': 'Menu not found'}), 404
    return jsonify(menu.to_dict()), 200


@menus_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_menu():
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form
        image_file = request.files.get('image')
    else:
        data = request.get_json() or {}
        image_file = None

    menu_date = parse_date(data.get('menu_date'))
    meal_type = data.get('meal_type')
    menu_title = data.get('menu_title')
    menu_items = data.get('menu_items')

    if not all([menu_date, meal_type, menu_title, menu_items]):
        return jsonify({'error': 'menu_date, meal_type, menu_title, menu_items are required'}), 400

    existing = FoodMenu.query.filter_by(menu_date=menu_date, meal_type=meal_type).first()
    if existing:
        return jsonify({'error': 'Menu already exists for this date and meal type'}), 409

    image_path = save_menu_image(image_file) if image_file else None

    menu = FoodMenu(
        menu_date=menu_date,
        meal_type=meal_type,
        menu_title=menu_title,
        menu_items=menu_items,
        is_special=data.get('is_special', 'false') in (True, 'true', '1'),
        description=data.get('description'),
        image_path=image_path,
    )
    db.session.add(menu)
    db.session.commit()
    return jsonify(menu.to_dict()), 201


@menus_bp.route('/<int:menu_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_menu(menu_id):
    menu = FoodMenu.query.get(menu_id)
    if not menu:
        return jsonify({'error': 'Menu not found'}), 404

    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form
        image_file = request.files.get('image')
    else:
        data = request.get_json() or {}
        image_file = None

    for field in ['menu_title', 'menu_items', 'description', 'meal_type']:
        if field in data:
            setattr(menu, field, data[field])
    if 'menu_date' in data:
        menu.menu_date = parse_date(data['menu_date'])
    if 'is_special' in data:
        menu.is_special = data['is_special'] in (True, 'true', '1')
    if image_file:
        menu.image_path = save_menu_image(image_file)

    db.session.commit()
    return jsonify(menu.to_dict()), 200


@menus_bp.route('/<int:menu_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_menu(menu_id):
    menu = FoodMenu.query.get(menu_id)
    if not menu:
        return jsonify({'error': 'Menu not found'}), 404

    db.session.delete(menu)
    db.session.commit()
    return jsonify({'message': 'Menu deleted successfully'}), 200
