import { useEffect, useState } from 'react';
import { feesAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

const emptyForm = {
  roll_no: '', academic_year: '2025-2026', fee_amount: '', due_date: '',
  hostel_block: '', room_number: '',
};

const emptyBulk = {
  academic_year: '2025-2026', fee_amount: '', due_date: '', hostel_block: '', roll_numbers: '',
};

export default function Fees() {
  const [fees, setFees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [showBulk, setShowBulk] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [bulk, setBulk] = useState(emptyBulk);
  const [error, setError] = useState('');

  const fetchData = () => {
    const params = statusFilter ? { status: statusFilter } : {};
    feesAPI.list(params)
      .then((res) => setFees(res.data.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [statusFilter]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await feesAPI.create({ ...form, fee_amount: parseFloat(form.fee_amount) });
      setForm(emptyForm);
      setShowForm(false);
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create fee');
    }
  };

  const handleBulk = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const payload = {
        academic_year: bulk.academic_year,
        fee_amount: parseFloat(bulk.fee_amount),
        due_date: bulk.due_date,
      };
      if (bulk.hostel_block) payload.hostel_block = bulk.hostel_block;
      if (bulk.roll_numbers.trim()) {
        payload.roll_numbers = bulk.roll_numbers.split(',').map((r) => r.trim()).filter(Boolean);
      }
      await feesAPI.assignBulk(payload);
      setBulk(emptyBulk);
      setShowBulk(false);
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to assign fees');
    }
  };

  const markPaid = async (feeId) => {
    await feesAPI.markPaid(feeId);
    fetchData();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Hostel Fee Management</h1>
        <div className="flex gap-2">
          <button onClick={() => { setShowBulk(!showBulk); setShowForm(false); }} className="btn-secondary">
            Bulk Assign
          </button>
          <button onClick={() => { setShowForm(!showForm); setShowBulk(false); }} className="btn-primary">
            Assign Fee
          </button>
        </div>
      </div>

      {error && <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">{error}</div>}

      {showForm && (
        <form onSubmit={handleCreate} className="card mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label">Roll Number</label>
            <input className="input-field" value={form.roll_no} onChange={(e) => setForm({ ...form, roll_no: e.target.value })} required />
          </div>
          <div>
            <label className="label">Academic Year</label>
            <input className="input-field" value={form.academic_year} onChange={(e) => setForm({ ...form, academic_year: e.target.value })} required />
          </div>
          <div>
            <label className="label">Fee Amount (₹)</label>
            <input type="number" className="input-field" value={form.fee_amount} onChange={(e) => setForm({ ...form, fee_amount: e.target.value })} required />
          </div>
          <div>
            <label className="label">Due Date</label>
            <input type="date" className="input-field" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} required />
          </div>
          <div>
            <label className="label">Hostel Block</label>
            <input className="input-field" value={form.hostel_block} onChange={(e) => setForm({ ...form, hostel_block: e.target.value })} />
          </div>
          <div className="flex items-end">
            <button type="submit" className="btn-primary">Create Fee</button>
          </div>
        </form>
      )}

      {showBulk && (
        <form onSubmit={handleBulk} className="card mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label">Academic Year</label>
            <input className="input-field" value={bulk.academic_year} onChange={(e) => setBulk({ ...bulk, academic_year: e.target.value })} required />
          </div>
          <div>
            <label className="label">Fee Amount (₹)</label>
            <input type="number" className="input-field" value={bulk.fee_amount} onChange={(e) => setBulk({ ...bulk, fee_amount: e.target.value })} required />
          </div>
          <div>
            <label className="label">Due Date</label>
            <input type="date" className="input-field" value={bulk.due_date} onChange={(e) => setBulk({ ...bulk, due_date: e.target.value })} required />
          </div>
          <div>
            <label className="label">Hostel Block (optional)</label>
            <input className="input-field" value={bulk.hostel_block} onChange={(e) => setBulk({ ...bulk, hostel_block: e.target.value })} placeholder="Leave empty for all" />
          </div>
          <div className="md:col-span-2">
            <label className="label">Roll Numbers (comma-separated, optional)</label>
            <input className="input-field" value={bulk.roll_numbers} onChange={(e) => setBulk({ ...bulk, roll_numbers: e.target.value })} placeholder="CS001, CS002" />
          </div>
          <div className="flex items-end">
            <button type="submit" className="btn-primary">Assign to Students</button>
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
              <th className="pb-3 pr-4">Fee ID</th>
              <th className="pb-3 pr-4">Roll No</th>
              <th className="pb-3 pr-4">Student</th>
              <th className="pb-3 pr-4">Year</th>
              <th className="pb-3 pr-4">Block</th>
              <th className="pb-3 pr-4">Amount</th>
              <th className="pb-3 pr-4">Due Date</th>
              <th className="pb-3 pr-4">Status</th>
              <th className="pb-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {fees.map((f) => (
              <tr key={f.id} className="border-b border-gray-50">
                <td className="py-3 pr-4 font-mono text-xs">{f.fee_id}</td>
                <td className="py-3 pr-4 font-medium">{f.roll_no}</td>
                <td className="py-3 pr-4">{f.student_name || '—'}</td>
                <td className="py-3 pr-4">{f.academic_year}</td>
                <td className="py-3 pr-4">{f.hostel_block || '—'}</td>
                <td className="py-3 pr-4">₹{f.fee_amount.toLocaleString()}</td>
                <td className="py-3 pr-4">{f.due_date}</td>
                <td className="py-3 pr-4"><StatusBadge status={f.status} /></td>
                <td className="py-3">
                  {f.status !== 'Paid' && (
                    <button onClick={() => markPaid(f.fee_id)} className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                      Mark Paid
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {fees.length === 0 && <p className="text-gray-400 text-center py-8">No fees found</p>}
      </div>
    </div>
  );
}
