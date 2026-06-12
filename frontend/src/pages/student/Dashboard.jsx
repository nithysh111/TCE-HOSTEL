import { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { menusAPI, announcementsAPI, feesAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import StatCard from '../../components/StatCard';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function StudentDashboard() {
  const { student } = useAuth();
  const [todayMenu, setTodayMenu] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [feeSummary, setFeeSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([menusAPI.today(), announcementsAPI.list(), feesAPI.summary()])
      .then(([menuRes, annRes, feeRes]) => {
        setTodayMenu(menuRes.data.items);
        setAnnouncements(annRes.data.items.slice(0, 5));
        setFeeSummary(feeRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Welcome, {student?.name || 'Student'}</h1>
      <p className="text-gray-500 mb-6">{student?.roll_no} — {student?.department} — Year {student?.year}</p>

      {feeSummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <StatCard title="Total Hostel Fee" value={`₹${feeSummary.total_hostel_fee.toLocaleString()}`} icon="🏠" color="blue" />
          <StatCard title="Pending Fee" value={`₹${feeSummary.pending_fee.toLocaleString()}`} icon="⏳" color="yellow" />
          <StatCard title="Total Fine Amount" value={`₹${feeSummary.total_fine_amount.toLocaleString()}`} icon="⚠️" color="red" />
          <StatCard title="Pending Fine Amount" value={`₹${feeSummary.pending_fine_amount.toLocaleString()}`} icon="💸" color="red" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Today's Menu</h2>
          {todayMenu.length > 0 ? (
            <div className="space-y-3">
              {todayMenu.map((m) => (
                <div key={m.id} className={`p-3 rounded-lg ${m.is_special ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'}`}>
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-800">{m.meal_type}</span>
                    {m.is_special && <span className="badge badge-yellow">Special</span>}
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{m.menu_items}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No menu published for today</p>
          )}
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Announcements</h2>
          {announcements.length > 0 ? (
            <div className="space-y-3">
              {announcements.map((a) => (
                <div key={a.id} className="border-b border-gray-50 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-800">{a.title}</span>
                    <StatusBadge status={a.priority} />
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{a.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No announcements</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
        <div className="card text-center">
          <p className="text-2xl mb-1">🍽️</p>
          <p className="font-medium">Food Menu</p>
          <p className="text-xs text-gray-500">View daily & weekly menus</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl mb-1">📋</p>
          <p className="font-medium">Complaints</p>
          <p className="text-xs text-gray-500">Submit & track complaints</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl mb-1">📝</p>
          <p className="font-medium">Leave Request</p>
          <p className="text-xs text-gray-500">Apply for leave or holiday stay</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl mb-1">💰</p>
          <p className="font-medium">Fees & Fines</p>
          <p className="text-xs text-gray-500">View dues and pay online</p>
        </div>
      </div>
    </div>
  );
}
