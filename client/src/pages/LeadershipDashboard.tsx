import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import Header from '../components/Header';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
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

export default function LeadershipDashboard() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => axios.get('/api/dashboard').then(r => r.data),
    refetchInterval: 10000,
  });

  const printReport = () => {
    window.print();
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
          <div className="flex gap-3">
            <div className="text-right text-xs text-gray-500">
              <div>Auto-refreshes every 10s</div>
              <div className="mt-0.5">Last updated: {new Date().toLocaleTimeString('en-UG')}</div>
            </div>
            <button onClick={printReport} className="btn-secondary text-sm py-2 flex items-center gap-2 print:hidden">
              📄 Weekly Scorecard PDF
            </button>
          </div>
        </div>

        {isLoading || !metrics ? (
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
                    <Line type="monotone" dataKey="submitted" stroke="#1F3864" strokeWidth={2} dot={{ r: 4 }} name="Submitted" />
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
                    <Bar dataKey="total" fill="#1F3864" name="Total" radius={[3,3,0,0]} />
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
                        <tr key={d.district} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 font-medium">{d.district}</td>
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

            {/* Print-only scorecard header */}
            <div className="hidden print:block space-y-4 mt-8 border-t pt-8">
              <h2 className="text-xl font-bold text-navy-700">Weekly Executive Scorecard</h2>
              <p className="text-sm text-gray-600">Mbarara District Local Government · NileGov Stack · Generated: {new Date().toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
              <p className="text-xs text-gray-500">This report is generated from live operational data within the NileGov Stack platform and is designed to support internal governance and accountability reporting.</p>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
