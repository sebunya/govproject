import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface IntegStatus { configured: boolean; provider: string; }
interface HealthData {
  integrations?: { sms?: IntegStatus; email?: IntegStatus; whatsapp?: IntegStatus; pesapal?: IntegStatus };
  notificationsSentLive?: number;
  status?: string;
}

const channels = [
  { key: 'sms',      label: 'SMS',      icon: '📱' },
  { key: 'email',    label: 'Email',    icon: '📧' },
  { key: 'whatsapp', label: 'WhatsApp', icon: '💬' },
  { key: 'pesapal',  label: 'Pesapal',  icon: '💳' },
] as const;

export default function IntegrationStatusBar() {
  const [collapsed, setCollapsed] = useState(false);

  const { data, isError } = useQuery<HealthData>({
    queryKey: ['health'],
    queryFn: () => axios.get('/api/health').then(r => r.data),
    refetchInterval: 30_000,
    staleTime: 15_000,
    retry: 1,
  });

  if (isError) return null;

  const integ = data?.integrations;
  const anyLive = integ && channels.some(c => integ[c.key]?.configured);
  const isOnline = data?.status === 'ok';

  return (
    <div
      className="integration-bar bg-navy-800 border-b border-navy-600 overflow-hidden"
      aria-label="Integration status"
      role="status"
    >
      <div className="max-w-7xl mx-auto px-3 sm:px-4">
        <div className="flex items-center gap-3 h-7">
          {/* Server status dot */}
          <div className="flex items-center gap-1.5 shrink-0">
            <span
              className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                !data ? 'bg-gray-500' : isOnline ? 'bg-status-green animate-pulse' : 'bg-status-red'
              }`}
              aria-hidden="true"
            />
            <span className="text-2xs text-navy-300 font-semibold uppercase tracking-wider hidden sm:inline">
              {!data ? 'Connecting…' : isOnline ? 'Server OK' : 'Offline'}
            </span>
          </div>

          <span className="text-navy-600 text-xs" aria-hidden="true">|</span>

          {/* Channels */}
          <div className={`flex items-center gap-3 flex-1 overflow-hidden transition-all ${collapsed ? 'opacity-0 w-0' : 'opacity-100'}`}>
            {channels.map(({ key, label, icon }) => {
              const info = integ?.[key];
              const live = info?.configured;
              return (
                <div
                  key={key}
                  className="flex items-center gap-1 shrink-0"
                  title={`${label}: ${live ? 'Live — ' + (info?.provider || '') : 'Simulated'}`}
                >
                  <span className="text-xs" aria-hidden="true">{icon}</span>
                  <span className={`text-2xs font-semibold hidden md:inline ${live ? 'text-status-green' : 'text-navy-400'}`}>
                    {label}
                  </span>
                  <span
                    className={`text-2xs px-1 rounded font-bold leading-tight ${
                      !info ? 'text-navy-600'
                      : live ? 'text-status-green bg-status-greenBg'
                      : 'text-navy-500 bg-navy-700'
                    }`}
                    aria-label={`${label} ${live ? 'live' : 'simulated'}`}
                  >
                    {!info ? '…' : live ? 'LIVE' : 'SIM'}
                  </span>
                </div>
              );
            })}

            {anyLive && data?.notificationsSentLive !== undefined && data.notificationsSentLive > 0 && (
              <span className="text-2xs text-navy-400 ml-auto hidden lg:inline shrink-0">
                {data.notificationsSentLive} live sent
              </span>
            )}
          </div>

          {/* Collapse toggle */}
          <button
            onClick={() => setCollapsed(v => !v)}
            className="text-navy-400 hover:text-navy-200 transition-colors ml-auto shrink-0 p-0.5"
            aria-label={collapsed ? 'Show integration status' : 'Hide integration status'}
            title={collapsed ? 'Show' : 'Hide'}
          >
            <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor" aria-hidden="true">
              {collapsed
                ? <path d="M1 3l4 4 4-4" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round"/>
                : <path d="M1 7l4-4 4 4" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round"/>
              }
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
