import { useState, useRef } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import StatusBadge from '../../components/StatusBadge';
import SlaTimer from '../../components/SlaTimer';

export default function ApplicationStatus() {
  const { id } = useParams<{ id: string }>();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';
  const navigate = useNavigate();
  const qc = useQueryClient();

  const [rating, setRating] = useState(0);
  const [moreInfoMsg, setMoreInfoMsg] = useState('');
  const [moreInfoFile, setMoreInfoFile] = useState<File | null>(null);
  const [submittingMoreInfo, setSubmittingMoreInfo] = useState(false);
  const moreInfoFileRef = useRef<HTMLInputElement>(null);
  const [ratingComment, setRatingComment] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);
  const [hoverRating, setHoverRating] = useState(0);

  const { data: app, isLoading } = useQuery({
    queryKey: ['application', id],
    queryFn: () => axios.get(`/api/applications/${id}`).then(r => r.data),
    refetchInterval: 5000,
  });

  const submitRating = async () => {
    setSubmittingRating(true);
    await axios.patch(`/api/applications/${id}/rate`, { rating, comment: ratingComment });
    qc.invalidateQueries({ queryKey: ['application', id] });
    setSubmittingRating(false);
  };

  const submitMoreInfo = async () => {
    setSubmittingMoreInfo(true);
    const fd = new FormData();
    if (moreInfoMsg) fd.append('message', moreInfoMsg);
    if (moreInfoFile) fd.append('additionalDoc', moreInfoFile);
    await axios.patch(`/api/applications/${id}/citizen-response`, fd);
    qc.invalidateQueries({ queryKey: ['application', id] });
    setMoreInfoMsg('');
    setMoreInfoFile(null);
    setSubmittingMoreInfo(false);
  };

  if (isLoading || !app) return (
    <div className="flex items-center justify-center py-20">
      <div className="animate-spin h-8 w-8 border-4 border-navy-700 border-t-transparent rounded-full" />
    </div>
  );

  const isResolved = ['approved', 'rejected'].includes(app.status);

  const timelineSteps = [
    { label: 'Application Submitted', time: app.submittedAt, done: true },
    { label: 'Assigned to Officer', time: app.respondedAt, done: !!app.assignedOfficerId },
    { label: 'Officer Review Complete', time: app.officerDecision ? app.respondedAt : null, done: !!app.officerDecision },
    { label: 'Supervisor Countersignature', time: app.supervisorDecision ? app.resolvedAt : null, done: !!app.supervisorDecision },
    { label: 'Final Decision', time: app.resolvedAt, done: isResolved },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <button onClick={() => navigate(`/portal/my-applications?persona=${persona}`)} className="text-sm text-navy-700 hover:underline mb-2 block">← My Applications</button>
          <h1 className="text-2xl font-extrabold text-navy-700">{app.referenceNumber}</h1>
          <div className="w-16 h-0.5 bg-gold-500 mt-1 mb-1" />
          <div className="flex items-center gap-2">
            <StatusBadge status={app.status} />
          </div>
        </div>
      </div>

      {/* Decision banner */}
      {app.status === 'approved' && (
        <div className="bg-status-greenBg border-2 border-status-green rounded-xl overflow-hidden">
          <div className="bg-status-green text-white px-5 py-3 flex items-center gap-2">
            <span className="text-xl">✅</span>
            <span className="font-bold text-lg">Application Approved — Permit Granted</span>
          </div>
          <div className="p-5 space-y-3">
            <p className="text-sm text-gray-700">
              Your application for <strong>Cooperative Registration & Agribusiness Permit</strong> has been
              approved by Mbarara District Local Government. Your cooperative is authorised to operate.
            </p>
            {app.supervisorNotes && (
              <div className="bg-white rounded-lg p-3 border border-status-green">
                <p className="text-xs font-semibold text-gray-500 mb-1">Senior Officer's Note</p>
                <p className="text-sm text-gray-700 italic">"{app.supervisorNotes}"</p>
              </div>
            )}
            <div className="flex gap-3 pt-1">
              <div className="text-xs text-gray-500">
                Decision by: <strong>Nakamya Grace</strong> · Senior District Officer
              </div>
              {app.resolvedAt && (
                <div className="text-xs text-gray-500">
                  Date: <strong>{new Date(app.resolvedAt).toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}</strong>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {app.status === 'rejected' && (
        <div className="bg-status-redBg border border-status-red rounded-xl p-5">
          <div className="flex items-center gap-3">
            <span className="text-3xl">❌</span>
            <div>
              <h3 className="font-bold text-status-red text-lg">Application Rejected</h3>
              <p className="text-sm text-gray-700 mt-0.5">{app.officerNotes || 'Application did not meet requirements.'}</p>
            </div>
          </div>
        </div>
      )}

      {app.status === 'more_info_requested' && (
        <div className="bg-status-orangeBg border-2 border-status-orange rounded-xl overflow-hidden">
          <div className="bg-status-orange text-white px-5 py-3 flex items-center gap-2">
            <span>📋</span>
            <span className="font-bold">Additional Information Required — Action Needed</span>
          </div>
          <div className="p-5 space-y-4">
            <div className="bg-white rounded-lg p-4 border border-orange-200">
              <p className="text-xs font-semibold text-gray-500 mb-1">Officer's Request</p>
              <p className="text-sm text-gray-800">{app.officerNotes || 'Please provide additional documentation to support your application.'}</p>
            </div>

            <div className="space-y-3">
              <p className="text-sm font-semibold text-gray-700">Your Response</p>
              <textarea
                className="form-input"
                rows={3}
                placeholder="Describe the additional information you are providing…"
                value={moreInfoMsg}
                onChange={e => setMoreInfoMsg(e.target.value)}
              />
              <div className="flex items-center gap-3">
                {moreInfoFile ? (
                  <div className="flex items-center gap-2 text-status-green text-sm">
                    <span>✅</span><span className="max-w-[200px] truncate">{moreInfoFile.name}</span>
                    <button onClick={() => setMoreInfoFile(null)} className="text-gray-400 text-xs">✕</button>
                  </div>
                ) : (
                  <button onClick={() => moreInfoFileRef.current?.click()} className="btn-secondary text-sm py-2">
                    📎 Attach Document
                  </button>
                )}
                <input ref={moreInfoFileRef} type="file" className="hidden" accept=".pdf,.jpg,.jpeg,.png"
                  onChange={e => setMoreInfoFile(e.target.files?.[0] || null)} />
              </div>
              <button
                onClick={submitMoreInfo}
                disabled={(!moreInfoMsg.trim() && !moreInfoFile) || submittingMoreInfo}
                className="btn-primary"
              >
                {submittingMoreInfo ? 'Submitting…' : 'Submit Additional Information →'}
              </button>
            </div>
          </div>
          <div className="bg-white border-t border-orange-200">
            <div className="flex items-center gap-2 text-xs text-gray-500 px-5 py-3">
              <span className="text-gray-400">ℹ</span>
              After submission, your application returns to the officer's queue for further review.
            </div>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {/* Application details */}
        <div className="card space-y-4">
          <h2 className="section-title">Application Details</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">Service</span><span className="font-medium text-right max-w-[60%]">{app.serviceType}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Applicant</span><span className="font-medium">{app.fullName}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Cooperative</span><span className="font-medium text-right max-w-[60%]">{app.cooperativeName}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">District</span><span className="font-medium">{app.district}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Submitted</span><span className="font-medium">{new Date(app.submittedAt).toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}</span></div>
            {app.documents?.length > 0 && (
              <div className="pt-2 border-t">
                <span className="text-gray-500 block mb-1">Documents</span>
                {app.documents.map((d: any) => (
                  <div key={d.id} className="flex items-center gap-1 text-xs text-status-green">
                    <span>✓</span>{d.originalName}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* SLA status */}
        <div className="card space-y-4">
          <h2 className="section-title">SLA Status</h2>
          {!app.resolvedAt ? (
            <div className="space-y-3">
              <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResponseHours} label="Initial Response (48h)" />
              <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResolveHours} label="Resolution (14 days)" />
            </div>
          ) : (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Resolved in</span>
                <span className="font-bold text-status-green">
                  {Math.round((new Date(app.resolvedAt).getTime() - new Date(app.submittedAt).getTime()) / 3600000)} hours
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">SLA Target</span>
                <span className="font-medium">{app.slaResolveHours}h ({app.slaResolveHours / 24} days)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">SLA Status</span>
                <span className={`font-semibold ${
                  (new Date(app.resolvedAt).getTime() - new Date(app.submittedAt).getTime()) / 3600000 <= app.slaResolveHours
                    ? 'text-status-green' : 'text-status-red'
                }`}>
                  {(new Date(app.resolvedAt).getTime() - new Date(app.submittedAt).getTime()) / 3600000 <= app.slaResolveHours
                    ? '✓ Within SLA' : '⚠ SLA Breached'}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Timeline */}
      <div className="card">
        <h2 className="section-title">Application Timeline</h2>
        <div className="space-y-0">
          {timelineSteps.map((step, i) => (
            <div key={i} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  step.done ? 'bg-status-green text-white' : 'bg-gray-200 text-gray-400'
                }`}>
                  {step.done ? '✓' : i + 1}
                </div>
                {i < timelineSteps.length - 1 && (
                  <div className={`w-0.5 h-6 ${step.done ? 'bg-status-green' : 'bg-gray-200'}`} />
                )}
              </div>
              <div className="pb-4 pt-1">
                <p className={`text-sm font-semibold ${step.done ? 'text-gray-800' : 'text-gray-400'}`}>{step.label}</p>
                {step.time && <p className="text-xs text-gray-500">{new Date(step.time).toLocaleString('en-UG')}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Rating */}
      {isResolved && !app.rating && (
        <div className="card">
          <h2 className="section-title">Rate This Service</h2>
          <p className="text-sm text-gray-600 mb-4">Your feedback helps improve government services for all citizens.</p>

          <div className="flex gap-2 mb-4">
            {[1, 2, 3, 4, 5].map(s => (
              <button
                key={s}
                onClick={() => setRating(s)}
                onMouseEnter={() => setHoverRating(s)}
                onMouseLeave={() => setHoverRating(0)}
                className={`text-3xl transition-transform hover:scale-110 ${
                  s <= (hoverRating || rating) ? 'opacity-100' : 'opacity-30'
                }`}
              >
                ⭐
              </button>
            ))}
          </div>

          {rating > 0 && (
            <>
              <textarea
                className="form-input mb-3"
                rows={2}
                placeholder="Optional comment…"
                value={ratingComment}
                onChange={e => setRatingComment(e.target.value)}
              />
              <button onClick={submitRating} disabled={submittingRating} className="btn-primary">
                {submittingRating ? 'Submitting…' : 'Submit Rating'}
              </button>
            </>
          )}
        </div>
      )}

      {isResolved && app.rating && (
        <div className="card bg-status-greenBg border border-status-green">
          <p className="font-semibold text-status-green">Thank you for your feedback!</p>
          <p className="text-sm text-gray-600 mt-1">
            You rated this service {'⭐'.repeat(app.rating)} ({app.rating}/5).
            {app.ratingComment && ` "${app.ratingComment}"`}
          </p>
        </div>
      )}
    </div>
  );
}
