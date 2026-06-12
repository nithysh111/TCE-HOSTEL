import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from app.config import Config
from app.extensions import db, jwt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={r'/api/*': {'origins': '*'}})

    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.students import students_bp
    from app.routes.attendance import attendance_bp
    from app.routes.occupancy import occupancy_bp
    from app.routes.menus import menus_bp
    from app.routes.complaints import complaints_bp
    from app.routes.announcements import announcements_bp
    from app.routes.leave import leave_bp
    from app.routes.predictions import predictions_bp
    from app.routes.analytics import analytics_bp
    from app.routes.fees import fees_bp
    from app.routes.fines import fines_bp
    from app.routes.payments import payments_bp
    from app.routes.notifications import notifications_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(occupancy_bp, url_prefix='/api/occupancy')
    app.register_blueprint(menus_bp, url_prefix='/api/menus')
    app.register_blueprint(complaints_bp, url_prefix='/api/complaints')
    app.register_blueprint(announcements_bp, url_prefix='/api/announcements')
    app.register_blueprint(leave_bp, url_prefix='/api/leave')
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(fees_bp, url_prefix='/api/fees')
    app.register_blueprint(fines_bp, url_prefix='/api/fines')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    @app.route('/uploads/menus/<filename>')
    def serve_menu_image(filename):
        return send_from_directory(upload_folder, filename)

    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'service': 'Hostel Food Intelligence API'}, 200

    with app.app_context():
        db.create_all()

    return app
