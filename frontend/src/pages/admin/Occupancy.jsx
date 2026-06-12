import { useEffect, useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { occupancyAPI } from '../../services/api';
import StatCard from '../../components/StatCard';
import ChartCard from '../../components/ChartCard';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function Occupancy() {
  const [summary, setSummary] = useState(null);
  const [weekly, setWeekly] = useState([]);
  const [monthly, setMonthly] = useState([]);
  const [activeTab, setActiveTab] = useState('inside');
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      occupancyAPI.summary(),
      occupancyAPI.weekly(),
      occupancyAPI.monthly(),
    ]).then(([sumRes, weekRes, monthRes]) => {
      setSummary(sumRes.data);
      setWeekly(weekRes.data.items);
      setMonthly(monthRes.data.items);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const fetchers = { inside: occupancyAPI.inside, outside: occupancyAPI.outside, on_leave: occupancyAPI.onLeave };
    fetchers[activeTab]?.().then((res) => setStudents(res.data.items)).catch(console.error);
  }, [activeTab]);

  if (loading) return <LoadingSpinner />;

  const dailyChart = {
    labels: weekly.map((d) => d.date.slice(5)),
    datasets: [
      { label: 'Inside', data: weekly.map((d) => d.inside), backgroundColor: '#22c55e' },
      { label: 'Outside', data: weekly.map((d) => d.outside), backgroundColor: '#ef4444' },
    ],
  };

  const monthlyChart = {
    labels: monthly.filter((_, i) => i % 3 === 0).map((d) => d.date.slice(5)),
    datasets: [{
      label: 'Hostel Population',
      data: monthly.filter((_, i) => i % 3 === 0).map((d) => d.inside),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59,130,246,0.1)',
      fill: true,
      tension: 0.4,
    }],
  };

  const tabs = [
    { key: 'inside', label: 'Inside Hostel' },
    { key: 'outside', label: 'Outside Hostel' },
    { key: 'on_leave', label: 'On Leave' },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Live Hostel Occupancy</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mb-8">
        <StatCard title="Total Students" value={summary?.total_students} icon="👨‍🎓" color="blue" />
        <StatCard title="Inside" value={summary?.students_inside} icon="🏠" color="green" />
        <StatCard title="Outside" value={summary?.students_outside} icon="🚶" color="red" />
        <StatCard title="On Leave" value={summary?.students_on_leave} icon="📝" color="yellow" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ChartCard title="Daily Hostel Population (Weekly)">
          <Bar data={dailyChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }} />
        </ChartCard>
        <ChartCard title="Monthly Hostel Population">
          <Line data={monthlyChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
        </ChartCard>
      </div>

      <div className="card">
        <div className="flex gap-2 mb-4 border-b pb-3">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.key ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-3 pr-4">Roll No</th>
                <th className="pb-3 pr-4">Name</th>
                <th className="pb-3 pr-4">Department</th>
                <th className="pb-3 pr-4">Room</th>
                <th className="pb-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s) => (
                <tr key={s.roll_no} className="border-b border-gray-50">
                  <td className="py-3 pr-4 font-medium">{s.roll_no}</td>
                  <td className="py-3 pr-4">{s.name}</td>
                  <td className="py-3 pr-4">{s.department}</td>
                  <td className="py-3 pr-4">{s.room_number} ({s.hostel_block})</td>
                  <td className="py-3"><StatusBadge status={s.occupancy_status} /></td>
                </tr>
              ))}
              {students.length === 0 && (
                <tr><td colSpan={5} className="py-8 text-center text-gray-400">No students found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
