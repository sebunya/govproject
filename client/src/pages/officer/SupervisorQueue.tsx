import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import StatusBadge from '../../components/StatusBadge';
import SlaTimer from '../../components/SlaTimer';

export default function SupervisorQueue() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'supervisor';
  const qc = useQueryClient();
  const [expanded, setExpanded] = useState<number | null>(null);
  const [decision, setDecision] = useState<Record<number, 'approved' | 'rejected'>>({});
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState<number | null>(null);
  const [recentDecision, setRecentDecision] = useState<{ ref: string; decision: string } | null>(null);

  const { data: apps = [], isLoading } = useQuery({
    queryKey: ['supervisor-queue'],
    queryFn: () => axios.get('/api/applications?persona=supervisor').then(r => r.data),
    refetchInterval: 5000,
  });

  const submitDecision = async (appId: number, refNum: string) => {
    setSubmitting(appId);
    try {
      await axios.patch(`/api/applications/${appId}/supervisor-decision`, {
        decision: decision[appId],
        notes: notes[appId] || '',
      });
      qc.invalidateQueries({ queryKey: ['supervisor-queue'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
      setExpanded(null);
      setRecentDecision({ ref: refNum, decision: decision[appId] });
      setTimeout(() => setRecentDecision(null), 5000);
    } finally {
      setSubmitting(null);
    }
  };

  if (isLoading) return (
    <div className="flex items-center justify-center py-20">
      <div className="animate-spin h-8 w-8 border-4 border-navy-700 border-t-transparent rounded-full" />
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Decision confirmation toast */}
      {recentDecision && (
        <div className={`fixed top-16 right-4 z-50 rounded-xl shadow-xl p-4 flex items-center gap-3 text-white text-sm font-semibold transition-all ${
          recentDecision.decision === 'approved' ? 'bg-status-green' : 'bg-status-red'
        }`}>
          <span className="text-lg">{recentDecision.decision === 'approved' ? '✅' : '❌'}</span>
          <div>
            <div>{recentDecision.ref} — Decision recorded</div>
            <div className="font-normal text-xs opacity-90 mt-0.5">
              {recentDecision.decision === 'approved' ? 'Application approved and permit granted' : 'Application rejected'}
            </div>
          </div>
          <button onClick={() => setRecentDecision(null)} className="ml-2 opacity-70 hover:opacity-100">✕</button>
        </div>
      )}

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-navy-700">Supervisor Review Queue</h1>
          <div className="w-16 h-0.5 bg-gold-500 mt-1 mb-2" />
          <p className="text-gray-600">Nakamya Grace · Senior District Officer · Mbarara District</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-extrabold text-navy-700">{apps.length}</div>
          <div className="text-xs text-gray-500">Awaiting countersignature</div>
        </div>
      </div>

      {apps.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-3">✅</div>
          <h3 className="font-bold text-gray-700">No applications pending countersignature</h3>
          <p className="text-gray-500 text-sm mt-1">All officer decisions have been reviewed.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {apps.map((app: any) => (
            <div key={app.id} className="card">
              <div
                className="flex items-start gap-4 cursor-pointer"
                onClick={() => setExpanded(expanded === app.id ? null : app.id)}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className="font-extrabold text-navy-700">{app.referenceNumber}</span>
                    <StatusBadge status={app.status} />
                    {app.officerDecision && (
                      <span className="badge-green">Officer: {app.officerDecision}</span>
                    )}
                  </div>
                  <p className="font-semibold text-sm">{app.fullName}</p>
                  <p className="text-sm text-gray-600">{app.cooperativeName}</p>
                  {app.officerNotes && (
                    <p className="text-xs text-gray-500 mt-1 italic">Officer notes: "{app.officerNotes}"</p>
                  )}
                </div>
                <div className="shrink-0 w-44">
                  <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResolveHours} label="Resolution SLA" />
                </div>
                <div className="text-navy-700 text-xl self-center">{expanded === app.id ? '↑' : '↓'}</div>
              </div>

              {expanded === app.id && (
                <div className="mt-5 pt-5 border-t border-gray-100 space-y-4">
                  {/* Summary */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    {[
                      { label: 'Applicant', val: app.fullName },
                      { label: 'District', val: app.district },
                      { label: 'Cooperative', val: app.cooperativeName },
                      { label: 'Tax Status', val: app.taxStatus },
                    ].map(f => (
                      <div key={f.label}>
                        <span className="text-xs text-gray-500 block">{f.label}</span>
                        <span className="font-medium">{f.val}</span>
                      </div>
                    ))}
                  </div>

                  <div className="bg-navy-50 rounded-lg p-3">
                    <p className="text-xs font-semibold text-navy-700 mb-1">{app.assignedOfficerName || 'Officer'}'s Recommendation</p>
                    <p className="text-sm font-bold text-status-green capitalize">{app.officerDecision} — Forwarded for countersignature</p>
                    {app.officerNotes && <p className="text-xs text-gray-600 mt-1">"{app.officerNotes}"</p>}
                  </div>

                  {/* Decision */}
                  <div>
                    <p className="form-label">Supervisor Decision</p>
                    <div className="flex gap-3 mb-3">
                      {[
                        { val: 'approved', label: '✅ Countersign & Approve' },
                        { val: 'rejected', label: '❌ Reject' },
                      ].map(opt => (
                        <button
                          key={opt.val}
                          onClick={() => setDecision(prev => ({ ...prev, [app.id]: opt.val as any }))}
                          className={`flex-1 border-2 rounded-lg py-2.5 font-semibold text-sm transition-colors ${
                            decision[app.id] === opt.val
                              ? opt.val === 'approved' ? 'bg-status-green text-white border-status-green' : 'bg-status-red text-white border-status-red'
                              : 'border-gray-300 text-gray-700 hover:border-navy-700'
                          }`}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                    <textarea
                      className="form-input mb-3"
                      rows={2}
                      placeholder="Supervisor notes (optional for approval)…"
                      value={notes[app.id] || ''}
                      onChange={e => setNotes(prev => ({ ...prev, [app.id]: e.target.value }))}
                    />
                    <button
                      onClick={() => submitDecision(app.id, app.referenceNumber)}
                      disabled={!decision[app.id] || submitting === app.id}
                      className={`font-semibold px-6 py-2.5 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${
                        decision[app.id] === 'rejected' ? 'bg-status-red' : 'bg-status-green'
                      }`}
                    >
                      {submitting === app.id ? 'Submitting…' : 'Confirm Decision'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
