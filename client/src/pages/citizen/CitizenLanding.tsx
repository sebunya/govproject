import { useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export default function CitizenLanding() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';
  const trackRef = useRef<HTMLInputElement>(null);

  const { data: metrics } = useQuery({
    queryKey: ['dashboard-public'],
    queryFn: () => axios.get('/api/dashboard').then(r => r.data),
    staleTime: 30_000,
  });

  const { data: services = [] } = useQuery({
    queryKey: ['services-count'],
    queryFn: () => axios.get('/api/services').then(r => r.data as any[]),
    staleTime: 60_000,
  });
  const activeCount = (services as any[]).filter((s: any) => s.active).length;
  const totalCount = (services as any[]).length;

  const handleTrack = () => {
    const val = trackRef.current?.value.trim().toUpperCase() || '';
    navigate(val ? `/track?persona=${persona}&ref=${val}` : `/track?persona=${persona}`);
  };

  const kpiStats = [
    {
      label: 'Services Available',
      value: activeCount > 0 ? `${activeCount}` : '—',
      unit: 'Active',
      sub: `${totalCount - activeCount} coming soon`,
      icon: '📋',
    },
    {
      label: 'Avg. Resolution',
      value: metrics
        ? metrics.avgResolutionHours >= 24
          ? `${(metrics.avgResolutionHours / 24).toFixed(1)}`
          : `${metrics.avgResolutionHours}`
        : '—',
      unit: metrics?.avgResolutionHours >= 24 ? 'days' : 'hrs',
      sub: 'vs. 14-day SLA target',
      icon: '⏱',
    },
    {
      label: 'SLA Compliance',
      value: metrics ? `${metrics.slaCompliancePercent}` : '—',
      unit: '%',
      sub: 'Applications resolved on time',
      icon: '✅',
    },
  ];

  return (
    <div className="space-y-6 sm:space-y-8">

      {/* ── Hero ────────────────────────────────────────────────────────── */}
      <section
        aria-label="Welcome banner"
        className="bg-navy-700 rounded-2xl text-white relative overflow-hidden"
      >
        {/* Decorative pattern */}
        <div
          className="absolute inset-0 opacity-[0.04] pointer-events-none"
          style={{ backgroundImage: 'repeating-linear-gradient(45deg,#BF8F00 0,#BF8F00 1px,transparent 0,transparent 50%)', backgroundSize: '12px 12px' }}
          aria-hidden="true"
        />
        <div className="relative z-10 px-6 sm:px-10 py-8 sm:py-10">
          <div className="inline-flex items-center gap-2 bg-gold-500 text-white text-xs font-bold px-3 py-1.5 rounded-full mb-4 uppercase tracking-wider">
            <span aria-hidden="true">🇺🇬</span>
            Mbarara District Local Government
          </div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold mb-3 leading-tight text-balance">
            Government services that respect your time
          </h1>
          <p className="text-navy-100 text-base sm:text-lg mb-6 max-w-xl opacity-90 leading-relaxed text-pretty">
            Apply for permits, register cooperatives, and track your applications — all in one place.
            Transparent, accountable, and designed around you.
          </p>
          <div className="flex flex-col xs:flex-row gap-3">
            <button
              onClick={() => navigate(`/portal/services?persona=${persona}`)}
              className="btn-gold text-base px-6 py-3"
            >
              Apply for a Service
              <span aria-hidden="true">→</span>
            </button>
            <button
              onClick={() => navigate(`/portal/my-applications?persona=${persona}`)}
              className="inline-flex items-center justify-center gap-2 bg-white/15 hover:bg-white/25 text-white
                         font-semibold px-6 py-3 rounded-lg transition-colors border border-white/30 text-base"
              style={{ minHeight: '44px' }}
            >
              My Applications
            </button>
          </div>
        </div>
      </section>

      {/* ── Live KPI Stats ───────────────────────────────────────────────── */}
      <section aria-label="Service statistics">
        <div className="grid grid-cols-3 gap-3 sm:gap-4">
          {kpiStats.map(s => (
            <div key={s.label} className="bg-navy-50 border border-navy-100 rounded-xl p-3 sm:p-4 text-center">
              <div className="text-lg sm:text-2xl mb-1" aria-hidden="true">{s.icon}</div>
              <div className="flex items-baseline justify-center gap-1">
                <span className="text-xl sm:text-2xl font-extrabold text-navy-700">{s.value}</span>
                <span className="text-xs sm:text-sm font-semibold text-navy-600">{s.unit}</span>
              </div>
              <div className="text-2xs sm:text-xs font-semibold text-navy-700 mt-0.5 leading-tight">{s.label}</div>
              <div className="text-2xs sm:text-xs text-gray-500 mt-0.5 hidden xs:block">{s.sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Active Applications Alert ────────────────────────────────────── */}
      {metrics && metrics.activeApplications > 0 && (
        <div
          role="status"
          className="bg-gold-50 border border-gold-500 rounded-xl p-4 flex items-center gap-3"
        >
          <span className="text-gold-500 text-xl flex-shrink-0" aria-hidden="true">📌</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-yellow-900">
              {metrics.activeApplications} application{metrics.activeApplications !== 1 ? 's' : ''} currently being processed
            </p>
            <p className="text-xs text-yellow-800 mt-0.5 hidden sm:block">
              Officers are reviewing submissions. Track yours under "My Applications".
            </p>
          </div>
          <button
            onClick={() => navigate(`/portal/my-applications?persona=${persona}`)}
            className="btn-secondary text-xs py-1.5 px-3 flex-shrink-0"
          >
            View →
          </button>
        </div>
      )}

      {/* ── How It Works ─────────────────────────────────────────────────── */}
      <section aria-labelledby="how-it-works-heading">
        <h2 id="how-it-works-heading" className="text-lg font-bold text-navy-700 mb-4">How it works</h2>
        <ol className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4" aria-label="Application process steps">
          {[
            { step: '1', icon: '📋', title: 'Choose a Service', desc: 'Browse the Service Catalogue and select the permit or licence you need.' },
            { step: '2', icon: '📝', title: 'Submit Your Application', desc: 'Fill in your details. Your identity is verified via NIRA and your tax status via URA.' },
            { step: '3', icon: '👨‍💼', title: 'Officer Review', desc: 'A District Officer reviews your documents within the SLA window. You are notified at every step.' },
            { step: '4', icon: '🎉', title: 'Receive Your Permit', desc: 'Download your official permit certificate. Pay securely via mobile money for fee-based services.' },
          ].map(s => (
            <li key={s.step} className="relative bg-white border border-gray-200 rounded-xl p-4 list-none">
              <div
                className="absolute -top-3 -left-3 w-7 h-7 bg-gold-500 rounded-full flex items-center justify-center text-white text-xs font-extrabold shadow-sm"
                aria-hidden="true"
              >
                {s.step}
              </div>
              <div className="text-2xl mb-2 mt-1" aria-hidden="true">{s.icon}</div>
              <h3 className="font-bold text-navy-700 text-sm mb-1">{s.title}</h3>
              <p className="text-xs text-gray-600 leading-relaxed">{s.desc}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* ── Info Cards ───────────────────────────────────────────────────── */}
      <section aria-label="Key features" className="grid sm:grid-cols-3 gap-4">
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
          <article key={c.title} className="card hover:shadow-card-hover transition-shadow">
            <div className="text-3xl mb-3" aria-hidden="true">{c.icon}</div>
            <h3 className="font-bold text-navy-700 mb-1.5">{c.title}</h3>
            <p className="text-sm text-gray-600 leading-relaxed">{c.body}</p>
          </article>
        ))}
      </section>

      {/* ── Quick Reference Tracker ──────────────────────────────────────── */}
      <section aria-labelledby="tracker-heading" className="bg-navy-50 rounded-xl p-5 border border-navy-100">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-xl" aria-hidden="true">🔍</span>
          <h2 id="tracker-heading" className="font-bold text-navy-700">Already applied? Track your reference</h2>
        </div>
        <div className="flex gap-2">
          <label htmlFor="quick-track" className="sr-only">Enter your application reference number</label>
          <input
            ref={trackRef}
            id="quick-track"
            type="text"
            className="form-input font-mono uppercase flex-1 text-sm"
            placeholder="NGS-2026-0001"
            autoComplete="off"
            spellCheck={false}
            onKeyDown={e => { if (e.key === 'Enter') handleTrack(); }}
          />
          <button onClick={handleTrack} className="btn-primary flex-shrink-0">
            Track →
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">No account required. Enter your reference number to check status.</p>
      </section>

    </div>
  );
}
