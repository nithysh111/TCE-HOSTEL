import { Link } from 'react-router-dom';

export default function PaymentFailure() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="card text-center max-w-md w-full">
        <div className="text-6xl mb-4">❌</div>
        <h1 className="text-2xl font-bold text-red-600 mb-2">Payment Failed</h1>
        <p className="text-gray-500 mb-6">
          Your payment could not be processed. Please try again or contact the hostel office.
        </p>
        <div className="flex gap-3 justify-center">
          <Link to="/student/fees" className="btn-primary">Try Again</Link>
          <Link to="/student/payments" className="btn-secondary">Payment History</Link>
        </div>
      </div>
    </div>
  );
}
