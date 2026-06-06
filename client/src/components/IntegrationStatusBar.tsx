import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface IntegStatus { configured: boolean; provider: string; }
interface HealthData {
  integrations?: { sms?: IntegStatus; email?: IntegStatus; whatsapp?: IntegStatus; pesapal?: IntegStatus };
  notificationsSentLive?: number;
}

export default function IntegrationStatusBar() {
  const { data } = useQuery<HealthData>({
    queryKey: ['health'],
    queryFn: () => axios.get('/api/health').then(r => r.data),
    refetchInterval: 30000,
    staleTime: 15000,
  });

  if (!data?.integrations) return null;
  const { sms, email, whatsapp, pesapal } = data.integrations;
  const channels = [
    { key: 'sms', label: 'SMS', icon: '📱', info: sms },
    { key: 'email', label: 'Email', icon: '📧', info: email },
    { key: 'whatsapp', label: 'WhatsApp', icon: '💬', info: whatsapp },
    { key: 'pesapal', label: 'Pesapal', icon: '💳', info: pesapal },
  ];
  const anyLive = channels.some(c => c.info?.configured);

  return (
    <div className="bg-navy-900 border-b border-navy-700 px-4 py-1 flex items-center gap-4 text-xs overflow-x-auto">
      <span className="text-navy-300 shrink-0 font-semibold uppercase tracking-wide">Integrations</span>
      {channels.map(({ key, label, icon, info }) => (
        <div key={key} className="flex items-center gap-1 shrink-0">
          <span>{icon}</span>
          <span className={info?.configured ? 'text-status-green font-semibold' : 'text-navy-400'}>
            {label}
          </span>
          <span className={`px-1 rounded text-xs ${info?.configured ? 'bg-status-greenBg text-status-green' : 'bg-navy-800 text-navy-400'}`}>
            {info?.configured ? 'LIVE' : 'SIM'}
          </span>
        </div>
      ))}
      {anyLive && data.notificationsSentLive !== undefined && (
        <span className="ml-auto text-navy-400 shrink-0">{data.notificationsSentLive} live sent</span>
      )}
    </div>
  );
}
