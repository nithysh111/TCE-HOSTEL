import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { feesAPI, finesAPI, paymentsAPI } from '../../services/api';
import { openRazorpayCheckout } from '../../utils/razorpay';
import StatCard from '../../components/StatCard';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function StudentFees() {
  const navigate = useNavigate();
  const [fees, setFees] = useState([]);
  const [fines, setFines] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paying, setPaying] = useState(null);
  const [error, setError] = useState('');

  const fetchData = () => {
    Promise.all([feesAPI.list(), finesAPI.list(), feesAPI.summary()])
      .then(([feesRes, finesRes, summaryRes]) => {
        setFees(feesRes.data.items);
        setFines(finesRes.data.items);
        setSummary(summaryRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handlePay = async (type, refId) => {
    setPaying(refId);
    setError('');
    try {
      const payload = type === 'fee' ? { fee_id: refId } : { fine_id: refId };
      const orderRes = await paymentsAPI.createOrder(payload);
      const orderData = orderRes.data;

      openRazorpayCheckout(
        orderData,
        async (response) => {
          try {
            await paymentsAPI.verify({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });
            navigate('/student/payment-success', {
              state: { paymentId: orderData.payment_id },
            });
          } catch {
            navigate('/student/payment-failure');
          }
        },
        () => navigate('/student/payment-failure'),
      );
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to initiate payment');
    } finally {
      setPaying(null);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Fees & Fines</h1>

      {error && <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">{error}</div>}

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <StatCard title="Total Hostel Fee" value={`₹${summary.total_hostel_fee.toLocaleString()}`} icon="🏠" color="blue" />
          <StatCard title="Pending Fee" value={`₹${summary.pending_fee.toLocaleString()}`} icon="⏳" color="yellow" />
          <StatCard title="Total Fine Amount" value={`₹${summary.total_fine_amount.toLocaleString()}`} icon="⚠️" color="red" />
          <StatCard title="Pending Fine Amount" value={`₹${summary.pending_fine_amount.toLocaleString()}`} icon="💸" color="red" />
        </div>
      )}

      <div className="card mb-6">
        <h2 className="text-lg font-semibold mb-4">Hostel Fees</h2>
        {fees.length > 0 ? (
          <div className="space-y-3">
            {fees.map((f) => (
              <div key={f.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{f.academic_year} — {f.fee_id}</p>
                  <p className="text-sm text-gray-500">Due: {f.due_date} · ₹{f.fee_amount.toLocaleString()}</p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={f.status} />
                  {f.status !== 'Paid' && (
                    <button
                      onClick={() => handlePay('fee', f.fee_id)}
                      disabled={paying === f.fee_id}
                      className="btn-primary text-sm py-1.5 px-3"
                    >
                      {paying === f.fee_id ? 'Processing...' : 'Pay Now'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400">No hostel fees assigned</p>
        )}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Fines</h2>
        {fines.length > 0 ? (
          <div className="space-y-3">
            {fines.map((f) => (
              <div key={f.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{f.fine_reason} — {f.fine_id}</p>
                  <p className="text-sm text-gray-500">{f.fine_description}</p>
                  <p className="text-sm text-gray-500">Due: {f.due_date} · ₹{f.fine_amount.toLocaleString()}</p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={f.status} />
                  {f.status !== 'Paid' && (
                    <button
                      onClick={() => handlePay('fine', f.fine_id)}
                      disabled={paying === f.fine_id}
                      className="btn-primary text-sm py-1.5 px-3"
                    >
                      {paying === f.fine_id ? 'Processing...' : 'Pay Now'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400">No fines assigned</p>
        )}
      </div>
    </div>
  );
}
