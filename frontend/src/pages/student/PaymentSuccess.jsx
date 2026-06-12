import { Link, useLocation } from 'react-router-dom';

export default function PaymentSuccess() {
  const location = useLocation();
  const paymentId = location.state?.paymentId;

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="card text-center max-w-md w-full">
        <div className="text-6xl mb-4">✅</div>
        <h1 className="text-2xl font-bold text-green-600 mb-2">Payment Successful</h1>
        <p className="text-gray-500 mb-6">
          Your payment has been processed successfully.
          {paymentId && <span className="block mt-2 font-mono text-sm">Ref: {paymentId}</span>}
        </p>
        <div className="flex gap-3 justify-center">
          <Link to="/student/payments" className="btn-primary">View Payment History</Link>
          <Link to="/student/fees" className="btn-secondary">Back to Fees</Link>
        </div>
      </div>
    </div>
  );
}
