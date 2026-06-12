import { useEffect, useState } from 'react';
import { leaveAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function StudentLeave() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    start_date: '',
    end_date: '',
    reason: '',
    leave_type: 'regular',
  });

  const fetchData = () => {
    leaveAPI.list().then((res) => setRequests(res.data.items)).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await leaveAPI.create(form);
    setForm({ start_date: '', end_date: '', reason: '', leave_type: 'regular' });
    setShowForm(false);
    fetchData();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Leave Requests</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary">+ New Request</button>
      </div>

      {showForm && (
        <div className="card mb-6">
          <h3 className="font-semibold mb-4">Submit Leave Request</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Leave Type</label>
              <select className="input-field" value={form.leave_type} onChange={(e) => setForm({ ...form, leave_type: e.target.value })}>
                <option value="regular">Regular Leave</option>
                <option value="holiday_stay">Stay During Holidays</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="label">Start Date</label><input type="date" className="input-field" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} required /></div>
              <div><label className="label">End Date</label><input type="date" className="input-field" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} required /></div>
            </div>
            <div><label className="label">Reason</label><textarea className="input-field" rows={3} value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} required /></div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary">Submit</button>
              <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-4">
        {requests.map((r) => (
          <div key={r.id} className="card">
            <div className="flex justify-between items-start">
              <div>
                <p className="font-medium capitalize">{r.leave_type.replace('_', ' ')}</p>
                <p className="text-sm text-gray-600">{r.start_date} to {r.end_date}</p>
                <p className="text-sm text-gray-500 mt-1">{r.reason}</p>
              </div>
              <StatusBadge status={r.status} />
            </div>
          </div>
        ))}
        {requests.length === 0 && <p className="text-gray-400 text-center py-8">No leave requests yet</p>}
      </div>
    </div>
  );
}
