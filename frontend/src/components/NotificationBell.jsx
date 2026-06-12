import { useEffect, useState } from 'react';
import { notificationsAPI } from '../services/api';

export default function NotificationBell() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);

  const fetchNotifications = () => {
    notificationsAPI.list({ per_page: 10 })
      .then((res) => {
        setNotifications(res.data.items);
        setUnreadCount(res.data.unread_count || 0);
      })
      .catch(console.error);
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleMarkRead = async (id) => {
    await notificationsAPI.markRead(id);
    fetchNotifications();
  };

  const handleMarkAllRead = async () => {
    await notificationsAPI.markAllRead();
    fetchNotifications();
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-lg hover:bg-primary-800 transition-colors"
        aria-label="Notifications"
      >
        <span className="text-xl">🔔</span>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50 text-gray-900">
          <div className="flex items-center justify-between p-3 border-b">
            <h3 className="font-semibold text-sm">Notifications</h3>
            {unreadCount > 0 && (
              <button onClick={handleMarkAllRead} className="text-xs text-primary-600 hover:underline">
                Mark all read
              </button>
            )}
          </div>
          <div className="max-h-80 overflow-y-auto">
            {notifications.length > 0 ? notifications.map((n) => (
              <div
                key={n.id}
                className={`p-3 border-b border-gray-50 cursor-pointer hover:bg-gray-50 ${!n.is_read ? 'bg-blue-50' : ''}`}
                onClick={() => !n.is_read && handleMarkRead(n.id)}
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-primary-600">{n.notification_type}</span>
                  {!n.is_read && <span className="w-2 h-2 bg-blue-500 rounded-full" />}
                </div>
                <p className="font-medium text-sm mt-1">{n.title}</p>
                <p className="text-xs text-gray-500 mt-0.5">{n.message}</p>
              </div>
            )) : (
              <p className="p-4 text-sm text-gray-400 text-center">No notifications</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
