import { useEffect, useState } from 'react';
import { leaveAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function Leave() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = () => {
    leaveAPI.list().then((res) => setRequests(res.data.items)).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const updateStatus = async (id, status) => {
    await leaveAPI.updateStatus(id, status);
    fetchData();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Leave Requests</h1>
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="pb-3 pr-4">Roll No</th>
              <th className="pb-3 pr-4">Type</th>
              <th className="pb-3 pr-4">From</th>
              <th className="pb-3 pr-4">To</th>
              <th className="pb-3 pr-4">Reason</th>
              <th className="pb-3 pr-4">Status</th>
              <th className="pb-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {requests.map((r) => (
              <tr key={r.id} className="border-b border-gray-50">
                <td className="py-3 pr-4 font-medium">{r.roll_no}</td>
                <td className="py-3 pr-4 capitalize">{r.leave_type.replace('_', ' ')}</td>
                <td className="py-3 pr-4">{r.start_date}</td>
                <td className="py-3 pr-4">{r.end_date}</td>
                <td className="py-3 pr-4 max-w-xs truncate">{r.reason}</td>
                <td className="py-3 pr-4"><StatusBadge status={r.status} /></td>
                <td className="py-3">
                  {r.status === 'pending' && (
                    <div className="flex gap-1">
                      <button onClick={() => updateStatus(r.id, 'approved')} className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Approve</button>
                      <button onClick={() => updateStatus(r.id, 'rejected')} className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">Reject</button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
