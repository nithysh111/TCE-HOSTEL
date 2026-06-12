import { useEffect, useState } from 'react';
import { complaintsAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

const CATEGORIES = ['Electrical Issue', 'Room Cleaning', 'WiFi Issue', 'Food Quality Issue', 'Water Issue', 'Other'];

export default function StudentComplaints() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ category: CATEGORIES[0], description: '' });

  const fetchData = () => {
    complaintsAPI.list().then((res) => setComplaints(res.data.items)).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await complaintsAPI.create(form);
    setForm({ category: CATEGORIES[0], description: '' });
    setShowForm(false);
    fetchData();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Complaints</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary">+ Submit Complaint</button>
      </div>

      {showForm && (
        <div className="card mb-6">
          <h3 className="font-semibold mb-4">New Complaint</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Category</label>
              <select className="input-field" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Description</label>
              <textarea className="input-field" rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required placeholder="Describe your issue in detail..." />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary">Submit</button>
              <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-4">
        {complaints.map((c) => (
          <div key={c.id} className="card">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-xs text-gray-500">{c.complaint_id}</span>
                  <StatusBadge status={c.status} />
                </div>
                <p className="font-medium text-gray-800">{c.category}</p>
                <p className="text-sm text-gray-600 mt-1">{c.description}</p>
                <p className="text-xs text-gray-400 mt-2">Submitted: {c.created_at?.slice(0, 10)}</p>
              </div>
            </div>
          </div>
        ))}
        {complaints.length === 0 && <p className="text-gray-400 text-center py-8">No complaints submitted yet</p>}
      </div>
    </div>
  );
}
