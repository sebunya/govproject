import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import StatusBadge from '../components/StatusBadge';
import SlaTimer from '../components/SlaTimer';

export default function TrackApplication() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';
  const [ref, setRef] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const track = async () => {
    if (!ref.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await axios.get(`/api/track/${ref.trim().toUpperCase()}`);
      setResult(res.data);
    } catch {
      setError('Reference number not found. Please check and try again.');
    } finally {
      setLoading(false);
    }
  };

  const STATUS_MSG: Record<string, string> = {
    submitted: 'Your application has been received and is awaiting officer assignment.',
    under_review: 'A District Officer is currently reviewing your application.',
    more_info_requested: 'An officer has requested additional information. Please log in to respond.',
    pending_countersign: 'Your application has been approved by the officer and is awaiting supervisor countersignature.',
    approved: 'Your application has been approved. Your permit has been granted.',
    rejected: 'Your application has been rejected. Please contact the District Office for details.',
    withdrawn: 'This application was withdrawn by the applicant.',
  };

  return (
    <div>
      <Header persona={persona} />
      <main className="max-w-2xl mx-auto px-4 sm:px-6 py-16 space-y-8">
        <div className="text-center">
          <div className="text-5xl mb-4">🔍</div>
          <h1 className="text-3xl font-extrabold text-navy-700 mb-2">Track Your Application</h1>
          <div className="w-16 h-0.5 bg-gold-500 mx-auto mt-1 mb-3" />
          <p className="text-gray-600">Enter your reference number to check the status of your application. No account required.</p>
        </div>

        <div className="card">
          <label className="form-label">Reference Number</label>
          <div className="flex gap-2">
            <input
              className="form-input font-mono uppercase"
              placeholder="NGS-2026-0001"
              value={ref}
              onChange={e => setRef(e.target.value.toUpperCase())}
              onKeyDown={e => e.key === 'Enter' && track()}
            />
            <button onClick={track} disabled={loading || !ref.trim()} className="btn-primary shrink-0">
              {loading ? 'Searching…' : 'Track →'}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">Example: NGS-2026-0001</p>
          {error && <p className="text-sm text-status-red mt-2">{error}</p>}
        </div>

        {result && (
          <div className="card space-y-4">
            <div className="flex items-center gap-3">
              <div className="text-3xl font-extrabold text-navy-700 font-mono">{result.referenceNumber}</div>
              <StatusBadge status={result.status} />
            </div>

            <div className="bg-navy-50 rounded-xl p-4 space-y-3">
              {STATUS_MSG[result.status] && (
                <p className="text-sm text-gray-700 font-medium">{STATUS_MSG[result.status]}</p>
              )}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="text-xs text-gray-500 block">Service</span><span className="font-medium">{result.serviceType}</span></div>
                <div><span className="text-xs text-gray-500 block">Submitted</span><span className="font-medium">{new Date(result.submittedAt).toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}</span></div>
                {result.respondedAt && <div><span className="text-xs text-gray-500 block">First Response</span><span className="font-medium">{new Date(result.respondedAt).toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}</span></div>}
                {result.resolvedAt && <div><span className="text-xs text-gray-500 block">Resolved</span><span className="font-medium text-status-green">{new Date(result.resolvedAt).toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}</span></div>}
              </div>
            </div>

            {!result.resolvedAt && (
              <div className="space-y-2">
                <SlaTimer submittedAt={result.submittedAt} slaHours={result.slaResponseHours} label="Initial Response SLA" />
                <SlaTimer submittedAt={result.submittedAt} slaHours={result.slaResolveHours} label="Resolution SLA" />
              </div>
            )}

            {result.status === 'more_info_requested' && (
              <div className="bg-status-orangeBg border border-status-orange rounded-lg p-3">
                <p className="text-sm font-bold text-status-orange">Action Required</p>
                <p className="text-xs text-gray-700 mt-1">Log in to the NileGov citizen portal and navigate to "My Applications" to respond to the officer's request.</p>
              </div>
            )}

            {result.status === 'approved' && (
              <div className="bg-status-greenBg border border-status-green rounded-lg p-3">
                <p className="text-sm font-bold text-status-green">Permit Granted</p>
                <p className="text-xs text-gray-700 mt-1">Visit the citizen portal and log in with your NIN to download your permit certificate.</p>
              </div>
            )}
          </div>
        )}

        <div className="bg-gold-50 border border-gold-500 rounded-xl p-4 text-sm text-yellow-800">
          <strong>Prototype:</strong> This tracker is for demonstration only. Reference numbers shown are from seeded demo data and do not represent real government applications.
        </div>
      </main>
      <Footer />
    </div>
  );
}
