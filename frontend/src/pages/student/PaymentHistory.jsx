import { useEffect, useState } from 'react';
import { paymentsAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function PaymentHistory() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [receipt, setReceipt] = useState(null);

  useEffect(() => {
    paymentsAPI.list()
      .then((res) => setPayments(res.data.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const downloadReceipt = async (paymentId) => {
    const res = await paymentsAPI.receipt(paymentId);
    setReceipt(res.data);
  };

  const printReceipt = () => {
    window.print();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Payment History</h1>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="pb-3 pr-4">Payment ID</th>
              <th className="pb-3 pr-4">Type</th>
              <th className="pb-3 pr-4">Reference</th>
              <th className="pb-3 pr-4">Amount</th>
              <th className="pb-3 pr-4">Date</th>
              <th className="pb-3 pr-4">Status</th>
              <th className="pb-3">Receipt</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((p) => (
              <tr key={p.id} className="border-b border-gray-50">
                <td className="py-3 pr-4 font-mono text-xs">{p.payment_id}</td>
                <td className="py-3 pr-4">{p.fee_ref ? 'Hostel Fee' : 'Fine'}</td>
                <td className="py-3 pr-4">{p.fee_ref || p.fine_ref}</td>
                <td className="py-3 pr-4">₹{p.amount.toLocaleString()}</td>
                <td className="py-3 pr-4">{p.transaction_date?.slice(0, 10) || '—'}</td>
                <td className="py-3 pr-4"><StatusBadge status={p.status} /></td>
                <td className="py-3">
                  {p.status === 'Success' && (
                    <button onClick={() => downloadReceipt(p.payment_id)} className="text-xs text-primary-600 hover:underline">
                      View Receipt
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {payments.length === 0 && <p className="text-gray-400 text-center py-8">No payment history</p>}
      </div>

      {receipt && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4" id="receipt">
            <h2 className="text-xl font-bold text-center mb-4">Payment Receipt</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-500">Receipt ID</span><span>{receipt.receipt_id}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Student</span><span>{receipt.student_name}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Roll No</span><span>{receipt.roll_no}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Payment For</span><span>{receipt.payment_for}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Reference</span><span>{receipt.fee_id || receipt.fine_id}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Amount</span><span className="font-bold">₹{receipt.amount.toLocaleString()}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Transaction ID</span><span className="text-xs">{receipt.razorpay_payment_id}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Date</span><span>{receipt.transaction_date?.slice(0, 10)}</span></div>
            </div>
            <div className="flex gap-2 mt-6">
              <button onClick={printReceipt} className="btn-primary flex-1">Download / Print</button>
              <button onClick={() => setReceipt(null)} className="btn-secondary flex-1">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
