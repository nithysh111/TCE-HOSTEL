import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
};

export const studentsAPI = {
  list: (params) => api.get('/students/', { params }),
  search: (rollNo) => api.get(`/students/search/${rollNo}`),
  get: (id) => api.get(`/students/${id}`),
  create: (data) => api.post('/students/', data),
  update: (id, data) => api.put(`/students/${id}`, data),
  rooms: () => api.get('/students/rooms'),
};

export const attendanceAPI = {
  list: (params) => api.get('/attendance/', { params }),
  importCSV: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/attendance/import/csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  importAPI: (data) => api.post('/attendance/import/api', data),
  create: (data) => api.post('/attendance/', data),
};

export const occupancyAPI = {
  summary: (date) => api.get('/occupancy/summary', { params: { date } }),
  inside: (date) => api.get('/occupancy/inside', { params: { date } }),
  outside: (date) => api.get('/occupancy/outside', { params: { date } }),
  onLeave: (date) => api.get('/occupancy/on-leave', { params: { date } }),
  trend: (days) => api.get('/occupancy/trend', { params: { days } }),
  weekly: () => api.get('/occupancy/weekly'),
  monthly: () => api.get('/occupancy/monthly'),
};

export const menusAPI = {
  list: (params) => api.get('/menus/', { params }),
  today: () => api.get('/menus/today'),
  weekly: (start) => api.get('/menus/weekly', { params: { start } }),
  special: () => api.get('/menus/special'),
  get: (id) => api.get(`/menus/${id}`),
  create: (data) => api.post('/menus/', data),
  update: (id, data) => api.put(`/menus/${id}`, data),
  delete: (id) => api.delete(`/menus/${id}`),
};

export const complaintsAPI = {
  list: (params) => api.get('/complaints/', { params }),
  get: (id) => api.get(`/complaints/${id}`),
  create: (data) => api.post('/complaints/', data),
  updateStatus: (id, status) => api.put(`/complaints/${id}/status`, { status }),
};

export const announcementsAPI = {
  list: (params) => api.get('/announcements/', { params }),
  get: (id) => api.get(`/announcements/${id}`),
  create: (data) => api.post('/announcements/', data),
  update: (id, data) => api.put(`/announcements/${id}`, data),
  delete: (id) => api.delete(`/announcements/${id}`),
};

export const leaveAPI = {
  list: (params) => api.get('/leave/', { params }),
  create: (data) => api.post('/leave/', data),
  updateStatus: (id, status) => api.put(`/leave/${id}/status`, { status }),
};

export const predictionsAPI = {
  food: (params) => api.get('/predictions/food', { params }),
  history: (days) => api.get('/predictions/food/history', { params: { days } }),
  wastage: (params) => api.get('/predictions/wastage', { params }),
  createWastage: (data) => api.post('/predictions/wastage', data),
};

export const analyticsAPI = {
  dashboard: () => api.get('/analytics/dashboard'),
  complaints: () => api.get('/analytics/complaints'),
  leave: () => api.get('/analytics/leave'),
  feesFines: () => api.get('/analytics/fees-fines'),
};

export const feesAPI = {
  list: (params) => api.get('/fees/', { params }),
  get: (id) => api.get(`/fees/${id}`),
  create: (data) => api.post('/fees/', data),
  assignBulk: (data) => api.post('/fees/assign-bulk', data),
  update: (id, data) => api.put(`/fees/${id}`, data),
  markPaid: (id) => api.put(`/fees/${id}/mark-paid`),
  summary: (params) => api.get('/fees/summary', { params }),
};

export const finesAPI = {
  list: (params) => api.get('/fines/', { params }),
  get: (id) => api.get(`/fines/${id}`),
  reasons: () => api.get('/fines/reasons'),
  create: (data) => api.post('/fines/', data),
  update: (id, data) => api.put(`/fines/${id}`, data),
  delete: (id) => api.delete(`/fines/${id}`),
  markPaid: (id) => api.put(`/fines/${id}/mark-paid`),
  audit: (id) => api.get(`/fines/${id}/audit`),
};

export const paymentsAPI = {
  list: (params) => api.get('/payments/', { params }),
  config: () => api.get('/payments/config'),
  createOrder: (data) => api.post('/payments/create-order', data),
  verify: (data) => api.post('/payments/verify', data),
  receipt: (id) => api.get(`/payments/${id}/receipt`),
};

export const notificationsAPI = {
  list: (params) => api.get('/notifications/', { params }),
  markRead: (id) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put('/notifications/read-all'),
  runReminders: () => api.post('/notifications/run-reminders'),
};

export default api;
