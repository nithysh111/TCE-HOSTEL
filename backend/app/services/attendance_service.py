import csv
import io
from datetime import datetime
from app.extensions import db
from app.models.attendance import Attendance
from app.utils.helpers import parse_date


class AttendanceService:

    @staticmethod
    def import_from_csv(file_content):
        reader = csv.DictReader(io.StringIO(file_content))
        imported = 0
        errors = []

        for row_num, row in enumerate(reader, start=2):
            try:
                roll_no = row.get('roll_no', '').strip()
                if not roll_no:
                    errors.append(f'Row {row_num}: Missing roll_no')
                    continue

                attendance_date = parse_date(row.get('attendance_date', '').strip())
                if not attendance_date:
                    errors.append(f'Row {row_num}: Invalid attendance_date')
                    continue

                entry_time = None
                exit_time = None
                if row.get('entry_time'):
                    entry_time = datetime.fromisoformat(row['entry_time'].strip())
                if row.get('exit_time'):
                    exit_time = datetime.fromisoformat(row['exit_time'].strip())

                status = row.get('status', 'outside').strip().lower()
                if status not in ('inside', 'outside', 'on_leave'):
                    status = 'inside' if entry_time and not exit_time else 'outside'

                record = Attendance(
                    roll_no=roll_no,
                    entry_time=entry_time,
                    exit_time=exit_time,
                    attendance_date=attendance_date,
                    status=status,
                )
                db.session.add(record)
                imported += 1
            except Exception as e:
                errors.append(f'Row {row_num}: {str(e)}')

        db.session.commit()
        return {'imported': imported, 'errors': errors}

    @staticmethod
    def import_from_api(data_list):
        imported = 0
        errors = []

        for idx, item in enumerate(data_list):
            try:
                roll_no = item.get('roll_no', '').strip()
                attendance_date = parse_date(item.get('attendance_date'))
                if not roll_no or not attendance_date:
                    errors.append(f'Record {idx}: Missing required fields')
                    continue

                entry_time = None
                exit_time = None
                if item.get('entry_time'):
                    entry_time = datetime.fromisoformat(item['entry_time'])
                if item.get('exit_time'):
                    exit_time = datetime.fromisoformat(item['exit_time'])

                status = item.get('status', 'outside')
                record = Attendance(
                    roll_no=roll_no,
                    entry_time=entry_time,
                    exit_time=exit_time,
                    attendance_date=attendance_date,
                    status=status,
                )
                db.session.add(record)
                imported += 1
            except Exception as e:
                errors.append(f'Record {idx}: {str(e)}')

        db.session.commit()
        return {'imported': imported, 'errors': errors}

    @staticmethod
    def get_attendance_logs(roll_no=None, attendance_date=None, page=1, per_page=50):
        query = Attendance.query
        if roll_no:
            query = query.filter(Attendance.roll_no == roll_no)
        if attendance_date:
            query = query.filter(Attendance.attendance_date == parse_date(attendance_date))

        pagination = query.order_by(Attendance.attendance_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return {
            'items': [a.to_dict() for a in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
        }
