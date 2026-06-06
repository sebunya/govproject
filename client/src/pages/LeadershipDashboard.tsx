import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import Header from '../components/Header';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid,
  PolarAngleAxis, Radar,
} from 'recharts';

function StatCard({ value, label, sub, color }: { value: string | number; label: string; sub?: string; color?: string }) {
  return (
    <div className="stat-card">
      <div className={`text-3xl font-extrabold ${color || 'text-navy-700'}`}>{value}</div>
      <div className="text-sm font-semibold text-gray-700 mt-1">{label}</div>
      {sub && <div className="text-xs text-gray-500 mt-0.5">{sub}</div>}
    </div>
  );
}

// Chart palette derived from Uganda national colours
const DISTRICT_COLORS: Record<string, string> = {
  Mbarara: '#C8102E',   // Uganda red — featured district
  Kampala: '#1A1A1A',   // Uganda black
  Gulu:    '#D4A400',   // Uganda gold variant
  Jinja:   '#7B3F00',   // earth brown (neutral differentiation)
};

export default function LeadershipDashboard() {
  const [drillDistrict, setDrillDistrict] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'reports'>('dashboard');

  const { data: metrics, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => axios.get('/api/dashboard').then(r => r.data),
    refetchInterval: 10000,
  });

  const { data: districtTrend } = useQuery({
    queryKey: ['district-trend'],
    queryFn: () => axios.get('/api/dashboard/district-trend').then(r => r.data),
    refetchInterval: 30000,
  });

  const [lastUpdated, setLastUpdated] = useState(new Date());
  useEffect(() => {
    if (metrics) setLastUpdated(new Date());
  }, [metrics]);

  const { data: officerStats = [] } = useQuery({
    queryKey: ['officer-stats'],
    queryFn: () => axios.get('/api/dashboard/officers').then(r => r.data),
    refetchInterval: 15000,
  });

  const { data: reports } = useQuery({
    queryKey: ['me-reports'],
    queryFn: () => axios.get('/api/dashboard/reports').then(r => r.data),
    refetchInterval: 30000,
  });

  const printReport = () => window.print();

  const exportCSV = () => {
    if (!metrics) return;
    const rows = [
      ['Metric', 'Value'],
      ['Processed Today', metrics.todayProcessed],
      ['Processed This Week', metrics.weekProcessed],
      ['Avg Resolution (hours)', metrics.avgResolutionHours],
      ['SLA Compliance %', metrics.slaCompliancePercent],
      ['Active Applications', metrics.activeApplications],
      [],
      ['District', 'Total', 'SLA Compliant', 'Avg Hours'],
      ...(metrics.districtStats || []).map((d: any) => [d.district, d.total, d.onTime, d.avgHours ?? '—']),
      [],
      ['Officer', 'Total', 'Active', 'SLA %', 'Avg Resolution (h)'],
      ...(officerStats as any[]).map((o: any) => [o.name, o.total, o.active, o.slaCompliance, o.avgResolutionHours ?? '—']),
    ];
    const csv = rows.map(r => r.join(',')).join('\n');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = `nilegov-dashboard-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div>
      <Header persona="leadership" />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-extrabold text-navy-700">Executive Operations Dashboard</h1>
              <span className="flex items-center gap-1.5 bg-status-greenBg text-status-green text-xs font-bold px-2.5 py-1 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-status-green animate-pulse inline-block" />
                LIVE
              </span>
            </div>
            <div className="w-16 h-0.5 bg-gold-500 mb-2" />
            <p className="text-gray-600">Mbarara District Local Government · Real-time service delivery metrics</p>
          </div>
          <div className="flex gap-3 items-start">
            <div className="text-right text-xs text-gray-500">
              <div className="flex items-center gap-1 justify-end">
                <span className="w-1.5 h-1.5 rounded-full bg-status-green animate-pulse inline-block" />
                Auto-refreshes every 10s
              </div>
              <div className="mt-0.5 font-semibold tabular-nums">
                Last updated: {lastUpdated.toLocaleTimeString('en-UG')}
              </div>
            </div>
            <button onClick={exportCSV} className="btn-secondary text-sm py-2 flex items-center gap-2 print:hidden">
              📊 Export CSV
            </button>
            <button onClick={printReport} className="btn-secondary text-sm py-2 flex items-center gap-2 print:hidden">
              📄 Print Scorecard
            </button>
          </div>
        </div>

        {/* Tab switcher */}
        <div className="flex gap-2">
          {[
            { id: 'dashboard', label: '📊 Live Dashboard' },
            { id: 'reports', label: '📋 M&E Reports' },
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`px-4 py-2 rounded-full text-sm font-bold transition-colors ${activeTab === t.id ? 'bg-navy-700 text-white' : 'bg-white border border-navy-700 text-navy-700'}`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* M&E Reports Tab */}
        {activeTab === 'reports' && reports && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Total Applications', value: reports.totals?.total || 0, sub: 'All time' },
                { label: 'Approval Rate', value: `${reports.totals?.approvalRate || 0}%`, sub: 'Approved / total resolved', color: 'text-status-green' },
                { label: 'Avg Citizen Rating', value: reports.totals?.avgRating ? `${reports.totals.avgRating}★` : '—', sub: 'Service satisfaction score', color: 'text-gold-500' },
                { label: 'Escalations', value: reports.totals?.escalated || 0, sub: 'Flagged for priority review', color: reports.totals?.escalated > 0 ? 'text-status-red' : 'text-status-green' },
              ].map(s => (
                <div key={s.label} className="stat-card">
                  <div className={`text-3xl font-extrabold ${s.color || 'text-navy-700'}`}>{s.value}</div>
                  <div className="text-sm font-semibold text-gray-700 mt-1">{s.label}</div>
                  {s.sub && <div className="text-xs text-gray-500 mt-0.5">{s.sub}</div>}
                </div>
              ))}
            </div>

            {/* Notification stats */}
            {reports.notifications && (
              <div className="card">
                <h2 className="section-title">Notification Delivery (Module 06)</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="bg-navy-50 rounded-xl p-4 text-center">
                    <div className="text-2xl font-extrabold text-navy-700">{reports.notifications.total}</div>
                    <div className="text-xs text-gray-500 mt-1">Total Sent</div>
                  </div>
                  <div className="bg-status-greenBg rounded-xl p-4 text-center">
                    <div className="text-2xl font-extrabold text-status-green">{reports.notifications.simulated_sent || 0}</div>
                    <div className="text-xs text-gray-500 mt-1">Simulated Sent</div>
                  </div>
                  <div className="bg-status-redBg rounded-xl p-4 text-center">
                    <div className="text-2xl font-extrabold text-status-red">{reports.notifications.simulated_failed || 0}</div>
                    <div className="text-xs text-gray-500 mt-1">Failed</div>
                  </div>
                  <div className="bg-gold-50 rounded-xl p-4 text-center">
                    <div className="text-2xl font-extrabold text-gold-500">{reports.notifications.byChannel?.sms || 0}</div>
                    <div className="text-xs text-gray-500 mt-1">SMS</div>
                  </div>
                </div>
                <div className="space-y-2">
                  {Object.entries(reports.notifications.byChannel || {}).map(([ch, count]) => (
                    <div key={ch} className="flex items-center gap-3">
                      <span className="text-sm font-semibold text-gray-700 w-20 capitalize">{ch}</span>
                      <div className="flex-1 bg-gray-100 rounded-full h-2">
                        <div
                          className="h-2 rounded-full bg-navy-700"
                          style={{ width: `${reports.notifications.total > 0 ? Math.round((count as number / reports.notifications.total) * 100) : 0}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 w-8 text-right">{count as number}</span>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-yellow-800 bg-gold-50 border border-gold-500 rounded-lg p-2 mt-3">
                  ⚠ Prototype simulation only. No live SMS, email or portal notifications were sent. Production integration would use NITA-U certified channels.
                </p>
              </div>
            )}

            {/* Payment stats */}
            {reports.payments && (
              <div className="card">
                <h2 className="section-title">Payment Revenue (Module 07 — Pesapal Sandbox)</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="bg-status-greenBg rounded-xl p-4 text-center">
                    <div className="text-2xl font-extrabold text-status-green">{Number(reports.payments.totalVerifiedAmount || 0).toLocaleString()}</div>
                    <div className="text-xs text-gray-500 mt-1">UGX Verified Revenue</div>
                  </div>
                  <div className="bg-navy-50 rounded-xl p-4 text-center">
                    <div className="text-2xl font-extrabold text-navy-700">{reports.payments.verifiedCount || 0}</div>
                    <div className="text-xs text-gray-500 mt-1">Payments Verified</div>
                  </div>
                  <div className="bg-status-orangeBg rounded-xl p-4 text-center">
                    <div className="text-2xl font-extrabold text-status-orange">{reports.payments.pendingCount || 0}</div>
                    <div className="text-xs text-gray-500 mt-1">Pending</div>
                  </div>
                  <div className="bg-navy-50 rounded-xl p-4 text-center">
                    <div className="text-2xl font-extrabold text-navy-700">UGX 120k</div>
                    <div className="text-xs text-gray-500 mt-1">Per Licence Fee</div>
                  </div>
                </div>
                <div className="space-y-2">
                  {Object.entries(reports.payments.byMethod || {}).map(([method, count]) => (
                    <div key={method} className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 capitalize">{method.replace(/_/g, ' ')}</span>
                      <span className="font-bold text-navy-700">{count as number} payments</span>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-yellow-800 bg-gold-50 border border-gold-500 rounded-lg p-2 mt-3">
                  ⚠ Prototype simulation only. No live payment was processed. Pesapal API 3.0 Sandbox Pattern.
                </p>
              </div>
            )}

            {/* Service breakdown */}
            {reports.byService && (
              <div className="card">
                <h2 className="section-title">Applications by Service (Module 08 — Service Catalogue)</h2>
                <div className="space-y-3">
                  {reports.byService.map((svc: any) => (
                    <div key={svc.serviceCode} className="border border-gray-100 rounded-xl p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-navy-700">{svc.serviceName || svc.serviceCode}</span>
                        <span className="text-sm font-bold text-gray-700">{svc.total} total</span>
                      </div>
                      <div className="flex gap-4 text-xs text-gray-500">
                        <span className="text-status-green">✓ {svc.approved} approved</span>
                        <span className="text-status-red">✕ {svc.rejected} rejected</span>
                        <span className="text-status-orange">⏱ {svc.active} active</span>
                        {svc.avgResolutionHours > 0 && <span>⏰ avg {svc.avgResolutionHours}h</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Officer workload in M&E tab */}
            {reports.officerWorkload && reports.officerWorkload.length > 0 && (
              <div className="card">
                <h2 className="section-title">Officer Workload & Performance (Module 04 — Assignment)</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 text-xs uppercase text-gray-500 font-semibold">
                        <th className="text-left py-2">Officer</th>
                        <th className="text-right py-2">Total</th>
                        <th className="text-right py-2">Active</th>
                        <th className="text-right py-2">Resolved</th>
                        <th className="text-right py-2">Approved</th>
                        <th className="text-right py-2">SLA %</th>
                        <th className="text-right py-2">Avg Res.</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(reports.officerWorkload as any[]).map((o: any) => (
                        <tr key={o.id} className="border-b border-gray-100 hover:bg-navy-50">
                          <td className="py-2 font-medium">{o.name}</td>
                          <td className="py-2 text-right">{o.total}</td>
                          <td className="py-2 text-right text-status-orange font-semibold">{o.active}</td>
                          <td className="py-2 text-right">{o.resolved}</td>
                          <td className="py-2 text-right text-status-green font-semibold">{o.approved ?? '—'}</td>
                          <td className="py-2 text-right">
                            <span className={`font-bold ${(o.slaCompliance ?? 100) >= 90 ? 'text-status-green' : 'text-status-orange'}`}>
                              {o.slaCompliance ?? 100}%
                            </span>
                          </td>
                          <td className="py-2 text-right text-gray-600">{o.avgResolutionHours > 0 ? `${o.avgResolutionHours}h` : '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="bg-gold-50 border border-gold-500 rounded-xl p-4 text-sm text-yellow-800">
              <strong>Module 09 — M&E Reporting:</strong> This snapshot is generated from live operational data in NileGov Stack.
              In production, it would feed into the Ministry of Local Government IFMIS reporting framework and OPM performance scorecards.
            </div>
          </div>
        )}

        {activeTab === 'dashboard' && isLoading && !metrics && (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin h-10 w-10 border-4 border-navy-700 border-t-transparent rounded-full" />
          </div>
        )}

        {activeTab === 'dashboard' && !isLoading && metrics && (
        <div className="space-y-8">

        {false ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin h-10 w-10 border-4 border-navy-700 border-t-transparent rounded-full" />
          </div>
        ) : (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <StatCard value={metrics.todayProcessed} label="Processed Today" sub="Applications resolved" />
              <StatCard value={metrics.weekProcessed} label="Processed This Week" sub="Last 7 days" />
              <StatCard value={`${metrics.avgResolutionHours}h`} label="Avg. Resolution Time" sub={`vs. ${14 * 24}h SLA`} color={metrics.avgResolutionHours <= 14 * 24 ? 'text-status-green' : 'text-status-red'} />
              <StatCard value={`${metrics.slaCompliancePercent}%`} label="SLA Compliance" sub="Resolved within target" color={metrics.slaCompliancePercent >= 90 ? 'text-status-green' : metrics.slaCompliancePercent >= 70 ? 'text-status-orange' : 'text-status-red'} />
              <StatCard value={metrics.activeApplications} label="Active Applications" sub="In-progress" color="text-navy-700" />
            </div>

            {/* Charts row */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Weekly trend */}
              <div className="card">
                <h2 className="section-title">Weekly Application Trend</h2>
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={metrics.weeklyTrend} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="week" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="submitted" stroke="#C8102E" strokeWidth={2} dot={{ r: 4 }} name="Submitted" />
                    <Line type="monotone" dataKey="resolved" stroke="#1F6F3F" strokeWidth={2} dot={{ r: 4 }} name="Resolved" />
                    <Line type="monotone" dataKey="slaBreached" stroke="#C00000" strokeWidth={2} dot={{ r: 4 }} name="SLA Breached" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* District distribution */}
              <div className="card">
                <h2 className="section-title">Applications by District</h2>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={metrics.districtStats} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="district" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="total" fill="#C8102E" name="Total" radius={[3,3,0,0]} />
                    <Bar dataKey="approved" fill="#1F6F3F" name="Approved" radius={[3,3,0,0]} />
                    <Bar dataKey="slaBreached" fill="#C00000" name="SLA Breached" radius={[3,3,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Bottlenecks */}
            <div className="card">
              <h2 className="section-title">Active Bottlenecks</h2>
              <div className="grid md:grid-cols-3 gap-4">
                {metrics.bottlenecks.map((b: any) => (
                  <div key={b.stage} className={`rounded-xl p-4 ${b.count > 0 ? 'bg-status-orangeBg border border-status-orange' : 'bg-gray-50 border border-gray-200'}`}>
                    <div className={`text-2xl font-extrabold ${b.count > 0 ? 'text-status-orange' : 'text-gray-400'}`}>
                      {b.count}
                    </div>
                    <div className={`text-sm font-semibold mt-1 ${b.count > 0 ? 'text-status-orange' : 'text-gray-400'}`}>{b.stage}</div>
                    {b.count > 0 && (
                      <div className="text-xs text-gray-600 mt-1">Avg wait: {b.avgWaitHours}h</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* District stats table */}
            <div className="card">
              <h2 className="section-title">District Performance Table</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 text-gray-500 font-semibold text-xs uppercase">District</th>
                      <th className="text-right py-2 text-gray-500 font-semibold text-xs uppercase">Total</th>
                      <th className="text-right py-2 text-gray-500 font-semibold text-xs uppercase">Approved</th>
                      <th className="text-right py-2 text-gray-500 font-semibold text-xs uppercase">SLA Breached</th>
                      <th className="text-right py-2 text-gray-500 font-semibold text-xs uppercase">Compliance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.districtStats.map((d: any) => {
                      const compliance = d.total > 0 ? Math.round(((d.total - d.slaBreached) / d.total) * 100) : 100;
                      return (
                        <tr
                          key={d.district}
                          className={`border-b border-gray-100 hover:bg-navy-50 cursor-pointer transition-colors ${drillDistrict === d.district ? 'bg-navy-50' : ''}`}
                          onClick={() => setDrillDistrict(drillDistrict === d.district ? null : d.district)}
                        >
                          <td className="py-3 font-medium flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full inline-block" style={{ background: DISTRICT_COLORS[d.district] || '#888' }} />
                            {d.district}
                            {drillDistrict === d.district && <span className="text-xs text-navy-700 font-normal ml-1">▲ trend</span>}
                          </td>
                          <td className="py-3 text-right">{d.total}</td>
                          <td className="py-3 text-right text-status-green font-semibold">{d.approved}</td>
                          <td className="py-3 text-right">
                            {d.slaBreached > 0 ? (
                              <span className="text-status-red font-semibold">{d.slaBreached}</span>
                            ) : (
                              <span className="text-status-green">0</span>
                            )}
                          </td>
                          <td className="py-3 text-right">
                            <span className={`font-semibold ${compliance >= 90 ? 'text-status-green' : compliance >= 70 ? 'text-status-orange' : 'text-status-red'}`}>
                              {compliance}%
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* District SLA Trend Drill-Down */}
            {drillDistrict && districtTrend && districtTrend.trend[drillDistrict] && (
              <div className="card border-navy-700 border-2">
                <div className="flex items-center justify-between mb-1">
                  <h2 className="section-title mb-0">
                    SLA Compliance Trend — {drillDistrict} District
                  </h2>
                  <button onClick={() => setDrillDistrict(null)} className="text-gray-400 hover:text-gray-600 text-sm">✕ Close</button>
                </div>
                <p className="text-xs text-gray-500 mb-4">5-week rolling window · Click a district row to drill down</p>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={districtTrend.trend[drillDistrict]} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="week" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} unit="%" domain={[0, 100]} />
                    <Tooltip formatter={(v: any) => `${v}%`} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="compliance"
                      stroke={DISTRICT_COLORS[drillDistrict] || '#C8102E'}
                      strokeWidth={3}
                      dot={{ r: 5 }}
                      name="SLA Compliance %"
                    />
                  </LineChart>
                </ResponsiveContainer>
                <div className="grid grid-cols-4 gap-3 mt-4">
                  {districtTrend.trend[drillDistrict].slice(-1).map((w: any) => (
                    <div key="latest" className="bg-navy-50 rounded-lg p-3 text-center">
                      <div className={`text-xl font-extrabold ${w.compliance >= 90 ? 'text-status-green' : w.compliance >= 70 ? 'text-status-orange' : 'text-status-red'}`}>
                        {w.compliance}%
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5">Current SLA</div>
                    </div>
                  ))}
                  <div className="bg-navy-50 rounded-lg p-3 text-center">
                    <div className="text-xl font-extrabold text-navy-700">{districtTrend.trend[drillDistrict].reduce((s: number, w: any) => s + w.total, 0)}</div>
                    <div className="text-xs text-gray-500 mt-0.5">Total (5 wks)</div>
                  </div>
                  <div className="bg-navy-50 rounded-lg p-3 text-center">
                    <div className="text-xl font-extrabold text-status-red">{districtTrend.trend[drillDistrict].reduce((s: number, w: any) => s + w.slaBreached, 0)}</div>
                    <div className="text-xs text-gray-500 mt-0.5">SLA Breached</div>
                  </div>
                  <div className="bg-navy-50 rounded-lg p-3 text-center">
                    <div className="text-xl font-extrabold text-status-green">{districtTrend.trend[drillDistrict].reduce((s: number, w: any) => s + w.onTime, 0)}</div>
                    <div className="text-xs text-gray-500 mt-0.5">On Time</div>
                  </div>
                </div>
              </div>
            )}

            {/* Category SLA */}
            <div className="card">
              <h2 className="section-title">SLA Compliance by Service Category</h2>
              <div className="space-y-3">
                {metrics.categoryStats.map((cat: any) => {
                  const pct = cat.total > 0 ? Math.round(((cat.total - cat.slaBreached) / cat.total) * 100) : 100;
                  return (
                    <div key={cat.category}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium">{cat.category}</span>
                        <span className={`font-bold ${pct >= 90 ? 'text-status-green' : pct >= 70 ? 'text-status-orange' : 'text-status-red'}`}>
                          {pct}% compliant
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span>{cat.total} total</span>
                        <span>·</span>
                        <span className="text-status-red">{cat.slaBreached} breached</span>
                        <span>·</span>
                        <span>Avg {cat.avgResolutionHours}h resolution</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                        <div
                          className={`h-2 rounded-full ${pct >= 90 ? 'bg-status-green' : pct >= 70 ? 'bg-status-orange' : 'bg-status-red'}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Responsible Officers */}
            {officerStats.length > 0 && (
              <div className="card">
                <h2 className="section-title">Officer Performance & Workload</h2>
                <p className="text-xs text-gray-500 mb-4">Officers responsible for SLA outcomes · Mbarara District Agricultural Office</p>
                <div className="space-y-3">
                  {(officerStats as any[]).map((o: any) => (
                    <div key={o.id} className="border border-gray-100 rounded-xl p-4 hover:border-navy-700 transition-colors">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white text-sm ${o.role === 'supervisor' ? 'bg-ug-red' : 'bg-navy-700'}`}>
                            {o.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2)}
                          </div>
                          <div>
                            <p className="font-bold text-sm text-gray-800">{o.name}</p>
                            <p className="text-xs text-gray-500 capitalize">{o.role === 'supervisor' ? 'Senior District Officer' : 'District Agricultural Officer'} · {o.district}</p>
                          </div>
                        </div>
                        <div className="flex gap-6 text-center text-xs">
                          <div>
                            <div className="text-lg font-extrabold text-navy-700">{o.total}</div>
                            <div className="text-gray-500">Total</div>
                          </div>
                          <div>
                            <div className="text-lg font-extrabold text-status-orange">{o.active}</div>
                            <div className="text-gray-500">Active</div>
                          </div>
                          <div>
                            <div className={`text-lg font-extrabold ${o.slaCompliance >= 90 ? 'text-status-green' : o.slaCompliance >= 70 ? 'text-status-orange' : 'text-status-red'}`}>
                              {o.slaCompliance}%
                            </div>
                            <div className="text-gray-500">SLA</div>
                          </div>
                          <div>
                            <div className={`text-lg font-extrabold ${o.slaBreached > 0 ? 'text-status-red' : 'text-status-green'}`}>
                              {o.slaBreached}
                            </div>
                            <div className="text-gray-500">Breached</div>
                          </div>
                          <div>
                            <div className="text-lg font-extrabold text-gray-700">{o.avgResolutionHours > 0 ? `${o.avgResolutionHours}h` : '—'}</div>
                            <div className="text-gray-500">Avg Res.</div>
                          </div>
                        </div>
                      </div>
                      {o.total > 0 && (
                        <div className="mt-3">
                          <div className="flex justify-between text-xs text-gray-500 mb-1">
                            <span>SLA compliance rate</span>
                            <span>{o.onTime}/{o.resolved} resolved on time</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div
                              className={`h-1.5 rounded-full ${o.slaCompliance >= 90 ? 'bg-status-green' : o.slaCompliance >= 70 ? 'bg-status-orange' : 'bg-status-red'}`}
                              style={{ width: `${o.slaCompliance}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Print-only scorecard header */}
            <div className="hidden print:block space-y-4 mt-8 border-t pt-8">
              <h2 className="text-xl font-bold text-navy-700">Weekly Executive Scorecard</h2>
              <p className="text-sm text-gray-600">Mbarara District Local Government · NileGov Stack · Generated: {new Date().toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
              <p className="text-xs text-gray-500">This report is generated from live operational data within the NileGov Stack platform and is designed to support internal governance and accountability reporting.</p>
            </div>
          </>
        )}
        </div>
        )}
      </main>
    </div>
  );
}
