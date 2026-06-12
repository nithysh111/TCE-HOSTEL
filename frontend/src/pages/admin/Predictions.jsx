import { useEffect, useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { predictionsAPI } from '../../services/api';
import StatCard from '../../components/StatCard';
import ChartCard from '../../components/ChartCard';
import LoadingSpinner from '../../components/LoadingSpinner';

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

export default function Predictions() {
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [wastage, setWastage] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isHoliday, setIsHoliday] = useState(false);
  const [wastageForm, setWastageForm] = useState({ report_date: new Date().toISOString().split('T')[0], meal_type: 'Lunch', prepared_quantity: '', consumed_quantity: '', notes: '' });

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      predictionsAPI.food({ is_holiday: isHoliday }),
      predictionsAPI.history(30),
      predictionsAPI.wastage(),
    ]).then(([predRes, histRes, wastRes]) => {
      setPrediction(predRes.data);
      setHistory(histRes.data.items);
      setWastage(wastRes.data.items);
    }).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [isHoliday]);

  const handleWastageSubmit = async (e) => {
    e.preventDefault();
    await predictionsAPI.createWastage(wastageForm);
    setWastageForm({ report_date: new Date().toISOString().split('T')[0], meal_type: 'Lunch', prepared_quantity: '', consumed_quantity: '', notes: '' });
    fetchData();
  };

  if (loading) return <LoadingSpinner />;

  const predChart = prediction ? {
    labels: ['Breakfast', 'Lunch', 'Dinner'],
    datasets: [{
      label: 'Predicted Students',
      data: [prediction.predicted_breakfast, prediction.predicted_lunch, prediction.predicted_dinner],
      backgroundColor: ['#60a5fa', '#34d399', '#fbbf24'],
    }],
  } : null;

  const historyChart = history.length > 0 ? {
    labels: history.map((h) => h.prediction_date.slice(5)),
    datasets: [
      { label: 'Breakfast', data: history.map((h) => h.predicted_breakfast), borderColor: '#60a5fa', tension: 0.3 },
      { label: 'Lunch', data: history.map((h) => h.predicted_lunch), borderColor: '#34d399', tension: 0.3 },
      { label: 'Dinner', data: history.map((h) => h.predicted_dinner), borderColor: '#fbbf24', tension: 0.3 },
    ],
  } : null;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">AI Food Prediction</h1>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={isHoliday} onChange={(e) => setIsHoliday(e.target.checked)} />
          Mark as Holiday
        </label>
      </div>

      {prediction && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-4">
            <StatCard title="Predicted Breakfast" value={prediction.predicted_breakfast} icon="🌅" color="blue" subtitle={`Inside: ${prediction.students_inside}`} />
            <StatCard title="Predicted Lunch" value={prediction.predicted_lunch} icon="☀️" color="green" subtitle={`On Leave: ${prediction.students_on_leave}`} />
            <StatCard title="Predicted Dinner" value={prediction.predicted_dinner} icon="🌙" color="yellow" subtitle={`Model: ${prediction.model_loaded ? 'ML Active' : 'Rule-based'}`} />
          </div>
          {prediction.model_metrics && (
            <div className="card mb-6 text-sm text-gray-600">
              <p className="font-medium text-gray-800 mb-2">Model Evaluation Metrics (R²)</p>
              <div className="flex gap-6">
                {Object.entries(prediction.model_metrics).map(([k, v]) => (
                  <span key={k}>{k.replace('_count', '')}: R²={v.r2}</span>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {predChart && (
          <ChartCard title="Today's Meal Predictions">
            <Bar data={predChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
          </ChartCard>
        )}
        {historyChart && (
          <ChartCard title="Prediction History (30 Days)">
            <Line data={historyChart} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }} />
          </ChartCard>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Record Food Wastage</h3>
          <form onSubmit={handleWastageSubmit} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div><label className="label">Date</label><input type="date" className="input-field" value={wastageForm.report_date} onChange={(e) => setWastageForm({ ...wastageForm, report_date: e.target.value })} required /></div>
              <div><label className="label">Meal</label><select className="input-field" value={wastageForm.meal_type} onChange={(e) => setWastageForm({ ...wastageForm, meal_type: e.target.value })}><option>Breakfast</option><option>Lunch</option><option>Dinner</option></select></div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div><label className="label">Prepared</label><input type="number" className="input-field" value={wastageForm.prepared_quantity} onChange={(e) => setWastageForm({ ...wastageForm, prepared_quantity: e.target.value })} required /></div>
              <div><label className="label">Consumed</label><input type="number" className="input-field" value={wastageForm.consumed_quantity} onChange={(e) => setWastageForm({ ...wastageForm, consumed_quantity: e.target.value })} required /></div>
            </div>
            <button type="submit" className="btn-primary">Save Wastage Report</button>
          </form>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Recent Wastage Reports</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {wastage.slice(0, 10).map((w) => (
              <div key={w.id} className="flex justify-between text-sm border-b border-gray-50 py-2">
                <span>{w.report_date} — {w.meal_type}</span>
                <span className="text-red-600 font-medium">Wasted: {w.wasted_quantity}</span>
              </div>
            ))}
            {wastage.length === 0 && <p className="text-gray-400 text-sm">No wastage reports yet</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
