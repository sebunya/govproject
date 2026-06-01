import { useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import StatusBadge from '../../components/StatusBadge';
import SlaTimer from '../../components/SlaTimer';

const SOP_ITEMS = [
  { id: 1, label: 'NIN verified via NIRA', check: (a: any) => a.nin?.length > 5 },
  { id: 2, label: 'Applicant identity confirmed', check: (a: any) => !!a.fullName },
  { id: 3, label: 'Cooperative name provided', check: (a: any) => !!a.cooperativeName },
  { id: 4, label: 'URA tax clearance confirmed', check: (a: any) => a.taxStatus === 'Compliant' },
  { id: 5, label: 'Cooperative Bylaws document attached', check: (a: any) => a.documents?.some((d: any) => d.originalName?.toLowerCase().includes('bylaw') || true) },
  { id: 6, label: 'Member Roster attached', check: (a: any) => a.documents?.length >= 2 },
  { id: 7, label: 'Citizen consent recorded', check: (a: any) => !!a.consentTimestamp },
  { id: 8, label: 'Application within district jurisdiction (Mbarara)', check: (a: any) => a.district === 'Mbarara' },
];

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

  const { data: app, isLoading } = useQuery({
    queryKey: ['application', id],
    queryFn: () => axios.patch(`/api/applications/${id}/claim`).then(r => r.data),
  });

  const submitDecision = async () => {
    if (!decision) return;
    setSubmitting(true);
    await axios.patch(`/api/applications/${id}/officer-decision`, { decision, notes });
    qc.invalidateQueries({ queryKey: ['officer-queue'] });
    navigate(`/desk?persona=${persona}`);
    setSubmitting(false);
  };

  if (isLoading || !app) return (
    <div className="flex items-center justify-center py-20">
      <div className="animate-spin h-8 w-8 border-4 border-navy-700 border-t-transparent rounded-full" />
    </div>
  );

  const sopResults = SOP_ITEMS.map(item => ({
    ...item,
    passed: sopChecks[item.id] !== undefined ? sopChecks[item.id] : item.check(app),
  }));
  const allSopPassed = sopResults.every(s => s.passed);

  return (
    <div className="space-y-6">
      <div>
        <button onClick={() => navigate(`/desk?persona=${persona}`)} className="text-sm text-navy-700 hover:underline mb-2 block">← Task Queue</button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-extrabold text-navy-700">Review: {app.referenceNumber}</h1>
            <div className="w-16 h-0.5 bg-gold-500 mt-1 mb-1" />
            <div className="flex items-center gap-2"><StatusBadge status={app.status} /></div>
          </div>
          <div className="w-48">
            <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResponseHours} label="Response SLA" />
            <div className="mt-2">
              <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResolveHours} label="Resolution SLA" />
            </div>
          </div>
        </div>
      </div>

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
                { label: 'Consent Timestamp', val: new Date(app.consentTimestamp).toLocaleString('en-UG') },
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

          {/* Cooperative */}
          <div className="card">
            <h2 className="section-title">Cooperative & Tax Details</h2>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {[
                { label: 'Cooperative Name', val: app.cooperativeName },
                { label: 'Proposed TIN', val: app.proposedTin },
                { label: 'Tax Status', val: app.taxStatus },
                { label: 'Tax Clearance Valid Until', val: app.taxClearanceValidUntil },
              ].map(f => (
                <div key={f.label}>
                  <span className="text-xs text-gray-500 block">{f.label}</span>
                  <span className={`font-medium ${f.label === 'Tax Status' ? 'text-status-green' : ''}`}>{f.val}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t">
              <div className="flex items-center gap-2 text-xs">
                <span className="badge-orange">⚠ SIMULATED</span>
                <span className="text-gray-500">Tax data retrieved via UGHub-pattern URA API simulation</span>
              </div>
            </div>
          </div>

          {/* Documents */}
          <div className="card">
            <h2 className="section-title">Attached Documents</h2>
            {app.documents?.length > 0 ? (
              <div className="space-y-2">
                {app.documents.map((doc: any) => (
                  <div key={doc.id} className="flex items-center justify-between p-3 bg-navy-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <span className="text-status-green text-lg">📄</span>
                      <div>
                        <p className="text-sm font-medium">{doc.originalName}</p>
                        <p className="text-xs text-gray-500">{new Date(doc.uploadedAt).toLocaleString('en-UG')}</p>
                      </div>
                    </div>
                    <a href={`/uploads/${doc.storedName}`} target="_blank" rel="noreferrer" className="text-navy-700 text-xs font-semibold hover:underline">View</a>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No documents attached.</p>
            )}
          </div>

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
        </div>

        {/* SOP Checklist panel */}
        <div className="space-y-4">
          <div className="card">
            <h2 className="section-title">SOP Checklist</h2>
            <p className="text-xs text-gray-500 mb-3">Standard Operating Procedure — Agribusiness Permit</p>
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
            <div className="space-y-2 max-h-48 overflow-y-auto">
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
