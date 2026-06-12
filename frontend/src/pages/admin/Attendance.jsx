import { useEffect, useState } from 'react';
import { attendanceAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function Attendance() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [importResult, setImportResult] = useState(null);

  const fetchLogs = () => {
    attendanceAPI.list({ per_page: 50 }).then((res) => setLogs(res.data.items)).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchLogs(); }, []);

  const handleCSVImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const res = await attendanceAPI.importCSV(file);
      setImportResult(res.data);
      fetchLogs();
    } catch (err) {
      alert(err.response?.data?.error || 'Import failed');
    }
    e.target.value = '';
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Biometric Attendance</h1>
        <label className="btn-primary cursor-pointer">
          Import CSV
          <input type="file" accept=".csv" className="hidden" onChange={handleCSVImport} />
        </label>
      </div>

      {importResult && (
        <div className="card mb-6 bg-green-50 border-green-200">
          <p className="text-green-800">Imported {importResult.imported} records.</p>
          {importResult.errors?.length > 0 && (
            <ul className="text-red-600 text-sm mt-2">{importResult.errors.map((e, i) => <li key={i}>{e}</li>)}</ul>
          )}
        </div>
      )}

      <div className="card mb-6">
        <h3 className="font-semibold mb-2">CSV Format</h3>
        <code className="text-xs bg-gray-100 p-3 rounded block">
          roll_no,entry_time,exit_time,attendance_date,status<br />
          CS001,2024-06-11T08:30:00,,2024-06-11,inside
        </code>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="pb-3 pr-4">Roll No</th>
              <th className="pb-3 pr-4">Date</th>
              <th className="pb-3 pr-4">Entry</th>
              <th className="pb-3 pr-4">Exit</th>
              <th className="pb-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((a) => (
              <tr key={a.id} className="border-b border-gray-50">
                <td className="py-3 pr-4 font-medium">{a.roll_no}</td>
                <td className="py-3 pr-4">{a.attendance_date}</td>
                <td className="py-3 pr-4">{a.entry_time?.slice(11, 19) || '—'}</td>
                <td className="py-3 pr-4">{a.exit_time?.slice(11, 19) || '—'}</td>
                <td className="py-3"><StatusBadge status={a.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
