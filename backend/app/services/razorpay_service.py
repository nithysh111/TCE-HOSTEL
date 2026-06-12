import razorpay
from flask import current_app


class RazorpayService:
    @staticmethod
    def get_client():
        return razorpay.Client(
            auth=(
                current_app.config['RAZORPAY_KEY_ID'],
                current_app.config['RAZORPAY_KEY_SECRET'],
            )
        )

    @staticmethod
    def create_order(amount_paise, receipt, notes=None):
        client = RazorpayService.get_client()
        order_data = {
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': receipt,
            'payment_capture': 1,
        }
        if notes:
            order_data['notes'] = notes
        return client.order.create(data=order_data)

    @staticmethod
    def verify_payment(order_id, payment_id, signature):
        client = RazorpayService.get_client()
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            })
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
