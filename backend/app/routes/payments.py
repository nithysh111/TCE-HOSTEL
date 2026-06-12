from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.payment import Payment
from app.models.hostel_fee import HostelFee
from app.models.fine import Fine
from app.models.student import Student
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.helpers import generate_payment_id, get_current_user_id
from app.services.razorpay_service import RazorpayService
from app.services.notification_service import NotificationService

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/', methods=['GET'])
@jwt_required()
def list_payments():
    user = User.query.get(get_current_user_id())
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Payment.query
    if user.role == 'student':
        query = query.filter_by(roll_no=user.roll_no)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'items': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    }), 200


@payments_bp.route('/config', methods=['GET'])
@jwt_required()
def razorpay_config():
    return jsonify({'key_id': current_app.config['RAZORPAY_KEY_ID']}), 200


@payments_bp.route('/create-order', methods=['POST'])
@jwt_required()
def create_order():
    user = User.query.get(get_current_user_id())
    if user.role != 'student' or not user.roll_no:
        return jsonify({'error': 'Only students can initiate payments'}), 403

    data = request.get_json()
    fee_id = data.get('fee_id')
    fine_id = data.get('fine_id')

    if not fee_id and not fine_id:
        return jsonify({'error': 'fee_id or fine_id is required'}), 400
    if fee_id and fine_id:
        return jsonify({'error': 'Provide either fee_id or fine_id, not both'}), 400

    amount = None
    fee_db_id = None
    fine_db_id = None
    receipt_ref = ''

    if fee_id:
        fee = HostelFee.query.filter_by(fee_id=fee_id, roll_no=user.roll_no).first()
        if not fee:
            return jsonify({'error': 'Fee not found'}), 404
        if fee.status == 'Paid':
            return jsonify({'error': 'Fee already paid'}), 400
        amount = float(fee.fee_amount)
        fee_db_id = fee.id
        receipt_ref = fee.fee_id
    else:
        fine = Fine.query.filter_by(fine_id=fine_id, roll_no=user.roll_no).first()
        if not fine:
            return jsonify({'error': 'Fine not found'}), 404
        if fine.status == 'Paid':
            return jsonify({'error': 'Fine already paid'}), 400
        amount = float(fine.fine_amount)
        fine_db_id = fine.id
        receipt_ref = fine.fine_id

    payment_id = generate_payment_id()
    amount_paise = int(round(amount * 100))

    try:
        order = RazorpayService.create_order(
            amount_paise,
            receipt=payment_id,
            notes={'roll_no': user.roll_no, 'ref': receipt_ref},
        )
    except Exception as e:
        return jsonify({'error': f'Failed to create Razorpay order: {str(e)}'}), 500

    payment = Payment(
        payment_id=payment_id,
        roll_no=user.roll_no,
        fee_id=fee_db_id,
        fine_id=fine_db_id,
        razorpay_order_id=order['id'],
        amount=amount,
        status='Pending',
    )
    db.session.add(payment)
    db.session.commit()

    student = Student.query.filter_by(roll_no=user.roll_no).first()
    return jsonify({
        'order_id': order['id'],
        'amount': amount,
        'amount_paise': amount_paise,
        'currency': 'INR',
        'payment_id': payment.payment_id,
        'key_id': current_app.config['RAZORPAY_KEY_ID'],
        'prefill': {
            'name': student.name if student else '',
            'email': user.email,
        },
    }), 201


@payments_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    user = User.query.get(get_current_user_id())
    data = request.get_json()
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return jsonify({'error': 'Missing payment verification fields'}), 400

    payment = Payment.query.filter_by(razorpay_order_id=razorpay_order_id).first()
    if not payment:
        return jsonify({'error': 'Payment record not found'}), 404
    if user.role == 'student' and payment.roll_no != user.roll_no:
        return jsonify({'error': 'Access denied'}), 403

    if RazorpayService.verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        payment.status = 'Success'
        payment.razorpay_payment_id = razorpay_payment_id
        payment.transaction_date = datetime.utcnow()

        if payment.fee_id:
            fee = HostelFee.query.get(payment.fee_id)
            if fee:
                fee.status = 'Paid'
                NotificationService.notify_fee_paid(fee)
        if payment.fine_id:
            fine = Fine.query.get(payment.fine_id)
            if fine:
                fine.status = 'Paid'
                NotificationService.notify_fine_paid(fine)

        db.session.commit()
        return jsonify({
            'message': 'Payment verified successfully',
            'payment': payment.to_dict(),
        }), 200

    payment.status = 'Failed'
    db.session.commit()
    return jsonify({'error': 'Payment verification failed'}), 400


@payments_bp.route('/<payment_id>/receipt', methods=['GET'])
@jwt_required()
def get_receipt(payment_id):
    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    user = User.query.get(get_current_user_id())
    if user.role == 'student' and payment.roll_no != user.roll_no:
        return jsonify({'error': 'Access denied'}), 403
    if payment.status != 'Success':
        return jsonify({'error': 'Receipt available only for successful payments'}), 400

    student = Student.query.filter_by(roll_no=payment.roll_no).first()
    fee_ref = payment.fee.fee_id if payment.fee else None
    fine_ref = payment.fine.fine_id if payment.fine else None

    return jsonify({
        'receipt_id': payment.payment_id,
        'student_name': student.name if student else '',
        'roll_no': payment.roll_no,
        'amount': float(payment.amount),
        'status': payment.status,
        'transaction_date': payment.transaction_date.isoformat() if payment.transaction_date else None,
        'razorpay_payment_id': payment.razorpay_payment_id,
        'razorpay_order_id': payment.razorpay_order_id,
        'fee_id': fee_ref,
        'fine_id': fine_ref,
        'payment_for': 'Hostel Fee' if fee_ref else 'Fine',
    }), 200
