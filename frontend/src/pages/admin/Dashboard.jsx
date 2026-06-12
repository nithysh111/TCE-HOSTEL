import { useEffect, useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { analyticsAPI } from '../../services/api';
import StatCard from '../../components/StatCard';
import ChartCard from '../../components/ChartCard';
import LoadingSpinner from '../../components/LoadingSpinner';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler);

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsAPI.dashboard()
      .then((res) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  if (!data) return <p className="text-red-500">Failed to load dashboard data.</p>;

  const { occupancy, occupancy_trend, complaints, leaves, food_prediction, wastage } = data;

  const trendChart = {
    labels: occupancy_trend.map((d) => d.date.slice(5)),
    datasets: [
      { label: 'Inside', data: occupancy_trend.map((d) => d.inside), borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,0.1)', fill: true, tension: 0.4 },
      { label: 'Outside', data: occupancy_trend.map((d) => d.outside), borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)', fill: true, tension: 0.4 },
      { label: 'On Leave', data: occupancy_trend.map((d) => d.on_leave), borderColor: '#eab308', backgroundColor: 'rgba(234,179,8,0.1)', fill: true, tension: 0.4 },
    ],
  };

  const complaintChart = {
    labels: Object.keys(complaints.by_category || {}),
    datasets: [{ data: Object.values(complaints.by_category || {}), backgroundColor: ['#3b82f6', '#22c55e', '#eab308', '#ef4444', '#8b5cf6', '#6b7280'] }],
  };

  const predictionChart = food_prediction ? {
    labels: ['Breakfast', 'Lunch', 'Dinner'],
    datasets: [{
      label: 'Predicted Students',
      data: [food_prediction.predicted_breakfast, food_prediction.predicted_lunch, food_prediction.predicted_dinner],
      backgroundColor: ['#60a5fa', '#34d399', '#fbbf24'],
    }],
  } : null;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Management Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard title="Total Students" value={occupancy.total_students} icon="👨‍🎓" color="blue" />
        <StatCard title="Inside Hostel" value={occupancy.students_inside} icon="🏠" color="green" />
        <StatCard title="Outside Hostel" value={occupancy.students_outside} icon="🚶" color="red" />
        <StatCard title="On Leave" value={occupancy.students_on_leave} icon="📝" color="yellow" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ChartCard title="Occupancy Trend (30 Days)">
          <Line data={trendChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }} />
        </ChartCard>
        <ChartCard title="Complaints by Category">
          <Doughnut data={complaintChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }} />
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {predictionChart && (
          <ChartCard title="Today's Food Prediction">
            <Bar data={predictionChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
          </ChartCard>
        )}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Complaint Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between"><span className="text-gray-600">Open</span><span className="font-bold text-red-600">{complaints.open}</span></div>
            <div className="flex justify-between"><span className="text-gray-600">In Progress</span><span className="font-bold text-yellow-600">{complaints.in_progress}</span></div>
            <div className="flex justify-between"><span className="text-gray-600">Resolved</span><span className="font-bold text-green-600">{complaints.resolved}</span></div>
          </div>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Food Wastage (30 Days)</h3>
          <p className="text-3xl font-bold text-red-600">{wastage.wastage_percentage}%</p>
          <p className="text-sm text-gray-500 mt-1">Wastage rate</p>
          <div className="mt-3 text-sm text-gray-600">
            <p>Prepared: {wastage.total_prepared} servings</p>
            <p>Wasted: {wastage.total_wasted} servings</p>
          </div>
        </div>
      </div>
    </div>
  );
}
