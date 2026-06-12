import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
_default_db = f'sqlite:///{os.path.join(BASE_DIR, "hostel_food.db")}'


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', _default_db)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {'pool_pre_ping': True}
        if 'mysql' in os.getenv('DATABASE_URL', '')
        else {}
    )

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'menus')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    ML_MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'food_prediction_model.joblib')

    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_T0gIlM2rKZMBbE')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'GCqCCN2sfXoqAdcMOtMhvXiE')
