import { useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import StatusBadge from '../../components/StatusBadge';
import SlaTimer from '../../components/SlaTimer';
import ApiInteropPanel from '../../components/ApiInteropPanel';
import PaymentPanel from '../../components/PaymentPanel';
import NotificationsPanel from '../../components/NotificationsPanel';
import { SkeletonCard, SkeletonTable } from '../../components/Skeleton';

const SOP_ITEMS_COOP = [
  { id: 1, label: 'NIN verified via NIRA', check: (a: any) => a.nin?.length > 5 },
  { id: 2, label: 'Applicant identity confirmed', check: (a: any) => !!a.fullName },
  { id: 3, label: 'Cooperative name provided', check: (a: any) => !!a.cooperativeName },
  { id: 4, label: 'URA tax clearance confirmed', check: (a: any) => a.taxStatus === 'Compliant' },
  { id: 5, label: 'Cooperative Bylaws document attached', check: (a: any) => a.documents?.length >= 1 },
  { id: 6, label: 'Member Roster attached', check: (a: any) => a.documents?.length >= 2 },
  { id: 7, label: 'Citizen consent recorded', check: (a: any) => !!a.consentTimestamp },
  { id: 8, label: 'Application within district jurisdiction (Mbarara)', check: (a: any) => a.district === 'Mbarara' },
];

const SOP_ITEMS_TRADING = [
  { id: 1, label: 'NIN verified via NIRA', check: (a: any) => a.nin?.length > 5 },
  { id: 2, label: 'Applicant identity confirmed', check: (a: any) => !!a.fullName },
  { id: 3, label: 'Business name provided', check: (a: any) => !!(a.businessName || a.cooperativeName) },
  { id: 4, label: 'URA tax clearance confirmed', check: (a: any) => a.taxStatus === 'Compliant' },
  { id: 5, label: 'Business registration document attached', check: (a: any) => a.documents?.length >= 1 },
  { id: 6, label: 'Service fee paid', check: (a: any) => a.paymentStatus === 'verified' },
  { id: 7, label: 'Citizen consent recorded', check: (a: any) => !!a.consentTimestamp },
  { id: 8, label: 'Application within district jurisdiction (Mbarara)', check: (a: any) => a.district === 'Mbarara' },
];

function DocVerifyRow({ doc, appId, onRefresh }: { doc: any; appId: string; onRefresh: () => void }) {
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState('');
  const [showNotes, setShowNotes] = useState(false);

  const verify = async (status: 'verified' | 'rejected') => {
    setLoading(true);
    try {
      await axios.patch(`/api/documents/${doc.id}/verify`, { status, notes });
      onRefresh();
      setShowNotes(false);
    } finally {
      setLoading(false);
    }
  };

  const statusColor = doc.verificationStatus === 'verified' ? 'bg-status-greenBg border-status-green'
    : doc.verificationStatus === 'rejected' ? 'bg-status-redBg border-status-red'
    : 'bg-navy-50 border-navy-100';

  return (
    <div className={`border rounded-xl p-4 transition-colors ${statusColor}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📄</span>
          <div>
            <p className="text-sm font-semibold text-gray-800">{doc.originalName}</p>
            <p className="text-xs text-gray-500">{new Date(doc.uploadedAt).toLocaleString('en-UG')}</p>
            {doc.verificationStatus && doc.verificationStatus !== 'pending' && (
              <p className={`text-xs font-bold mt-0.5 ${doc.verificationStatus === 'verified' ? 'text-status-green' : 'text-status-red'}`}>
                {doc.verificationStatus === 'verified' ? '✓ Verified' : '✕ Rejected'}
                {doc.verifiedBy && ` by ${doc.verifiedBy}`}
              </p>
            )}
            {doc.verificationNotes && (
              <p className="text-xs text-gray-500 italic mt-0.5">"{doc.verificationNotes}"</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <a href={`/uploads/${doc.storedName}`} target="_blank" rel="noreferrer" className="text-navy-700 text-xs font-semibold hover:underline px-2 py-1 border border-navy-200 rounded">
            View
          </a>
          {(!doc.verificationStatus || doc.verificationStatus === 'pending') && (
            <>
              <button
                onClick={() => verify('verified')}
                disabled={loading}
                className="text-xs font-bold px-3 py-1 rounded-lg bg-status-green text-white hover:opacity-90 disabled:opacity-50"
              >
                ✓ Verify
              </button>
              <button
                onClick={() => setShowNotes(!showNotes)}
                disabled={loading}
                className="text-xs font-bold px-3 py-1 rounded-lg bg-status-red text-white hover:opacity-90 disabled:opacity-50"
              >
                ✕ Reject
              </button>
            </>
          )}
        </div>
      </div>
      {showNotes && (
        <div className="mt-3 flex gap-2">
          <input
            className="form-input text-xs flex-1"
            placeholder="Rejection reason…"
            value={notes}
            onChange={e => setNotes(e.target.value)}
          />
          <button
            onClick={() => verify('rejected')}
            disabled={loading || !notes.trim()}
            className="btn-primary text-xs py-1.5 px-3 shrink-0"
          >
            Confirm
          </button>
        </div>
      )}
    </div>
  );
}

export default function ReviewInterface() {
  const { id } = useParams<{ id: string }>();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'officer';
  const navigate = useNavigate();
  const qc = useQueryClient();

  const [decision, setDecision] = useState<'approved' | 'rejected' | 'more_info_requested' | ''>('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [sopChecks, setSopChecks] = useState<Record<number, boolean>>({});
  const [escalating, setEscalating] = useState(false);
  const [reassignOfficerId, setReassignOfficerId] = useState('');
  const [reassigning, setReassigning] = useState(false);

  const { data: app, isLoading, refetch } = useQuery({
    queryKey: ['application', id],
    queryFn: () => axios.patch(`/api/applications/${id}/claim`).then(r => r.data),
  });

  const { data: officers = [] } = useQuery({
    queryKey: ['officers'],
    queryFn: () => axios.get('/api/officers').then(r => r.data),
  });

  const submitDecision = async () => {
    if (!decision) return;
    setSubmitting(true);
    try {
      await axios.patch(`/api/applications/${id}/officer-decision`, { decision, notes });
      qc.invalidateQueries({ queryKey: ['officer-queue'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
      navigate(`/desk?persona=${persona}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleEscalate = async () => {
    setEscalating(true);
    try {
      await axios.patch(`/api/applications/${id}/escalate`);
      refetch();
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    } finally {
      setEscalating(false);
    }
  };

  const handleReassign = async () => {
    if (!reassignOfficerId) return;
    setReassigning(true);
    try {
      await axios.patch(`/api/applications/${id}/reassign`, { officerId: Number(reassignOfficerId) });
      refetch();
    } finally {
      setReassigning(false);
    }
  };

  if (isLoading || !app) return (
    <div className="space-y-6" aria-busy="true" aria-label="Loading application…">
      <SkeletonCard />
      <SkeletonTable rows={8} cols={2} />
      <SkeletonCard />
    </div>
  );

  const isTrading = app.serviceCode === 'trading-licence';
  const SOP_ITEMS = isTrading ? SOP_ITEMS_TRADING : SOP_ITEMS_COOP;

  const sopResults = SOP_ITEMS.map(item => ({
    ...item,
    passed: sopChecks[item.id] !== undefined ? sopChecks[item.id] : item.check(app),
  }));
  const allSopPassed = sopResults.every(s => s.passed);

  const slaElapsed = (Date.now() - new Date(app.submittedAt).getTime()) / 3600000;
  const slaPct = Math.min(100, Math.round((slaElapsed / app.slaResolveHours) * 100));
  const shouldEscalate = slaPct >= 75 && app.escalationState !== 'escalated';

  const niraData = app.nin ? { fullName: app.fullName, dateOfBirth: app.dateOfBirth, district: app.district, gender: app.gender, nin: app.nin, _simulated: true } : null;
  const uraData = app.taxStatus ? { taxStatus: app.taxStatus, clearanceValidUntil: app.taxClearanceValidUntil, _simulated: true } : null;

  return (
    <div className="space-y-6">
      <div>
        <button onClick={() => navigate(`/desk?persona=${persona}`)} className="text-sm text-navy-700 hover:underline mb-2 block">← Task Queue</button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-extrabold text-navy-700">Review: {app.referenceNumber}</h1>
            <div className="w-16 h-0.5 bg-gold-500 mt-1 mb-1" />
            <div className="flex items-center gap-2 flex-wrap">
              <StatusBadge status={app.status} />
              {app.escalationState === 'escalated' && (
                <span className="bg-status-red text-white text-xs font-bold px-2 py-1 rounded-full">🚨 ESCALATED</span>
              )}
              {isTrading && <span className="bg-navy-100 text-navy-700 text-xs font-bold px-2 py-1 rounded-full">🏪 Trading Licence</span>}
            </div>
          </div>
          <div className="w-48">
            <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResponseHours} label="Response SLA" />
            <div className="mt-2">
              <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResolveHours} label="Resolution SLA" />
            </div>
          </div>
        </div>
      </div>

      {/* SLA escalation warning */}
      {shouldEscalate && (
        <div className="bg-status-redBg border-2 border-status-red rounded-xl p-4 flex items-center justify-between gap-4">
          <div>
            <p className="font-bold text-status-red">⚠ SLA at {slaPct}% — Escalation Recommended</p>
            <p className="text-sm text-gray-700">This application is approaching SLA breach. Escalate to supervisor for priority handling.</p>
          </div>
          <button
            onClick={handleEscalate}
            disabled={escalating}
            className="bg-status-red text-white font-bold text-sm px-4 py-2 rounded-lg hover:opacity-90 shrink-0"
          >
            {escalating ? 'Escalating…' : '🚨 Escalate Now'}
          </button>
        </div>
      )}

      {app.escalationState === 'escalated' && (
        <div className="bg-status-redBg border border-status-red rounded-xl p-4">
          <p className="font-bold text-status-red text-sm">🚨 Escalated to Supervisor</p>
          <p className="text-xs text-gray-700 mt-0.5">This application has been flagged for supervisor priority review. Supervisor has been notified.</p>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main details */}
        <div className="lg:col-span-2 space-y-4">
          {/* Applicant */}
          <div className="card">
            <h2 className="section-title">Applicant Details</h2>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {[
                { label: 'Full Name', val: app.fullName },
                { label: 'NIN', val: app.nin },
                { label: 'Date of Birth', val: app.dateOfBirth },
                { label: 'District of Origin', val: app.district },
                { label: 'Gender', val: app.gender },
                { label: 'Consent Timestamp', val: app.consentTimestamp ? new Date(app.consentTimestamp).toLocaleString('en-UG') : '—' },
              ].map(f => (
                <div key={f.label}>
                  <span className="text-xs text-gray-500 block">{f.label}</span>
                  <span className="font-medium">{f.val}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t">
              <div className="flex items-center gap-2 text-xs">
                <span className="badge-orange">⚠ SIMULATED</span>
                <span className="text-gray-500">Identity data retrieved via UGHub-pattern NIRA API simulation</span>
              </div>
            </div>
          </div>

          {/* Business / Cooperative */}
          <div className="card">
            <h2 className="section-title">{isTrading ? 'Business & Tax Details' : 'Cooperative & Tax Details'}</h2>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {isTrading ? (
                <>
                  <div><span className="text-xs text-gray-500 block">Business Name</span><span className="font-medium">{app.businessName || app.cooperativeName}</span></div>
                  <div><span className="text-xs text-gray-500 block">TIN</span><span className="font-medium">{app.proposedTin}</span></div>
                </>
              ) : (
                <>
                  <div><span className="text-xs text-gray-500 block">Cooperative Name</span><span className="font-medium">{app.cooperativeName}</span></div>
                  <div><span className="text-xs text-gray-500 block">Proposed TIN</span><span className="font-medium">{app.proposedTin}</span></div>
                </>
              )}
              <div><span className="text-xs text-gray-500 block">Tax Status</span><span className="font-medium text-status-green">{app.taxStatus}</span></div>
              <div><span className="text-xs text-gray-500 block">Tax Clearance Valid Until</span><span className="font-medium">{app.taxClearanceValidUntil}</span></div>
            </div>
            <div className="mt-4 pt-4 border-t">
              <div className="flex items-center gap-2 text-xs">
                <span className="badge-orange">⚠ SIMULATED</span>
                <span className="text-gray-500">Tax data retrieved via UGHub-pattern URA API simulation</span>
              </div>
            </div>
          </div>

          {/* Documents with verify/reject */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="section-title mb-0">Attached Documents</h2>
              <span className="text-xs text-gray-500">
                {(app.documents || []).filter((d: any) => d.verificationStatus === 'verified').length}/{(app.documents || []).length} verified
              </span>
            </div>
            {app.documents?.length > 0 ? (
              <div className="space-y-3">
                {app.documents.map((doc: any) => (
                  <DocVerifyRow key={doc.id} doc={doc} appId={id!} onRefresh={() => qc.invalidateQueries({ queryKey: ['application', id] })} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No documents attached.</p>
            )}
          </div>

          {/* Payment (trading licence) */}
          {isTrading && app.feeAmount > 0 && (
            <PaymentPanel
              applicationId={Number(id)}
              serviceCode={app.serviceCode}
              feeAmount={app.feeAmount}
              feeCurrency={app.feeCurrency || 'UGX'}
              readOnly={true}
            />
          )}

          {/* Officer Reassignment */}
          {app.status !== 'approved' && app.status !== 'rejected' && (
            <div className="card">
              <h2 className="section-title">Officer Reassignment</h2>
              <p className="text-xs text-gray-500 mb-3">Reassign to another officer if workload or expertise requires it.</p>
              <div className="flex gap-2">
                <select
                  className="form-input flex-1"
                  value={reassignOfficerId}
                  onChange={e => setReassignOfficerId(e.target.value)}
                >
                  <option value="">Select officer…</option>
                  {(officers as any[])
                    .filter((o: any) => o.role === 'officer' && o.id !== app.assignedOfficerId)
                    .map((o: any) => (
                      <option key={o.id} value={o.id}>{o.name} ({o.district})</option>
                    ))}
                </select>
                <button
                  onClick={handleReassign}
                  disabled={!reassignOfficerId || reassigning}
                  className="btn-secondary shrink-0"
                >
                  {reassigning ? 'Reassigning…' : 'Reassign →'}
                </button>
              </div>
              {app.assignedOfficerName && (
                <p className="text-xs text-gray-500 mt-2">Currently assigned to: <strong>{app.assignedOfficerName}</strong></p>
              )}
            </div>
          )}

          {/* Decision */}
          {app.status !== 'approved' && app.status !== 'rejected' && app.status !== 'pending_countersign' && (
            <div className="card">
              <h2 className="section-title">Officer Decision</h2>

              <div className="grid grid-cols-3 gap-3 mb-4">
                {[
                  { val: 'approved', label: '✅ Approve', cls: decision === 'approved' ? 'bg-status-green text-white border-status-green' : 'border-gray-300 text-gray-700 hover:border-status-green hover:text-status-green' },
                  { val: 'more_info_requested', label: '📋 Request Info', cls: decision === 'more_info_requested' ? 'bg-status-orange text-white border-status-orange' : 'border-gray-300 text-gray-700 hover:border-status-orange hover:text-status-orange' },
                  { val: 'rejected', label: '❌ Reject', cls: decision === 'rejected' ? 'bg-status-red text-white border-status-red' : 'border-gray-300 text-gray-700 hover:border-status-red hover:text-status-red' },
                ].map(opt => (
                  <button
                    key={opt.val}
                    onClick={() => setDecision(opt.val as any)}
                    className={`border-2 rounded-lg py-3 font-semibold text-sm transition-colors ${opt.cls}`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>

              <div className="mb-4">
                <label className="form-label">Officer Notes {decision !== 'approved' && <span className="text-status-red">*</span>}</label>
                <textarea
                  className="form-input"
                  rows={3}
                  placeholder={decision === 'approved' ? 'Optional notes for the record…' : 'Required: explain your decision…'}
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                />
              </div>

              <button
                onClick={submitDecision}
                disabled={!decision || submitting || (decision !== 'approved' && !notes.trim())}
                className={`font-semibold px-6 py-2.5 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  decision === 'approved' ? 'bg-status-green text-white hover:opacity-90'
                  : decision === 'rejected' ? 'bg-status-red text-white hover:opacity-90'
                  : 'bg-status-orange text-white hover:opacity-90'
                }`}
              >
                {submitting ? 'Submitting…' : 'Submit Decision'}
              </button>
            </div>
          )}

          {/* Notification log */}
          <NotificationsPanel applicationId={Number(id)} />

          {/* API Interoperability Panel */}
          <ApiInteropPanel niraData={niraData} uraData={uraData} applicationRef={app.referenceNumber} app={app} />
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="card">
            <h2 className="section-title">SOP Checklist</h2>
            <p className="text-xs text-gray-500 mb-3">
              Standard Operating Procedure — {isTrading ? 'Trading Licence' : 'Agribusiness Permit'}
            </p>
            <div className="space-y-2">
              {sopResults.map(item => (
                <label key={item.id} className="flex items-start gap-2 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={item.passed}
                    onChange={e => setSopChecks(prev => ({ ...prev, [item.id]: e.target.checked }))}
                    className="mt-0.5 w-4 h-4 rounded border-gray-300 text-status-green focus:ring-status-green"
                  />
                  <span className={`text-xs leading-relaxed ${item.passed ? 'text-gray-700' : 'text-gray-400 line-through'}`}>
                    {item.label}
                  </span>
                </label>
              ))}
            </div>
            <div className={`mt-3 pt-3 border-t text-xs font-semibold ${allSopPassed ? 'text-status-green' : 'text-status-orange'}`}>
              {allSopPassed ? '✅ All SOP checks passed' : `⚠ ${sopResults.filter(s => !s.passed).length} check(s) pending`}
            </div>
          </div>

          <div className="card bg-gold-50 border border-gold-500">
            <h3 className="font-bold text-yellow-900 text-sm mb-2">UGHub Integration Spine</h3>
            <p className="text-xs text-yellow-800 mb-2">Data retrieved from the following simulated integrations:</p>
            <div className="space-y-1.5">
              {[
                { name: 'NIRA Identity API', status: 'SIMULATED' },
                { name: 'URA Tax Clearance API', status: 'SIMULATED' },
                { name: 'NIN Validation Service', status: 'SIMULATED' },
              ].map(s => (
                <div key={s.name} className="flex items-center justify-between text-xs">
                  <span className="text-yellow-900">{s.name}</span>
                  <span className="badge-orange">{s.status}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Audit log */}
          <div className="card">
            <h3 className="font-bold text-navy-700 text-sm mb-2">Audit Trail</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {(app.auditLog || []).map((entry: any) => (
                <div key={entry.id} className="text-xs border-l-2 border-navy-100 pl-2">
                  <p className="font-medium text-gray-700">{entry.action}</p>
                  <p className="text-gray-500">{entry.actorName} · {new Date(entry.createdAt).toLocaleString('en-UG')}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
