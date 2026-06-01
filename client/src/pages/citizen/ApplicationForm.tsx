import { useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import SimulatedBanner from '../../components/SimulatedBanner';

type Step = 1 | 2 | 3 | 4 | 5 | 6;

interface NiraData {
  fullName: string; dateOfBirth: string; district: string; gender: string;
  verified: boolean; _simulated: true;
}
interface UraData {
  taxStatus: string; clearanceValidUntil: string; _simulated: true;
}

export default function ApplicationForm() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  const [step, setStep] = useState<Step>(1);
  const [nin, setNin] = useState('CM93019100ABC1J');
  const [niraData, setNiraData] = useState<NiraData | null>(null);
  const [niraLoading, setNiraLoading] = useState(false);
  const [showNiraBanner, setShowNiraBanner] = useState(false);
  const [niraError, setNiraError] = useState('');

  const [cooperativeName, setCooperativeName] = useState('Mbarara Coffee Growers Cooperative');
  const [proposedTin, setProposedTin] = useState('1000000042');
  const [uraData, setUraData] = useState<UraData | null>(null);
  const [uraLoading, setUraLoading] = useState(false);
  const [showUraBanner, setShowUraBanner] = useState(false);

  const [consent, setConsent] = useState(false);

  const [bylaws, setBylaws] = useState<File | null>(null);
  const [memberRoster, setMemberRoster] = useState<File | null>(null);
  const [fileError, setFileError] = useState('');

  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState<{ referenceNumber: string; id: number } | null>(null);

  const bylawsRef = useRef<HTMLInputElement>(null);
  const rosterRef = useRef<HTMLInputElement>(null);

  const verifyNira = async () => {
    if (!nin.trim()) { setNiraError('Please enter your NIN'); return; }
    setNiraLoading(true); setNiraError('');
    await new Promise(r => setTimeout(r, 1500));
    const res = await axios.post('/api/simulate/nira', { nin });
    setNiraData(res.data);
    setShowNiraBanner(true);
    setNiraLoading(false);
  };

  const verifyUra = async () => {
    setUraLoading(true);
    await new Promise(r => setTimeout(r, 1000));
    const res = await axios.post('/api/simulate/ura', { tin: proposedTin });
    setUraData(res.data);
    setShowUraBanner(true);
    setUraLoading(false);
  };

  const handleFile = (file: File | null, setter: (f: File | null) => void) => {
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { setFileError('File must be under 5MB'); return; }
    setFileError('');
    setter(file);
  };

  const [submitError, setSubmitError] = useState('');

  const handleSubmit = async () => {
    setSubmitting(true);
    setSubmitError('');
    try {
      const fd = new FormData();
      fd.append('nin', nin);
      fd.append('fullName', niraData!.fullName);
      fd.append('dateOfBirth', niraData!.dateOfBirth);
      fd.append('district', niraData!.district);
      fd.append('gender', niraData!.gender);
      fd.append('cooperativeName', cooperativeName);
      fd.append('proposedTin', proposedTin);
      fd.append('taxStatus', uraData!.taxStatus);
      fd.append('taxClearanceValidUntil', uraData!.clearanceValidUntil);
      fd.append('consentTimestamp', new Date().toISOString());
      if (bylaws) fd.append('bylaws', bylaws);
      if (memberRoster) fd.append('memberRoster', memberRoster);

      const res = await axios.post('/api/applications', fd);
      setSubmitted(res.data);
      setStep(6);
    } catch (err: any) {
      setSubmitError(err?.response?.data?.error || 'Submission failed. Please check your connection and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const stepLabels = [
    'Identity Verification',
    'Regulatory Check',
    'Consent',
    'Documents',
    'Review & Submit',
    'Confirmation',
  ];

  if (submitted && step === 6) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="card text-center py-10">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="text-2xl font-extrabold text-status-green mb-2">Application Submitted Successfully</h2>
          <p className="text-gray-600 mb-6">Your cooperative registration and agribusiness permit application has been received.</p>

          <div className="bg-navy-50 rounded-xl p-6 text-left space-y-3 mb-6">
            <div className="flex justify-between">
              <span className="text-sm font-semibold text-gray-500">Reference Number</span>
              <span className="font-extrabold text-navy-700 text-lg">{submitted.referenceNumber}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-semibold text-gray-500">Service</span>
              <span className="text-sm font-medium">Cooperative Registration & Agribusiness Permit</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-semibold text-gray-500">SLA — Initial Response</span>
              <span className="text-sm font-medium text-status-green">Within 2 working days</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-semibold text-gray-500">SLA — Resolution</span>
              <span className="text-sm font-medium text-status-green">Within 14 working days</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-semibold text-gray-500">MDA</span>
              <span className="text-sm font-medium">Mbarara District Local Government</span>
            </div>
          </div>

          <div className="bg-gold-50 border border-gold-500 rounded-lg p-4 text-left mb-6">
            <p className="text-sm text-yellow-900">
              <strong>What happens next?</strong> A District Agricultural Officer will review your application and contact you within 2 working days if additional information is required. You will be notified here when a decision is made.
            </p>
          </div>

          <div className="flex gap-3 justify-center">
            <button
              onClick={() => navigate(`/portal/application/${submitted.id}?persona=${persona}`)}
              className="btn-primary"
            >
              Track My Application →
            </button>
            <button
              onClick={() => navigate(`/portal?persona=${persona}`)}
              className="btn-secondary"
            >
              Return to Portal
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-navy-700">Cooperative Registration & Agribusiness Permit</h1>
        <div className="w-16 h-0.5 bg-gold-500 mt-1 mb-1" />
        <p className="text-sm text-gray-600">Mbarara District Local Government · No fee · SLA: 14 working days</p>
      </div>

      {/* Step indicator */}
      <div className="flex items-center gap-0">
        {stepLabels.map((label, i) => {
          const s = i + 1;
          const done = step > s;
          const active = step === s;
          return (
            <div key={s} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                  done ? 'bg-status-green text-white' : active ? 'bg-navy-700 text-white' : 'bg-gray-200 text-gray-400'
                }`}>
                  {done ? '✓' : s}
                </div>
                <span className={`text-xs mt-1 text-center hidden sm:block ${active ? 'text-navy-700 font-semibold' : 'text-gray-400'}`} style={{ maxWidth: 70 }}>
                  {label}
                </span>
              </div>
              {i < stepLabels.length - 1 && (
                <div className={`flex-1 h-0.5 mx-1 ${done ? 'bg-status-green' : 'bg-gray-200'}`} />
              )}
            </div>
          );
        })}
      </div>

      {/* STEP 1: NIN + NIRA */}
      {step === 1 && (
        <div className="card space-y-5">
          <h2 className="section-title">Step 1 — Identity Verification (NIRA)</h2>

          <div>
            <label className="form-label">National Identification Number (NIN)</label>
            <div className="flex gap-2">
              <input
                className="form-input"
                value={nin}
                onChange={e => setNin(e.target.value)}
                placeholder="e.g. CM93019100ABC1J"
                maxLength={20}
              />
              <button
                onClick={verifyNira}
                disabled={niraLoading || !!niraData}
                className="btn-primary shrink-0 flex items-center gap-2"
              >
                {niraLoading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                    </svg>
                    Verifying…
                  </>
                ) : niraData ? '✓ Verified' : 'Verify Identity'}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">Demo NIN: CM93019100ABC1J</p>
            {niraError && <p className="text-sm text-status-red mt-1">{niraError}</p>}
          </div>

          {showNiraBanner && <SimulatedBanner service="NIRA" />}

          {niraData && (
            <div className="bg-status-greenBg border border-status-green rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2 text-status-green font-semibold text-sm">
                <span>✓</span> Identity Verified
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: 'Full Name', val: niraData.fullName },
                  { label: 'Date of Birth', val: niraData.dateOfBirth },
                  { label: 'District of Origin', val: niraData.district },
                  { label: 'Gender', val: niraData.gender },
                ].map(f => (
                  <div key={f.label}>
                    <label className="form-label text-xs">{f.label} 🔒</label>
                    <div className="form-input-readonly">{f.val}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end">
            <button
              onClick={() => setStep(2)}
              disabled={!niraData}
              className="btn-primary"
            >
              Continue →
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: Cooperative + URA */}
      {step === 2 && (
        <div className="card space-y-5">
          <h2 className="section-title">Step 2 — Cooperative Details & Tax Status (URA)</h2>

          <div>
            <label className="form-label">Cooperative Name</label>
            <input
              className="form-input"
              value={cooperativeName}
              onChange={e => setCooperativeName(e.target.value)}
              placeholder="e.g. Mbarara Coffee Growers Cooperative"
            />
          </div>

          <div>
            <label className="form-label">Proposed Tax Identification Number (TIN)</label>
            <div className="flex gap-2">
              <input
                className="form-input"
                value={proposedTin}
                onChange={e => setProposedTin(e.target.value)}
                placeholder="10-digit TIN"
              />
              <button
                onClick={verifyUra}
                disabled={uraLoading || !!uraData}
                className="btn-primary shrink-0 flex items-center gap-2"
              >
                {uraLoading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                    </svg>
                    Checking…
                  </>
                ) : uraData ? '✓ Verified' : 'Verify Tax Status'}
              </button>
            </div>
          </div>

          {showUraBanner && <SimulatedBanner service="URA" />}

          {uraData && (
            <div className="bg-status-greenBg border border-status-green rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2 text-status-green font-semibold text-sm">
                <span>✓</span> Tax Status Verified
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="form-label text-xs">Tax Status 🔒</label>
                  <div className="form-input-readonly">{uraData.taxStatus}</div>
                </div>
                <div>
                  <label className="form-label text-xs">Clearance Valid Until 🔒</label>
                  <div className="form-input-readonly">{uraData.clearanceValidUntil}</div>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-between">
            <button onClick={() => setStep(1)} className="btn-secondary">← Back</button>
            <button onClick={() => setStep(3)} disabled={!uraData} className="btn-primary">Continue →</button>
          </div>
        </div>
      )}

      {/* STEP 3: Consent */}
      {step === 3 && (
        <div className="card space-y-5">
          <h2 className="section-title">Step 3 — Data Consent</h2>

          <div className="bg-navy-50 rounded-xl p-5 space-y-3">
            <h3 className="font-bold text-navy-700">Data Processing Consent</h3>
            <p className="text-sm text-gray-700 leading-relaxed">
              NileGov Stack will retrieve and process the following personal data for this application:
            </p>
            <ul className="text-sm text-gray-700 space-y-1 ml-4 list-disc">
              <li>Identity information retrieved from NIRA (name, date of birth, district, gender)</li>
              <li>Tax status information retrieved from URA</li>
              <li>Cooperative registration details provided by you</li>
              <li>Uploaded documents (cooperative bylaws, member roster)</li>
            </ul>
            <div className="border-t border-navy-100 pt-3">
              <p className="text-sm text-gray-700 leading-relaxed">
                This data will be shared with Mbarara District Local Government officers for the purpose of processing your application.
                Data will be retained in accordance with applicable government records retention schedules.
              </p>
            </div>
          </div>

          <label className="flex items-start gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={consent}
              onChange={e => setConsent(e.target.checked)}
              className="mt-0.5 w-5 h-5 rounded border-gray-300 text-navy-700 focus:ring-navy-700"
            />
            <span className="text-sm text-gray-700 leading-relaxed group-hover:text-gray-900">
              I consent to NileGov retrieving and processing my personal data for this application,
              in accordance with <strong>Section 10 of the Data Protection and Privacy Act 2019</strong>.
              I understand that my consent timestamp will be recorded.
            </span>
          </label>

          {consent && (
            <div className="bg-status-greenBg border border-status-green rounded-lg p-3 text-sm text-status-green flex items-center gap-2">
              <span>✓</span>
              Consent will be recorded at: <strong>{new Date().toLocaleString('en-UG')}</strong>
            </div>
          )}

          <div className="flex justify-between">
            <button onClick={() => setStep(2)} className="btn-secondary">← Back</button>
            <button onClick={() => setStep(4)} disabled={!consent} className="btn-primary">Continue →</button>
          </div>
        </div>
      )}

      {/* STEP 4: Documents */}
      {step === 4 && (
        <div className="card space-y-5">
          <h2 className="section-title">Step 4 — Document Attachment</h2>

          {fileError && (
            <div className="bg-status-redBg border border-status-red text-status-red text-sm rounded-lg p-3">{fileError}</div>
          )}

          <div className="space-y-4">
            {[
              { label: 'Cooperative Bylaws', key: 'bylaws', file: bylaws, setter: setBylaws, ref: bylawsRef, required: true },
              { label: 'Member Roster', key: 'roster', file: memberRoster, setter: setMemberRoster, ref: rosterRef, required: true },
            ].map(doc => (
              <div key={doc.key} className="border-2 border-dashed border-gray-300 rounded-xl p-5 hover:border-navy-700 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-sm text-gray-700">{doc.label}</p>
                    <p className="text-xs text-gray-500 mt-0.5">PDF or image · Max 5MB{doc.required ? ' · Required' : ''}</p>
                  </div>
                  {doc.file ? (
                    <div className="flex items-center gap-2 text-status-green text-sm font-medium">
                      <span>✅</span>
                      <span className="max-w-[160px] truncate">{doc.file.name}</span>
                      <button
                        onClick={() => doc.setter(null)}
                        className="text-gray-400 hover:text-status-red text-xs ml-1"
                      >✕</button>
                    </div>
                  ) : (
                    <button
                      onClick={() => doc.ref.current?.click()}
                      className="btn-secondary text-sm py-2"
                    >
                      Choose File
                    </button>
                  )}
                </div>
                <input
                  ref={doc.ref}
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  className="hidden"
                  onChange={e => handleFile(e.target.files?.[0] || null, doc.setter)}
                />
              </div>
            ))}
          </div>

          <div className="flex justify-between">
            <button onClick={() => setStep(3)} className="btn-secondary">← Back</button>
            <button
              onClick={() => setStep(5)}
              disabled={!bylaws || !memberRoster}
              className="btn-primary"
            >
              Continue →
            </button>
          </div>
        </div>
      )}

      {/* STEP 5: Review */}
      {step === 5 && (
        <div className="card space-y-5">
          <h2 className="section-title">Step 5 — Review & Submit</h2>

          <div className="space-y-4">
            <div className="bg-navy-50 rounded-xl p-4 space-y-2">
              <h3 className="font-bold text-navy-700 text-sm uppercase tracking-wide">Applicant Identity</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span className="text-gray-500">Full Name</span><span className="font-medium">{niraData?.fullName}</span>
                <span className="text-gray-500">NIN</span><span className="font-medium">{nin}</span>
                <span className="text-gray-500">Date of Birth</span><span className="font-medium">{niraData?.dateOfBirth}</span>
                <span className="text-gray-500">District</span><span className="font-medium">{niraData?.district}</span>
              </div>
            </div>

            <div className="bg-navy-50 rounded-xl p-4 space-y-2">
              <h3 className="font-bold text-navy-700 text-sm uppercase tracking-wide">Cooperative Details</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span className="text-gray-500">Name</span><span className="font-medium">{cooperativeName}</span>
                <span className="text-gray-500">Proposed TIN</span><span className="font-medium">{proposedTin}</span>
                <span className="text-gray-500">Tax Status</span><span className="font-medium text-status-green">{uraData?.taxStatus}</span>
                <span className="text-gray-500">Valid Until</span><span className="font-medium">{uraData?.clearanceValidUntil}</span>
              </div>
            </div>

            <div className="bg-navy-50 rounded-xl p-4 space-y-2">
              <h3 className="font-bold text-navy-700 text-sm uppercase tracking-wide">Documents</h3>
              <div className="space-y-1 text-sm">
                <div className="flex items-center gap-2"><span className="text-status-green">✓</span>{bylaws?.name}</div>
                <div className="flex items-center gap-2"><span className="text-status-green">✓</span>{memberRoster?.name}</div>
              </div>
            </div>

            <div className="bg-gold-50 border border-gold-500 rounded-lg p-4 text-sm text-yellow-900">
              <strong>SLA Commitment:</strong> Mbarara District Local Government will respond within <strong>2 working days</strong> and resolve your application within <strong>14 working days</strong>.
            </div>
          </div>

          {submitError && (
            <div className="bg-status-redBg border border-status-red text-status-red rounded-lg p-3 text-sm flex items-start gap-2">
              <span className="mt-0.5">⚠</span>
              <span>{submitError}</span>
            </div>
          )}

          <div className="flex justify-between">
            <button onClick={() => setStep(4)} className="btn-secondary">← Back</button>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="btn-primary flex items-center gap-2"
            >
              {submitting ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                  </svg>
                  Submitting…
                </>
              ) : 'Submit Application'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
