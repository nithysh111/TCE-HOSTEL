import { useEffect, useState } from 'react';
import { menusAPI } from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';

const MEAL_TYPES = ['Breakfast', 'Lunch', 'Dinner'];

export default function Menus() {
  const [menus, setMenus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    menu_date: new Date().toISOString().split('T')[0],
    meal_type: 'Breakfast',
    menu_title: '',
    menu_items: '',
    is_special: false,
    description: '',
  });
  const [editId, setEditId] = useState(null);

  const fetchMenus = () => {
    menusAPI.list().then((res) => setMenus(res.data.items)).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchMenus(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editId) {
        await menusAPI.update(editId, form);
      } else {
        await menusAPI.create(form);
      }
      setShowForm(false);
      setEditId(null);
      setForm({ menu_date: new Date().toISOString().split('T')[0], meal_type: 'Breakfast', menu_title: '', menu_items: '', is_special: false, description: '' });
      fetchMenus();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to save menu');
    }
  };

  const handleEdit = (menu) => {
    setForm({
      menu_date: menu.menu_date,
      meal_type: menu.meal_type,
      menu_title: menu.menu_title,
      menu_items: menu.menu_items,
      is_special: menu.is_special,
      description: menu.description || '',
    });
    setEditId(menu.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this menu?')) return;
    await menusAPI.delete(id);
    fetchMenus();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Food Menu Management</h1>
        <button onClick={() => { setShowForm(true); setEditId(null); }} className="btn-primary">+ Add Menu</button>
      </div>

      {showForm && (
        <div className="card mb-6">
          <h3 className="text-lg font-semibold mb-4">{editId ? 'Edit Menu' : 'Add New Menu'}</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Date</label>
              <input type="date" className="input-field" value={form.menu_date} onChange={(e) => setForm({ ...form, menu_date: e.target.value })} required />
            </div>
            <div>
              <label className="label">Meal Type</label>
              <select className="input-field" value={form.meal_type} onChange={(e) => setForm({ ...form, meal_type: e.target.value })}>
                {MEAL_TYPES.map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Menu Title</label>
              <input className="input-field" value={form.menu_title} onChange={(e) => setForm({ ...form, menu_title: e.target.value })} required />
            </div>
            <div>
              <label className="label">Menu Items</label>
              <input className="input-field" value={form.menu_items} onChange={(e) => setForm({ ...form, menu_items: e.target.value })} placeholder="Idli, Sambar, Chutney" required />
            </div>
            <div className="md:col-span-2">
              <label className="label">Description</label>
              <textarea className="input-field" rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="special" checked={form.is_special} onChange={(e) => setForm({ ...form, is_special: e.target.checked })} />
              <label htmlFor="special" className="text-sm">Special / Festival Meal</label>
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary">{editId ? 'Update' : 'Create'}</button>
              <button type="button" className="btn-secondary" onClick={() => { setShowForm(false); setEditId(null); }}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {menus.map((menu) => (
          <div key={menu.id} className={`card ${menu.is_special ? 'border-yellow-300 bg-yellow-50' : ''}`}>
            <div className="flex justify-between items-start mb-2">
              <div>
                <span className="text-xs text-gray-500">{menu.menu_date} — {menu.meal_type}</span>
                <h3 className="font-semibold text-gray-800">{menu.menu_title}</h3>
              </div>
              {menu.is_special && <span className="badge badge-yellow">Special</span>}
            </div>
            <p className="text-sm text-gray-600 mb-3">{menu.menu_items}</p>
            {menu.description && <p className="text-xs text-gray-400 mb-3">{menu.description}</p>}
            <div className="flex gap-2">
              <button onClick={() => handleEdit(menu)} className="text-sm text-primary-600 hover:underline">Edit</button>
              <button onClick={() => handleDelete(menu.id)} className="text-sm text-red-600 hover:underline">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
