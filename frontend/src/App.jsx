import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import LoadingSpinner from './components/LoadingSpinner';

import AdminDashboard from './pages/admin/Dashboard';
import Occupancy from './pages/admin/Occupancy';
import Students from './pages/admin/Students';
import Menus from './pages/admin/Menus';
import Predictions from './pages/admin/Predictions';
import Complaints from './pages/admin/Complaints';
import Announcements from './pages/admin/Announcements';
import Leave from './pages/admin/Leave';
import Attendance from './pages/admin/Attendance';
import Fees from './pages/admin/Fees';
import Fines from './pages/admin/Fines';
import FeeAnalytics from './pages/admin/FeeAnalytics';

import StudentDashboard from './pages/student/Dashboard';
import StudentMenu from './pages/student/Menu';
import StudentComplaints from './pages/student/Complaints';
import StudentAnnouncements from './pages/student/Announcements';
import StudentLeave from './pages/student/Leave';
import StudentFees from './pages/student/Fees';
import PaymentHistory from './pages/student/PaymentHistory';
import PaymentSuccess from './pages/student/PaymentSuccess';
import PaymentFailure from './pages/student/PaymentFailure';

function RootRedirect() {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === 'admin' ? '/admin/dashboard' : '/student/dashboard'} replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<RootRedirect />} />

      <Route path="/admin" element={<ProtectedRoute role="admin"><Layout /></ProtectedRoute>}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="occupancy" element={<Occupancy />} />
        <Route path="students" element={<Students />} />
        <Route path="menus" element={<Menus />} />
        <Route path="predictions" element={<Predictions />} />
        <Route path="complaints" element={<Complaints />} />
        <Route path="announcements" element={<Announcements />} />
        <Route path="leave" element={<Leave />} />
        <Route path="attendance" element={<Attendance />} />
        <Route path="fees" element={<Fees />} />
        <Route path="fines" element={<Fines />} />
        <Route path="fee-analytics" element={<FeeAnalytics />} />
      </Route>

      <Route path="/student" element={<ProtectedRoute role="student"><Layout /></ProtectedRoute>}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<StudentDashboard />} />
        <Route path="menu" element={<StudentMenu />} />
        <Route path="complaints" element={<StudentComplaints />} />
        <Route path="announcements" element={<StudentAnnouncements />} />
        <Route path="leave" element={<StudentLeave />} />
        <Route path="fees" element={<StudentFees />} />
        <Route path="payments" element={<PaymentHistory />} />
        <Route path="payment-success" element={<PaymentSuccess />} />
        <Route path="payment-failure" element={<PaymentFailure />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
