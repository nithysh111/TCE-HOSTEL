import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import NotificationBell from './NotificationBell';

const adminLinks = [
  { to: '/admin/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/admin/occupancy', label: 'Occupancy', icon: '🏠' },
  { to: '/admin/students', label: 'Students', icon: '👨‍🎓' },
  { to: '/admin/menus', label: 'Food Menu', icon: '🍽️' },
  { to: '/admin/predictions', label: 'Food Prediction', icon: '🤖' },
  { to: '/admin/complaints', label: 'Complaints', icon: '📋' },
  { to: '/admin/announcements', label: 'Announcements', icon: '📢' },
  { to: '/admin/leave', label: 'Leave Requests', icon: '📝' },
  { to: '/admin/attendance', label: 'Attendance', icon: '✅' },
  { to: '/admin/fees', label: 'Hostel Fees', icon: '💰' },
  { to: '/admin/fines', label: 'Fines', icon: '⚠️' },
  { to: '/admin/fee-analytics', label: 'Fee Analytics', icon: '📈' },
];

const studentLinks = [
  { to: '/student/dashboard', label: 'Dashboard', icon: '🏠' },
  { to: '/student/menu', label: 'Food Menu', icon: '🍽️' },
  { to: '/student/complaints', label: 'Complaints', icon: '📋' },
  { to: '/student/announcements', label: 'Announcements', icon: '📢' },
  { to: '/student/leave', label: 'Leave Request', icon: '📝' },
  { to: '/student/fees', label: 'Fees & Fines', icon: '💰' },
  { to: '/student/payments', label: 'Payment History', icon: '🧾' },
];

export default function Layout() {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const links = isAdmin ? adminLinks : studentLinks;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 bg-primary-900 text-white flex flex-col fixed h-full">
        <div className="p-5 border-b border-primary-700">
          <h1 className="text-lg font-bold leading-tight">Hostel Food Intelligence</h1>
          <p className="text-primary-300 text-xs mt-1">Management System</p>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                location.pathname === link.to
                  ? 'bg-primary-700 text-white'
                  : 'text-primary-200 hover:bg-primary-800 hover:text-white'
              }`}
            >
              <span>{link.icon}</span>
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-primary-700">
          <p className="text-sm text-primary-300 truncate">{user?.email}</p>
          <p className="text-xs text-primary-400 capitalize">{user?.role}</p>
          <button
            onClick={handleLogout}
            className="mt-2 w-full text-left text-sm text-primary-300 hover:text-white transition-colors"
          >
            Sign Out
          </button>
        </div>
      </aside>
      <main className="flex-1 ml-64 p-8">
        {!isAdmin && (
          <div className="flex justify-end mb-4 -mt-2">
            <NotificationBell />
          </div>
        )}
        <Outlet />
      </main>
    </div>
  );
}
