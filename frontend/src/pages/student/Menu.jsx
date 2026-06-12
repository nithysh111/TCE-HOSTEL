import { useEffect, useState } from 'react';
import { menusAPI } from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function StudentMenu() {
  const [todayMenu, setTodayMenu] = useState([]);
  const [weeklyMenu, setWeeklyMenu] = useState([]);
  const [specialMenus, setSpecialMenus] = useState([]);
  const [activeTab, setActiveTab] = useState('today');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([menusAPI.today(), menusAPI.weekly(), menusAPI.special()])
      .then(([todayRes, weekRes, specialRes]) => {
        setTodayMenu(todayRes.data.items);
        setWeeklyMenu(weekRes.data.items);
        setSpecialMenus(specialRes.data.items);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  const tabs = [
    { key: 'today', label: "Today's Menu" },
    { key: 'weekly', label: 'Weekly Menu' },
    { key: 'special', label: 'Special Meals' },
  ];

  const groupByDate = (menus) => {
    const grouped = {};
    menus.forEach((m) => {
      if (!grouped[m.menu_date]) grouped[m.menu_date] = [];
      grouped[m.menu_date].push(m);
    });
    return grouped;
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Food Menu</h1>

      <div className="flex gap-2 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${activeTab === tab.key ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600'}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'today' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {todayMenu.map((m) => (
            <div key={m.id} className={`card ${m.is_special ? 'border-yellow-300 bg-yellow-50' : ''}`}>
              <h3 className="font-semibold text-lg text-gray-800">{m.meal_type}</h3>
              <p className="text-gray-600 mt-2">{m.menu_items}</p>
              {m.description && <p className="text-xs text-gray-400 mt-2">{m.description}</p>}
            </div>
          ))}
          {todayMenu.length === 0 && <p className="text-gray-400">No menu for today</p>}
        </div>
      )}

      {activeTab === 'weekly' && (
        <div className="space-y-6">
          {Object.entries(groupByDate(weeklyMenu)).map(([date, menus]) => (
            <div key={date} className="card">
              <h3 className="font-semibold text-gray-800 mb-3">{date}</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {menus.map((m) => (
                  <div key={m.id} className="bg-gray-50 p-3 rounded-lg">
                    <p className="font-medium text-sm">{m.meal_type}</p>
                    <p className="text-sm text-gray-600">{m.menu_items}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'special' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {specialMenus.map((m) => (
            <div key={m.id} className="card border-yellow-300 bg-yellow-50">
              <span className="badge badge-yellow mb-2">Special Meal</span>
              <h3 className="font-semibold">{m.menu_title} — {m.meal_type}</h3>
              <p className="text-sm text-gray-500">{m.menu_date}</p>
              <p className="text-gray-600 mt-2">{m.menu_items}</p>
              {m.description && <p className="text-sm text-gray-500 mt-1">{m.description}</p>}
            </div>
          ))}
          {specialMenus.length === 0 && <p className="text-gray-400">No special meals scheduled</p>}
        </div>
      )}
    </div>
  );
}
