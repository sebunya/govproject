import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export default function CitizenLanding() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  const { data: metrics } = useQuery({
    queryKey: ['dashboard-public'],
    queryFn: () => axios.get('/api/dashboard').then(r => r.data),
    staleTime: 30000,
  });

  const { data: services = [] } = useQuery({
    queryKey: ['services-count'],
    queryFn: () => axios.get('/api/services').then(r => r.data as any[]),
    staleTime: 60000,
  });
  const activeCount = (services as any[]).filter((s: any) => s.active).length;
  const totalCount = (services as any[]).length;

  const stats = [
    {
      label: 'Services Available',
      value: activeCount > 0 ? `${activeCount} Active` : '—',
      sub: `${totalCount - activeCount} coming soon`,
    },
    {
      label: 'Avg. Resolution Time',
      value: metrics ? `${metrics.avgResolutionHours >= 24
        ? `${Math.round(metrics.avgResolutionHours / 24 * 10) / 10} days`
        : `${metrics.avgResolutionHours}h`}` : '—',
      sub: 'vs. 14-day SLA target',
    },
    {
      label: 'SLA Compliance',
      value: metrics ? `${metrics.slaCompliancePercent}%` : '—',
      sub: 'Applications resolved on time',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="bg-navy-700 rounded-2xl p-10 text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-5" style={{
          backgroundImage: 'repeating-linear-gradient(45deg, #BF8F00 0, #BF8F00 1px, transparent 0, transparent 50%)',
          backgroundSize: '12px 12px'
        }} />
        <div className="relative z-10">
          <div className="inline-block bg-gold-500 text-white text-xs font-bold px-3 py-1 rounded-full mb-4 uppercase tracking-wider">
            Mbarara District Local Government
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold mb-3 leading-tight">
            Government services that respect your time
          </h1>
          <p className="text-navy-100 text-lg mb-6 max-w-xl opacity-90">
            Apply for permits, register cooperatives, and track your applications — all in one place.
            Transparent, accountable, and designed around you.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => navigate(`/portal/services?persona=${persona}`)}
              className="bg-gold-500 hover:bg-yellow-600 text-white font-bold px-7 py-3 rounded-lg transition-colors text-base"
            >
              Apply for a Service →
            </button>
            <button
              onClick={() => navigate(`/portal/my-applications?persona=${persona}`)}
              className="bg-white bg-opacity-15 hover:bg-opacity-25 text-white font-semibold px-7 py-3 rounded-lg transition-colors border border-white border-opacity-30"
            >
              Track My Applications
            </button>
          </div>
        </div>
      </div>

      {/* Live stats */}
      <div className="grid grid-cols-3 gap-4">
        {stats.map(s => (
          <div key={s.label} className="bg-navy-50 rounded-xl p-4 text-center">
            <div className="text-2xl font-extrabold text-navy-700">{s.value}</div>
            <div className="text-xs font-semibold text-navy-700 mt-0.5">{s.label}</div>
            <div className="text-xs text-gray-500 mt-0.5">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Info cards */}
      <div className="grid md:grid-cols-3 gap-4">
        {[
          {
            icon: '🔒',
            title: 'Your Data, Protected',
            body: 'All data handling is designed to support compliance with the Data Protection and Privacy Act 2019.',
          },
          {
            icon: '⏱',
            title: 'SLA-Bound Officers',
            body: 'Every application has a legal Service Level Agreement. Officers are accountable to the clock.',
          },
          {
            icon: '📋',
            title: 'Full Audit Trail',
            body: 'Every action on your application is logged. You can request a complete audit trace at any time.',
          },
        ].map(c => (
          <div key={c.title} className="card">
            <div className="text-3xl mb-3">{c.icon}</div>
            <h3 className="font-bold text-navy-700 mb-1">{c.title}</h3>
            <p className="text-sm text-gray-600">{c.body}</p>
          </div>
        ))}
      </div>

      {/* How it works */}
      <div>
        <h2 className="text-lg font-bold text-navy-700 mb-4">How it works</h2>
        <div className="grid md:grid-cols-4 gap-4">
          {[
            { step: '1', icon: '📋', title: 'Choose a Service', desc: 'Browse the Service Catalogue and select the permit or licence you need.' },
            { step: '2', icon: '📝', title: 'Submit Your Application', desc: 'Fill in your details. Your identity is verified via NIRA and your tax status via URA.' },
            { step: '3', icon: '👨‍💼', title: 'Officer Review', desc: 'A District Officer reviews your documents within the SLA window. You are notified at every step.' },
            { step: '4', icon: '🎉', title: 'Receive Your Permit', desc: 'Download your official permit certificate. For fee-based services, pay securely via mobile money.' },
          ].map(s => (
            <div key={s.step} className="relative bg-white border border-gray-200 rounded-xl p-4">
              <div className="absolute -top-3 -left-3 w-7 h-7 bg-gold-500 rounded-full flex items-center justify-center text-white text-xs font-extrabold">{s.step}</div>
              <div className="text-2xl mb-2 mt-1">{s.icon}</div>
              <h3 className="font-bold text-navy-700 text-sm mb-1">{s.title}</h3>
              <p className="text-xs text-gray-600 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick reference tracker */}
      <div className="bg-navy-50 rounded-xl p-5 border border-navy-100">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-xl">🔍</span>
          <h3 className="font-bold text-navy-700">Already applied? Track your reference</h3>
        </div>
        <div className="flex gap-2">
          <input
            id="quick-track"
            className="form-input font-mono uppercase flex-1 text-sm"
            placeholder="NGS-2026-0001"
            onKeyDown={e => {
              if (e.key === 'Enter') {
                const val = (e.target as HTMLInputElement).value.trim().toUpperCase();
                if (val) navigate(`/track?persona=${persona}&ref=${val}`);
              }
            }}
          />
          <button
            onClick={() => {
              const el = document.getElementById('quick-track') as HTMLInputElement | null;
              const val = el?.value.trim().toUpperCase() || '';
              if (val) navigate(`/track?persona=${persona}&ref=${val}`);
              else navigate(`/track?persona=${persona}`);
            }}
            className="btn-primary shrink-0"
          >
            Track →
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">No account required. Enter your reference number to check status.</p>
      </div>

      {/* Active applications alert */}
      {metrics && metrics.activeApplications > 0 && (
        <div className="bg-gold-50 border border-gold-500 rounded-xl p-4 flex items-center gap-3">
          <span className="text-gold-500 text-xl">📌</span>
          <div>
            <p className="text-sm font-semibold text-yellow-900">
              {metrics.activeApplications} application{metrics.activeApplications !== 1 ? 's' : ''} currently being processed
            </p>
            <p className="text-xs text-yellow-800 mt-0.5">
              Officers are reviewing submissions. Track yours under "My Applications".
            </p>
          </div>
          <button
            onClick={() => navigate(`/portal/my-applications?persona=${persona}`)}
            className="ml-auto btn-secondary text-sm py-1.5 shrink-0"
          >
            Track →
          </button>
        </div>
      )}
    </div>
  );
}
