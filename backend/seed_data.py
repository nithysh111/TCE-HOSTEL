"""Seed script for demo data."""

from datetime import date, datetime, timedelta
import random
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.food_menu import FoodMenu
from app.models.announcement import Announcement
from app.models.leave_request import LeaveRequest
from app.models.hostel_fee import HostelFee
from app.models.fine import Fine
from app.utils.helpers import generate_fee_id, generate_fine_id

DEPARTMENTS = ['CSE', 'ECE', 'MECH', 'CIVIL', 'EEE', 'IT']
BLOCKS = ['Block A', 'Block B', 'Block C']
GENDERS = ['Male', 'Female']
MEAL_TYPES = ['Breakfast', 'Lunch', 'Dinner']

BREAKFAST_ITEMS = ['Idli, Sambar, Chutney', 'Dosa, Sambar', 'Poha, Tea', 'Bread, Butter, Jam, Tea']
LUNCH_ITEMS = ['Rice, Dal, Sabzi, Roti', 'Biryani, Raita', 'Rice, Rajma, Roti', 'Rice, Sambar, Poriyal']
DINNER_ITEMS = ['Rice, Dal, Roti', 'Chapati, Curry', 'Rice, Rasam, Veg Curry', 'Fried Rice, Soup']


def seed():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@hostel.edu').first()
        if not admin:
            admin = User(email='admin@hostel.edu', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)

        if Student.query.count() > 0:
            print('Data already seeded. Skipping.')
            return

        students = []
        for i in range(1, 51):
            roll = f'CS{i:03d}'
            user = User(email=f'{roll.lower()}@student.edu', roll_no=roll, role='student')
            user.set_password('student123')
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id,
                roll_no=roll,
                name=f'Student {i}',
                department=random.choice(DEPARTMENTS),
                year=random.randint(1, 4),
                gender=random.choice(GENDERS),
                phone_number=f'98765{str(i).zfill(5)}',
                parent_contact=f'98760{str(i).zfill(5)}',
                room_number=f'{random.randint(101, 420)}',
                hostel_block=random.choice(BLOCKS),
            )
            db.session.add(student)
            students.append(student)

        db.session.flush()
        today = date.today()

        for student in students:
            status = random.choice(['inside', 'outside', 'outside', 'inside'])
            entry = datetime.combine(today, datetime.min.time().replace(hour=random.randint(6, 9)))
            exit_t = None
            if status == 'outside':
                exit_t = datetime.combine(today, datetime.min.time().replace(hour=random.randint(8, 17)))

            att = Attendance(
                roll_no=student.roll_no,
                entry_time=entry,
                exit_time=exit_t,
                attendance_date=today,
                status=status,
            )
            db.session.add(att)

        for i in range(3):
            lr = LeaveRequest(
                roll_no=students[i].roll_no,
                start_date=today,
                end_date=today + timedelta(days=random.randint(1, 5)),
                reason='Family function',
                status='approved',
            )
            db.session.add(lr)

        for day_offset in range(7):
            menu_date = today + timedelta(days=day_offset)
            for meal_idx, meal_type in enumerate(MEAL_TYPES):
                items = [BREAKFAST_ITEMS, LUNCH_ITEMS, DINNER_ITEMS][meal_idx]
                menu = FoodMenu(
                    menu_date=menu_date,
                    meal_type=meal_type,
                    menu_title=f'{meal_type} Menu',
                    menu_items=random.choice(items),
                    is_special=day_offset == 6 and meal_type == 'Lunch',
                    description='Special festival lunch' if day_offset == 6 and meal_type == 'Lunch' else None,
                )
                db.session.add(menu)

        announcements = [
            Announcement(title='Hostel Timings Update', description='Hostel gates close at 10 PM on weekdays.', priority='high'),
            Announcement(title='Mess Menu Survey', description='Please fill the food preference survey by Friday.', priority='medium'),
            Announcement(title='Maintenance Notice', description='Water supply interruption on Sunday 8 AM - 12 PM.', priority='low', expiry_date=today + timedelta(days=7)),
        ]
        for a in announcements:
            db.session.add(a)

        for student in students[:10]:
            fee = HostelFee(
                fee_id=generate_fee_id(),
                roll_no=student.roll_no,
                academic_year='2025-2026',
                hostel_block=student.hostel_block,
                room_number=student.room_number,
                fee_amount=25000,
                due_date=today + timedelta(days=random.randint(7, 60)),
                status='Pending',
            )
            db.session.add(fee)

        for student in students[10:13]:
            fine = Fine(
                fine_id=generate_fine_id(),
                roll_no=student.roll_no,
                student_name=student.name,
                fine_amount=random.choice([500, 1000, 1500]),
                fine_reason=random.choice(['Late Hostel Entry', 'Mess Rule Violation']),
                fine_description='Demo fine for testing',
                issued_date=today,
                due_date=today + timedelta(days=random.randint(7, 30)),
                status='Pending',
                created_by='admin@hostel.edu',
            )
            db.session.add(fine)

        db.session.commit()
        print('Seed data created: 50 students, attendance, menus, announcements, leave requests, fees, fines')
        print('Admin: admin@hostel.edu / admin123')
        print('Student: cs001@student.edu / student123')


if __name__ == '__main__':
    seed()
