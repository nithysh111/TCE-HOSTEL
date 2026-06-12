import { useEffect, useState } from 'react';
import { complaintsAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

const STATUSES = ['Open', 'In Progress', 'Resolved'];

export default function Complaints() {
  const [complaints, setComplaints] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchComplaints = () => {
    const params = filter ? { status: filter } : {};
    complaintsAPI.list(params).then((res) => setComplaints(res.data.items)).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchComplaints(); }, [filter]);

  const updateStatus = async (id, status) => {
    await complaintsAPI.updateStatus(id, status);
    fetchComplaints();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Complaint Management</h1>
        <select className="input-field w-auto" value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="">All Status</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="pb-3 pr-4">ID</th>
              <th className="pb-3 pr-4">Roll No</th>
              <th className="pb-3 pr-4">Category</th>
              <th className="pb-3 pr-4">Description</th>
              <th className="pb-3 pr-4">Date</th>
              <th className="pb-3 pr-4">Status</th>
              <th className="pb-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {complaints.map((c) => (
              <tr key={c.id} className="border-b border-gray-50">
                <td className="py-3 pr-4 font-mono text-xs">{c.complaint_id}</td>
                <td className="py-3 pr-4">{c.roll_no}</td>
                <td className="py-3 pr-4">{c.category}</td>
                <td className="py-3 pr-4 max-w-xs truncate">{c.description}</td>
                <td className="py-3 pr-4">{c.created_at?.slice(0, 10)}</td>
                <td className="py-3 pr-4"><StatusBadge status={c.status} /></td>
                <td className="py-3">
                  <select
                    className="text-xs border rounded px-2 py-1"
                    value={c.status}
                    onChange={(e) => updateStatus(c.complaint_id, e.target.value)}
                  >
                    {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </td>
              </tr>
            ))}
            {complaints.length === 0 && (
              <tr><td colSpan={7} className="py-8 text-center text-gray-400">No complaints found</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
