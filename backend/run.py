from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()


def seed_admin():
    with app.app_context():
        admin = User.query.filter_by(email='admin@hostel.edu').first()
        if not admin:
            admin = User(email='admin@hostel.edu', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Default admin created: admin@hostel.edu / admin123')


if __name__ == '__main__':
    seed_admin()
    app.run(host='0.0.0.0', port=5000, debug=True)
