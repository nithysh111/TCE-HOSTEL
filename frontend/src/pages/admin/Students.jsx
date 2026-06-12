import { useEffect, useState } from 'react';
import { studentsAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function Students() {
  const [students, setStudents] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [searchRoll, setSearchRoll] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [activeView, setActiveView] = useState('list');
  const [loading, setLoading] = useState(true);
  const [searchError, setSearchError] = useState('');

  useEffect(() => {
    Promise.all([studentsAPI.list({ per_page: 100 }), studentsAPI.rooms()])
      .then(([listRes, roomsRes]) => {
        setStudents(listRes.data.items);
        setRooms(roomsRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    setSearchError('');
    setSearchResult(null);
    if (!searchRoll.trim()) return;
    try {
      const res = await studentsAPI.search(searchRoll.trim());
      setSearchResult(res.data);
    } catch {
      setSearchError('Student not found');
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Student Information</h1>

      <div className="card mb-6">
        <form onSubmit={handleSearch} className="flex gap-3">
          <input
            className="input-field flex-1"
            placeholder="Search by Roll Number (e.g., CS001)"
            value={searchRoll}
            onChange={(e) => setSearchRoll(e.target.value)}
          />
          <button type="submit" className="btn-primary">Search</button>
        </form>
        {searchError && <p className="text-red-500 text-sm mt-2">{searchError}</p>}
        {searchResult && (
          <div className="mt-4 p-4 bg-primary-50 rounded-lg grid grid-cols-2 md:grid-cols-4 gap-4">
            <div><p className="text-xs text-gray-500">Roll No</p><p className="font-medium">{searchResult.roll_no}</p></div>
            <div><p className="text-xs text-gray-500">Name</p><p className="font-medium">{searchResult.name}</p></div>
            <div><p className="text-xs text-gray-500">Department</p><p className="font-medium">{searchResult.department}</p></div>
            <div><p className="text-xs text-gray-500">Year</p><p className="font-medium">{searchResult.year}</p></div>
            <div><p className="text-xs text-gray-500">Room</p><p className="font-medium">{searchResult.room_number}</p></div>
            <div><p className="text-xs text-gray-500">Block</p><p className="font-medium">{searchResult.hostel_block}</p></div>
            <div><p className="text-xs text-gray-500">Phone</p><p className="font-medium">{searchResult.phone_number}</p></div>
            <div><p className="text-xs text-gray-500">Status</p><StatusBadge status={searchResult.occupancy_status} /></div>
          </div>
        )}
      </div>

      <div className="flex gap-2 mb-4">
        <button onClick={() => setActiveView('list')} className={`px-4 py-2 rounded-lg text-sm font-medium ${activeView === 'list' ? 'bg-primary-600 text-white' : 'bg-gray-100'}`}>All Students</button>
        <button onClick={() => setActiveView('rooms')} className={`px-4 py-2 rounded-lg text-sm font-medium ${activeView === 'rooms' ? 'bg-primary-600 text-white' : 'bg-gray-100'}`}>Room Allocation</button>
      </div>

      {activeView === 'list' ? (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-3 pr-4">Roll No</th>
                <th className="pb-3 pr-4">Name</th>
                <th className="pb-3 pr-4">Department</th>
                <th className="pb-3 pr-4">Year</th>
                <th className="pb-3 pr-4">Room</th>
                <th className="pb-3">Block</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s) => (
                <tr key={s.id} className="border-b border-gray-50">
                  <td className="py-3 pr-4 font-medium">{s.roll_no}</td>
                  <td className="py-3 pr-4">{s.name}</td>
                  <td className="py-3 pr-4">{s.department}</td>
                  <td className="py-3 pr-4">{s.year}</td>
                  <td className="py-3 pr-4">{s.room_number}</td>
                  <td className="py-3">{s.hostel_block}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {rooms.map((room) => (
            <div key={`${room.hostel_block}-${room.room_number}`} className="card">
              <h3 className="font-semibold text-gray-800">{room.hostel_block} — Room {room.room_number}</h3>
              <p className="text-sm text-gray-500 mb-3">{room.students.length} student(s)</p>
              <ul className="space-y-1">
                {room.students.map((s) => (
                  <li key={s.roll_no} className="text-sm text-gray-700">{s.roll_no} — {s.name}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
