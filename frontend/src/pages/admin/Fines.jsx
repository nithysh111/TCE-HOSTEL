import { useEffect, useState } from 'react';
import { finesAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

const emptyForm = {
  roll_no: '', fine_amount: '', fine_reason: '', fine_description: '',
  issued_date: new Date().toISOString().split('T')[0], due_date: '',
};

export default function Fines() {
  const [fines, setFines] = useState([]);
  const [reasons, setReasons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [editId, setEditId] = useState(null);
  const [error, setError] = useState('');

  const fetchData = () => {
    const params = statusFilter ? { status: statusFilter } : {};
    Promise.all([finesAPI.list(params), finesAPI.reasons()])
      .then(([finesRes, reasonsRes]) => {
        setFines(finesRes.data.items);
        setReasons(reasonsRes.data.reasons);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [statusFilter]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const payload = { ...form, fine_amount: parseFloat(form.fine_amount) };
    try {
      if (editId) {
        await finesAPI.update(editId, payload);
      } else {
        await finesAPI.create(payload);
      }
      setForm(emptyForm);
      setEditId(null);
      setShowForm(false);
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save fine');
    }
  };

  const startEdit = (fine) => {
    setEditId(fine.fine_id);
    setForm({
      roll_no: fine.roll_no,
      fine_amount: fine.fine_amount,
      fine_reason: fine.fine_reason,
      fine_description: fine.fine_description || '',
      issued_date: fine.issued_date,
      due_date: fine.due_date,
    });
    setShowForm(true);
  };

  const handleDelete = async (fineId) => {
    if (!window.confirm('Delete this fine?')) return;
    await finesAPI.delete(fineId);
    fetchData();
  };

  const markPaid = async (fineId) => {
    await finesAPI.markPaid(fineId);
    fetchData();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Fine Management</h1>
        <button onClick={() => { setShowForm(!showForm); setEditId(null); setForm(emptyForm); }} className="btn-primary">
          Create Fine
        </button>
      </div>

      {error && <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">{error}</div>}

      {showForm && (
        <form onSubmit={handleSubmit} className="card mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label">Roll Number</label>
            <input className="input-field" value={form.roll_no} onChange={(e) => setForm({ ...form, roll_no: e.target.value })} required disabled={!!editId} />
          </div>
          <div>
            <label className="label">Fine Amount (₹)</label>
            <input type="number" className="input-field" value={form.fine_amount} onChange={(e) => setForm({ ...form, fine_amount: e.target.value })} required />
          </div>
          <div>
            <label className="label">Fine Reason</label>
            <select className="input-field" value={form.fine_reason} onChange={(e) => setForm({ ...form, fine_reason: e.target.value })} required>
              <option value="">Select reason</option>
              {reasons.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Issued Date</label>
            <input type="date" className="input-field" value={form.issued_date} onChange={(e) => setForm({ ...form, issued_date: e.target.value })} required />
          </div>
          <div>
            <label className="label">Due Date</label>
            <input type="date" className="input-field" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} required />
          </div>
          <div className="md:col-span-3">
            <label className="label">Description</label>
            <textarea className="input-field" rows={2} value={form.fine_description} onChange={(e) => setForm({ ...form, fine_description: e.target.value })} />
          </div>
          <div className="flex items-end gap-2">
            <button type="submit" className="btn-primary">{editId ? 'Update Fine' : 'Create Fine'}</button>
            <button type="button" onClick={() => { setShowForm(false); setEditId(null); }} className="btn-secondary">Cancel</button>
          </div>
        </form>
      )}

      <div className="flex gap-2 mb-4">
        {['', 'Pending', 'Paid', 'Overdue'].map((s) => (
          <button
            key={s || 'all'}
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-sm ${statusFilter === s ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600'}`}
          >
            {s || 'All'}
          </button>
        ))}
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="pb-3 pr-4">Fine ID</th>
              <th className="pb-3 pr-4">Roll No</th>
              <th className="pb-3 pr-4">Student</th>
              <th className="pb-3 pr-4">Reason</th>
              <th className="pb-3 pr-4">Amount</th>
              <th className="pb-3 pr-4">Due Date</th>
              <th className="pb-3 pr-4">Status</th>
              <th className="pb-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {fines.map((f) => (
              <tr key={f.id} className="border-b border-gray-50">
                <td className="py-3 pr-4 font-mono text-xs">{f.fine_id}</td>
                <td className="py-3 pr-4 font-medium">{f.roll_no}</td>
                <td className="py-3 pr-4">{f.student_name}</td>
                <td className="py-3 pr-4">{f.fine_reason}</td>
                <td className="py-3 pr-4">₹{f.fine_amount.toLocaleString()}</td>
                <td className="py-3 pr-4">{f.due_date}</td>
                <td className="py-3 pr-4"><StatusBadge status={f.status} /></td>
                <td className="py-3">
                  <div className="flex gap-1 flex-wrap">
                    {f.status !== 'Paid' && (
                      <>
                        <button onClick={() => markPaid(f.fine_id)} className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Paid</button>
                        <button onClick={() => startEdit(f)} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">Edit</button>
                        <button onClick={() => handleDelete(f.fine_id)} className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">Delete</button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {fines.length === 0 && <p className="text-gray-400 text-center py-8">No fines found</p>}
      </div>
    </div>
  );
}
