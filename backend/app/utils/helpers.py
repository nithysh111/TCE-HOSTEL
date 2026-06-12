import os
import uuid
from datetime import date, datetime
from werkzeug.utils import secure_filename
from flask import current_app
from flask_jwt_extended import get_jwt_identity


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_menu_image(file):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return f"/uploads/menus/{filename}"
    return None


def generate_complaint_id():
    return f"CMP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def generate_fee_id():
    return f"FEE-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def generate_fine_id():
    return f"FIN-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def generate_payment_id():
    return f"PAY-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def get_current_user_id():
    """JWT identity is stored as string; convert back to int for DB lookups."""
    return int(get_jwt_identity())


def parse_date(date_str):
    if isinstance(date_str, date):
        return date_str
    if isinstance(date_str, str):
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    return None
