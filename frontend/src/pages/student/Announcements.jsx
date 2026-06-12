import { useEffect, useState } from 'react';
import { announcementsAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function StudentAnnouncements() {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    announcementsAPI.list().then((res) => setAnnouncements(res.data.items)).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Announcements</h1>
      <div className="space-y-4">
        {announcements.map((a) => (
          <div key={a.id} className={`card ${a.priority === 'high' ? 'border-red-200 bg-red-50' : ''}`}>
            <div className="flex items-center gap-2 mb-2">
              <h3 className="font-semibold text-gray-800">{a.title}</h3>
              <StatusBadge status={a.priority} />
            </div>
            <p className="text-gray-600">{a.description}</p>
            <p className="text-xs text-gray-400 mt-3">
              Posted: {a.created_at?.slice(0, 10)}
              {a.expiry_date && ` | Valid until: ${a.expiry_date}`}
            </p>
          </div>
        ))}
        {announcements.length === 0 && <p className="text-gray-400 text-center py-8">No announcements at this time</p>}
      </div>
    </div>
  );
}
