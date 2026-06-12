export default function ChartCard({ title, children, className = '' }) {
  return (
    <div className={`card ${className}`}>
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
      <div className="relative" style={{ height: '300px' }}>
        {children}
      </div>
    </div>
  );
}
