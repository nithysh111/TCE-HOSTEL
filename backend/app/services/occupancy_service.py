from datetime import date, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.leave_request import LeaveRequest


class OccupancyService:

    @staticmethod
    def get_students_on_leave(target_date=None):
        target_date = target_date or date.today()
        leave_records = LeaveRequest.query.filter(
            LeaveRequest.status == 'approved',
            LeaveRequest.start_date <= target_date,
            LeaveRequest.end_date >= target_date
        ).all()
        return {lr.roll_no for lr in leave_records}

    @staticmethod
    def get_occupancy_summary(target_date=None):
        target_date = target_date or date.today()
        total_students = Student.query.count()
        on_leave_roll_nos = OccupancyService.get_students_on_leave(target_date)

        latest_attendance = db.session.query(
            Attendance.roll_no,
            func.max(Attendance.id).label('max_id')
        ).filter(
            Attendance.attendance_date == target_date
        ).group_by(Attendance.roll_no).subquery()

        inside_records = db.session.query(Attendance).join(
            latest_attendance,
            (Attendance.id == latest_attendance.c.max_id) &
            (Attendance.roll_no == latest_attendance.c.roll_no)
        ).filter(Attendance.status == 'inside').all()

        inside_roll_nos = {a.roll_no for a in inside_records}
        inside_roll_nos -= on_leave_roll_nos

        students_on_leave = len(on_leave_roll_nos)
        students_inside = len(inside_roll_nos)
        students_outside = max(0, total_students - students_inside - students_on_leave)

        return {
            'date': target_date.isoformat(),
            'total_students': total_students,
            'students_inside': students_inside,
            'students_outside': students_outside,
            'students_on_leave': students_on_leave,
        }

    @staticmethod
    def get_students_by_status(status, target_date=None):
        target_date = target_date or date.today()
        on_leave_roll_nos = OccupancyService.get_students_on_leave(target_date)

        if status == 'on_leave':
            students = Student.query.filter(Student.roll_no.in_(on_leave_roll_nos)).all()
            return [s.to_dict(include_occupancy=True, occupancy_status='on_leave') for s in students]

        latest_attendance = db.session.query(
            Attendance.roll_no,
            func.max(Attendance.id).label('max_id')
        ).filter(
            Attendance.attendance_date == target_date
        ).group_by(Attendance.roll_no).subquery()

        attendance_records = db.session.query(Attendance).join(
            latest_attendance,
            (Attendance.id == latest_attendance.c.max_id) &
            (Attendance.roll_no == latest_attendance.c.roll_no)
        ).all()

        status_map = {a.roll_no: a.status for a in attendance_records}

        all_students = Student.query.all()
        result = []
        for student in all_students:
            if student.roll_no in on_leave_roll_nos:
                occ_status = 'on_leave'
            else:
                occ_status = status_map.get(student.roll_no, 'outside')

            if occ_status == status:
                result.append(student.to_dict(include_occupancy=True, occupancy_status=occ_status))

        return result

    @staticmethod
    def get_occupancy_trend(days=30):
        target_date = date.today()
        trend = []
        for i in range(days - 1, -1, -1):
            d = target_date - timedelta(days=i)
            summary = OccupancyService.get_occupancy_summary(d)
            trend.append({
                'date': d.isoformat(),
                'inside': summary['students_inside'],
                'outside': summary['students_outside'],
                'on_leave': summary['students_on_leave'],
                'total': summary['total_students'],
            })
        return trend

    @staticmethod
    def get_weekly_occupancy():
        return OccupancyService.get_occupancy_trend(days=7)

    @staticmethod
    def get_monthly_occupancy():
        return OccupancyService.get_occupancy_trend(days=30)
