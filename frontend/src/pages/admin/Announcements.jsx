import { useEffect, useState } from 'react';
import { announcementsAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function Announcements() {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', priority: 'medium', expiry_date: '' });
  const [editId, setEditId] = useState(null);

  const fetchData = () => {
    announcementsAPI.list({ active: false }).then((res) => setAnnouncements(res.data.items)).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = { ...form, expiry_date: form.expiry_date || null };
    if (editId) {
      await announcementsAPI.update(editId, data);
    } else {
      await announcementsAPI.create(data);
    }
    setShowForm(false);
    setEditId(null);
    setForm({ title: '', description: '', priority: 'medium', expiry_date: '' });
    fetchData();
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this announcement?')) return;
    await announcementsAPI.delete(id);
    fetchData();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Announcements</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary">+ New Announcement</button>
      </div>

      {showForm && (
        <div className="card mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div><label className="label">Title</label><input className="input-field" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></div>
            <div><label className="label">Description</label><textarea className="input-field" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required /></div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="label">Priority</label><select className="input-field" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></div>
              <div><label className="label">Expiry Date</label><input type="date" className="input-field" value={form.expiry_date} onChange={(e) => setForm({ ...form, expiry_date: e.target.value })} /></div>
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary">{editId ? 'Update' : 'Publish'}</button>
              <button type="button" className="btn-secondary" onClick={() => { setShowForm(false); setEditId(null); }}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-4">
        {announcements.map((a) => (
          <div key={a.id} className="card">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-gray-800">{a.title}</h3>
                  <StatusBadge status={a.priority} />
                </div>
                <p className="text-sm text-gray-600">{a.description}</p>
                <p className="text-xs text-gray-400 mt-2">Posted: {a.created_at?.slice(0, 10)} {a.expiry_date && `| Expires: ${a.expiry_date}`}</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => { setForm({ title: a.title, description: a.description, priority: a.priority, expiry_date: a.expiry_date || '' }); setEditId(a.id); setShowForm(true); }} className="text-sm text-primary-600">Edit</button>
                <button onClick={() => handleDelete(a.id)} className="text-sm text-red-600">Delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
