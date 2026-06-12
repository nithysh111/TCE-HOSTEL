from datetime import date, timedelta
from app.extensions import db
from app.models.notification import Notification
from app.models.hostel_fee import HostelFee
from app.models.fine import Fine


class NotificationService:
    REMINDER_DAYS = [30, 15, 7, 1]

    @staticmethod
    def create(roll_no, title, message, notification_type):
        notification = Notification(
            roll_no=roll_no,
            title=title,
            message=message,
            notification_type=notification_type,
        )
        db.session.add(notification)
        return notification

    @staticmethod
    def _exists_today(roll_no, title):
        today = date.today()
        return Notification.query.filter(
            Notification.roll_no == roll_no,
            Notification.title == title,
            db.func.date(Notification.created_at) == today,
        ).first() is not None

    @staticmethod
    def notify_fee_created(fee):
        NotificationService.create(
            fee.roll_no,
            'Hostel Fee Assigned',
            f'Hostel fee of ₹{float(fee.fee_amount):,.2f} for {fee.academic_year} '
            f'is due on {fee.due_date.isoformat()}.',
            'Fee',
        )

    @staticmethod
    def notify_fine_created(fine):
        NotificationService.create(
            fine.roll_no,
            'New Fine Assigned',
            f'A fine of ₹{float(fine.fine_amount):,.2f} has been issued for: {fine.fine_reason}.',
            'Fine',
        )

    @staticmethod
    def notify_fine_paid(fine):
        NotificationService.create(
            fine.roll_no,
            'Fine Payment Success',
            f'Your fine {fine.fine_id} of ₹{float(fine.fine_amount):,.2f} has been paid successfully.',
            'Fine',
        )

    @staticmethod
    def notify_fee_paid(fee):
        NotificationService.create(
            fee.roll_no,
            'Fee Payment Success',
            f'Your hostel fee {fee.fee_id} of ₹{float(fee.fee_amount):,.2f} has been paid successfully.',
            'Fee',
        )

    @staticmethod
    def process_fee_reminders():
        today = date.today()
        fees = HostelFee.query.filter(HostelFee.status.in_(['Pending', 'Overdue'])).all()
        for fee in fees:
            fee.refresh_status()
            days_left = (fee.due_date - today).days
            if days_left == 1:
                title = 'Fee Due Tomorrow'
                if not NotificationService._exists_today(fee.roll_no, title):
                    NotificationService.create(
                        fee.roll_no, title,
                        f'Hostel fee {fee.fee_id} is due tomorrow.',
                        'Fee',
                    )
            elif days_left in NotificationService.REMINDER_DAYS:
                title = f'Fee Due in {days_left} Days'
                if not NotificationService._exists_today(fee.roll_no, title):
                    NotificationService.create(
                        fee.roll_no, title,
                        f'Hostel fee {fee.fee_id} of ₹{float(fee.fee_amount):,.2f} '
                        f'is due on {fee.due_date.isoformat()}.',
                        'Fee',
                    )
            elif days_left < 0 and fee.status == 'Overdue':
                title = 'Fee Overdue'
                if not NotificationService._exists_today(fee.roll_no, title):
                    NotificationService.create(
                        fee.roll_no, title,
                        f'Hostel fee {fee.fee_id} is overdue. Please pay immediately.',
                        'Fee',
                    )

    @staticmethod
    def process_fine_reminders():
        today = date.today()
        fines = Fine.query.filter(Fine.status.in_(['Pending', 'Overdue'])).all()
        for fine in fines:
            fine.refresh_status()
            days_left = (fine.due_date - today).days
            if days_left in NotificationService.REMINDER_DAYS + [0]:
                title = 'Fine Due Reminder'
                if not NotificationService._exists_today(fine.roll_no, title):
                    NotificationService.create(
                        fine.roll_no, title,
                        f'Fine {fine.fine_id} of ₹{float(fine.fine_amount):,.2f} '
                        f'is due on {fine.due_date.isoformat()}.',
                        'Fine',
                    )
            elif days_left < 0 and fine.status == 'Overdue':
                title = 'Fine Overdue Reminder'
                if not NotificationService._exists_today(fine.roll_no, title):
                    NotificationService.create(
                        fine.roll_no, title,
                        f'Fine {fine.fine_id} is overdue. Please pay immediately.',
                        'Fine',
                    )

    @staticmethod
    def run_reminder_checks():
        NotificationService.process_fee_reminders()
        NotificationService.process_fine_reminders()
        db.session.commit()
