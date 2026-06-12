const statusStyles = {
  Open: 'badge-red',
  'In Progress': 'badge-yellow',
  Resolved: 'badge-green',
  inside: 'badge-green',
  outside: 'badge-red',
  on_leave: 'badge-yellow',
  pending: 'badge-yellow',
  Pending: 'badge-yellow',
  approved: 'badge-green',
  rejected: 'badge-red',
  Paid: 'badge-green',
  Overdue: 'badge-red',
  Success: 'badge-green',
  Failed: 'badge-red',
  Refunded: 'badge-gray',
  low: 'badge-gray',
  medium: 'badge-blue',
  high: 'badge-red',
};

export default function StatusBadge({ status }) {
  const style = statusStyles[status] || 'badge-gray';
  return <span className={`badge ${style}`}>{status}</span>;
}
