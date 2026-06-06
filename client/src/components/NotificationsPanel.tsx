import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const CHANNEL_ICON: Record<string, string> = {
  sms: '📱',
  email: '📧',
  portal: '🌐',
  internal: '🔔',
};
const CHANNEL_LABEL: Record<string, string> = {
  sms: 'SMS',
  email: 'Email',
  portal: 'Portal',
  internal: 'Internal',
};
const TYPE_COLOR: Record<string, string> = {
  citizen: 'bg-navy-50 border-navy-100',
  officer: 'bg-gold-50 border-gold-500',
  supervisor: 'bg-status-orangeBg border-status-orange',
  system: 'bg-gray-50 border-gray-200',
};

export default function NotificationsPanel({ applicationId }: { applicationId: number }) {
  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ['notifications', applicationId],
    queryFn: () => axios.get(`/api/applications/${applicationId}/notifications`).then(r => r.data),
    refetchInterval: 5000,
  });

  if (isLoading) return (
    <div className="card">
      <h2 className="section-title">Notification Log</h2>
      <div className="text-sm text-gray-400">Loading…</div>
    </div>
  );

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4 pb-2 border-b-2 border-gold-500">
        <h2 className="text-lg font-bold text-navy-700">Notification Log</h2>
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-status-green animate-pulse inline-block" />
          <span className="text-xs text-gray-500">{notifications.length} events</span>
        </div>
      </div>

      {notifications.length === 0 ? (
        <p className="text-sm text-gray-400">No notifications yet.</p>
      ) : (
        <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
          {(notifications as any[]).map((n: any) => (
            <div key={n.id} className={`rounded-lg border p-3 ${TYPE_COLOR[n.type] || TYPE_COLOR.system}`}>
              <div className="flex items-start gap-2">
                <span className="text-base shrink-0 mt-0.5">{CHANNEL_ICON[n.channel] || '📩'}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-0.5">
                    <span className="text-xs font-bold text-navy-700 uppercase tracking-wide">
                      {CHANNEL_LABEL[n.channel] || n.channel}
                    </span>
                    <span className="text-xs text-gray-500">→ {n.recipient}</span>
                    <span className={`text-xs font-semibold px-1.5 py-0.5 rounded-full ${
                      n.status === 'simulated_sent' ? 'bg-status-greenBg text-status-green'
                      : n.status === 'simulated_failed' ? 'bg-status-redBg text-status-red'
                      : 'bg-gray-100 text-gray-500'
                    }`}>
                      {n.status === 'simulated_sent' ? '✓ Simulated Sent' : n.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-700 leading-relaxed">{n.message}</p>
                  <p className="text-xs text-gray-400 mt-1">{new Date(n.createdAt).toLocaleString('en-UG')}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-3 pt-3 border-t border-gray-100 flex items-start gap-2 text-xs text-yellow-800 bg-gold-50 rounded-lg p-2">
        <span className="text-gold-500 shrink-0">⚠</span>
        <span>Prototype simulation only. No live SMS, email or portal notification was sent.</span>
      </div>
    </div>
  );
}
