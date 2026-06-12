import { useEffect, useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { analyticsAPI } from '../../services/api';
import StatCard from '../../components/StatCard';
import ChartCard from '../../components/ChartCard';
import LoadingSpinner from '../../components/LoadingSpinner';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend);

export default function FeeAnalytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsAPI.feesFines()
      .then((res) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  if (!data) return <p className="text-red-500">Failed to load analytics.</p>;

  const feeChart = {
    labels: data.monthly_fee_collection.map((d) => d.month),
    datasets: [{
      label: 'Fee Collection (₹)',
      data: data.monthly_fee_collection.map((d) => d.amount),
      backgroundColor: '#3b82f6',
    }],
  };

  const fineChart = {
    labels: data.monthly_fine_collection.map((d) => d.month),
    datasets: [{
      label: 'Fine Collection (₹)',
      data: data.monthly_fine_collection.map((d) => d.amount),
      backgroundColor: '#ef4444',
    }],
  };

  const pendingChart = {
    labels: data.pending_payments_trend.map((d) => d.date.slice(5)),
    datasets: [{
      label: 'Pending Payments',
      data: data.pending_payments_trend.map((d) => d.count),
      borderColor: '#eab308',
      backgroundColor: 'rgba(234,179,8,0.1)',
      fill: true,
      tension: 0.4,
    }],
  };

  const revenueChart = {
    labels: data.revenue_analytics.map((d) => d.label),
    datasets: [{
      data: data.revenue_analytics.map((d) => d.amount),
      backgroundColor: ['#22c55e', '#ef4444', '#eab308', '#f97316'],
    }],
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Fee & Fine Analytics</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
        <StatCard title="Total Fees Collected" value={`₹${data.total_fees_collected.toLocaleString()}`} icon="💰" color="green" />
        <StatCard title="Total Pending Fees" value={`₹${data.total_pending_fees.toLocaleString()}`} icon="⏳" color="yellow" />
        <StatCard title="Total Fine Amount" value={`₹${data.total_fine_amount.toLocaleString()}`} icon="⚠️" color="red" />
        <StatCard title="Total Fine Collected" value={`₹${data.total_fine_collected.toLocaleString()}`} icon="✅" color="green" />
        <StatCard title="Overdue Fees" value={data.overdue_fees} icon="📅" color="red" />
        <StatCard title="Overdue Fines" value={data.overdue_fines} icon="📅" color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ChartCard title="Monthly Fee Collection">
          <Bar data={feeChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
        </ChartCard>
        <ChartCard title="Monthly Fine Collection">
          <Bar data={fineChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Pending Payments Trend">
          <Line data={pendingChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
        </ChartCard>
        <ChartCard title="Revenue Analytics">
          <Doughnut data={revenueChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }} />
        </ChartCard>
      </div>
    </div>
  );
}
