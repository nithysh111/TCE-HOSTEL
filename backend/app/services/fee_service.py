from datetime import date
from sqlalchemy import func
from app.extensions import db
from app.models.hostel_fee import HostelFee
from app.models.fine import Fine
from app.models.payment import Payment
from app.models.student import Student


class FeeService:
    @staticmethod
    def refresh_all_statuses():
        for fee in HostelFee.query.filter(HostelFee.status != 'Paid').all():
            fee.refresh_status()
        for fine in Fine.query.filter(Fine.status != 'Paid').all():
            fine.refresh_status()
        db.session.commit()

    @staticmethod
    def get_student_summary(roll_no):
        FeeService.refresh_all_statuses()
        fees = HostelFee.query.filter_by(roll_no=roll_no).all()
        fines = Fine.query.filter_by(roll_no=roll_no).all()

        total_fee = sum(float(f.fee_amount) for f in fees)
        pending_fee = sum(float(f.fee_amount) for f in fees if f.status in ('Pending', 'Overdue'))
        total_fine = sum(float(f.fine_amount) for f in fines)
        pending_fine = sum(float(f.fine_amount) for f in fines if f.status in ('Pending', 'Overdue'))

        return {
            'total_hostel_fee': total_fee,
            'pending_fee': pending_fee,
            'total_fine_amount': total_fine,
            'pending_fine_amount': pending_fine,
        }

    @staticmethod
    def get_admin_analytics():
        FeeService.refresh_all_statuses()
        today = date.today()

        fees_collected = db.session.query(
            func.coalesce(func.sum(HostelFee.fee_amount), 0)
        ).filter(HostelFee.status == 'Paid').scalar()

        fees_pending = db.session.query(
            func.coalesce(func.sum(HostelFee.fee_amount), 0)
        ).filter(HostelFee.status.in_(['Pending', 'Overdue'])).scalar()

        fines_total = db.session.query(
            func.coalesce(func.sum(Fine.fine_amount), 0)
        ).scalar()

        fines_collected = db.session.query(
            func.coalesce(func.sum(Fine.fine_amount), 0)
        ).filter(Fine.status == 'Paid').scalar()

        overdue_fees = HostelFee.query.filter_by(status='Overdue').count()
        overdue_fines = Fine.query.filter_by(status='Overdue').count()

        six_months_ago = today.replace(day=1)
        from datetime import timedelta
        months = []
        for i in range(5, -1, -1):
            m = today.month - i
            y = today.year
            while m <= 0:
                m += 12
                y -= 1
            months.append((y, m))

        monthly_fee = []
        monthly_fine = []
        for y, m in months:
            fee_sum = db.session.query(
                func.coalesce(func.sum(Payment.amount), 0)
            ).filter(
                Payment.status == 'Success',
                Payment.fee_id.isnot(None),
                func.extract('year', Payment.transaction_date) == y,
                func.extract('month', Payment.transaction_date) == m,
            ).scalar()
            fine_sum = db.session.query(
                func.coalesce(func.sum(Payment.amount), 0)
            ).filter(
                Payment.status == 'Success',
                Payment.fine_id.isnot(None),
                func.extract('year', Payment.transaction_date) == y,
                func.extract('month', Payment.transaction_date) == m,
            ).scalar()
            monthly_fee.append({'month': f'{y}-{m:02d}', 'amount': float(fee_sum or 0)})
            monthly_fine.append({'month': f'{y}-{m:02d}', 'amount': float(fine_sum or 0)})

        pending_trend = []
        for i in range(5, -1, -1):
            d = today - timedelta(days=i * 7)
            pending_count = HostelFee.query.filter(
                HostelFee.status.in_(['Pending', 'Overdue']),
                HostelFee.created_at <= d,
            ).count() + Fine.query.filter(
                Fine.status.in_(['Pending', 'Overdue']),
                Fine.created_at <= d,
            ).count()
            pending_trend.append({'date': d.isoformat(), 'count': pending_count})

        revenue = [
            {'label': 'Fees Collected', 'amount': float(fees_collected or 0)},
            {'label': 'Fines Collected', 'amount': float(fines_collected or 0)},
            {'label': 'Fees Pending', 'amount': float(fees_pending or 0)},
            {'label': 'Fines Pending', 'amount': float(fines_total or 0) - float(fines_collected or 0)},
        ]

        return {
            'total_fees_collected': float(fees_collected or 0),
            'total_pending_fees': float(fees_pending or 0),
            'total_fine_amount': float(fines_total or 0),
            'total_fine_collected': float(fines_collected or 0),
            'overdue_fees': overdue_fees,
            'overdue_fines': overdue_fines,
            'monthly_fee_collection': monthly_fee,
            'monthly_fine_collection': monthly_fine,
            'pending_payments_trend': pending_trend,
            'revenue_analytics': revenue,
        }

    @staticmethod
    def enrich_fee(fee):
        student = Student.query.filter_by(roll_no=fee.roll_no).first()
        return fee.to_dict(student_name=student.name if student else None)
