import { useState, useRef, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import SimulatedBanner from '../../components/SimulatedBanner';

function ConfirmationScreen({ referenceNumber, applicationId, persona, serviceCode, onTrack, onPortal }: {
  referenceNumber: string;
  applicationId: number;
  persona: string;
  serviceCode: string;
  onTrack: () => void;
  onPortal: () => void;
}) {
  const [copied, setCopied] = useState(false);
  const [countdown, setCountdown] = useState(15);

  useEffect(() => {
    const t = setInterval(() => setCountdown(c => {
      if (c <= 1) { clearInterval(t); onTrack(); return 0; }
      return c - 1;
    }), 1000);
    return () => clearInterval(t);
  }, []);

  const copy = () => {
    navigator.clipboard.writeText(referenceNumber).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const isTrading = serviceCode === 'trading-licence';

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="card py-10">
        <div className="text-center mb-6">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-extrabold text-status-green mb-2">Application Submitted Successfully</h2>
          <p className="text-gray-600">
            {isTrading
              ? 'Your Trading Licence application has been received. Complete payment to proceed.'
              : 'Your cooperative registration and agribusiness permit application has been received by Mbarara District Local Government.'}
          </p>
        </div>

        <div className="bg-navy-700 rounded-xl p-5 text-center mb-6">
          <p className="text-navy-100 text-xs font-semibold uppercase tracking-wider mb-1">Your Reference Number</p>
          <div className="flex items-center justify-center gap-3">
            <span className="font-extrabold text-white text-3xl tracking-widest">{referenceNumber}</span>
            <button
              onClick={copy}
              className={`text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors ${copied ? 'bg-status-green text-white' : 'bg-white bg-opacity-20 text-white hover:bg-opacity-30'}`}
            >
              {copied ? '✓ Copied!' : '📋 Copy'}
            </button>
          </div>
          <p className="text-navy-100 text-xs mt-2 opacity-70">Keep this number to track your application</p>
        </div>

        <div className="bg-navy-50 rounded-xl p-5 space-y-3 mb-5">
          {[
            { label: 'Service', value: isTrading ? 'Trading Licence' : 'Cooperative Registration & Agribusiness Permit' },
            { label: 'SLA — Initial Response', value: 'Within 2 working days', green: true },
            { label: 'SLA — Resolution', value: isTrading ? 'Within 10 working days' : 'Within 14 working days', green: true },
            { label: 'MDA', value: 'Mbarara District Local Government' },
          ].map(f => (
            <div key={f.label} className="flex justify-between text-sm">
              <span className="text-gray-500 font-semibold">{f.label}</span>
              <span className={`font-medium text-right max-w-[60%] ${f.green ? 'text-status-green' : ''}`}>{f.value}</span>
            </div>
          ))}
        </div>

        {isTrading && (
          <div className="bg-gold-50 border-2 border-gold-500 rounded-xl p-4 mb-6">
            <p className="text-sm font-bold text-yellow-900 mb-1">💳 Payment Required</p>
            <p className="text-sm text-yellow-800">
              Your application requires a UGX 120,000 processing fee. Track your application to complete payment via MTN/Airtel Mobile Money or Card.
            </p>
          </div>
        )}

        <div className="bg-gold-50 border border-gold-500 rounded-lg p-4 mb-6">
          <p className="text-sm text-yellow-900">
            <strong>What happens next?</strong> A District Officer will review your application and may contact you within 2 working days if additional information is required.
          </p>
        </div>

        <div className="flex gap-3 justify-center">
          <button onClick={onTrack} className="btn-primary">
            Track My Application →
          </button>
          <button onClick={onPortal} className="btn-secondary">Return to Portal</button>
        </div>
        <p className="text-xs text-center text-gray-400 mt-3">
          Redirecting to application tracker in {countdown}s…
        </p>
      </div>
    </div>
  );
}

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
  const serviceParam = params.get('service') || 'cooperative-permit';
  const isTrading = serviceParam === 'trading-licence';

  const { data: serviceInfo } = useQuery({
    queryKey: ['service', serviceParam],
    queryFn: () => axios.get('/api/services').then(r => (r.data as any[]).find((s: any) => s.code === serviceParam)),
    staleTime: 60000,
  });

  const [step, setStep] = useState<Step>(1);
  const [nin, setNin] = useState('CM93019100ABC1J');
  const [niraData, setNiraData] = useState<NiraData | null>(null);
  const [niraLoading, setNiraLoading] = useState(false);
  const [showNiraBanner, setShowNiraBanner] = useState(false);
  const [niraError, setNiraError] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('+256700000000');
  const [email, setEmail] = useState('citizen@demo.ug');

  const [cooperativeName, setCooperativeName] = useState(isTrading ? '' : 'Mbarara Coffee Growers Cooperative');
  const [businessName, setBusinessName] = useState('Nakayima General Merchandise');
  const [proposedTin, setProposedTin] = useState('1000000042');
  const [uraData, setUraData] = useState<UraData | null>(null);
  const [uraLoading, setUraLoading] = useState(false);
  const [showUraBanner, setShowUraBanner] = useState(false);

  const [consent, setConsent] = useState(false);

  const [bylaws, setBylaws] = useState<File | null>(null);
  const [memberRoster, setMemberRoster] = useState<File | null>(null);
  const [tradingDoc, setTradingDoc] = useState<File | null>(null);
  const [fileError, setFileError] = useState('');

  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState<{ referenceNumber: string; id: number } | null>(null);
  const [submitError, setSubmitError] = useState('');

  const bylawsRef = useRef<HTMLInputElement>(null);
  const rosterRef = useRef<HTMLInputElement>(null);
  const tradingDocRef = useRef<HTMLInputElement>(null);

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
      if (phoneNumber.trim()) fd.append('phoneNumber', phoneNumber.trim());
      if (email.trim()) fd.append('email', email.trim());
      fd.append('serviceCode', serviceParam);
      if (isTrading) {
        fd.append('businessName', businessName);
      } else {
        fd.append('cooperativeName', cooperativeName);
      }
      fd.append('proposedTin', proposedTin);
      fd.append('taxStatus', uraData!.taxStatus);
      fd.append('taxClearanceValidUntil', uraData!.clearanceValidUntil);
      fd.append('consentTimestamp', new Date().toISOString());
      if (bylaws) fd.append('bylaws', bylaws);
      if (memberRoster) fd.append('memberRoster', memberRoster);
      if (tradingDoc) fd.append('bizReg', tradingDoc);

      const res = await axios.post('/api/applications', fd);
      setSubmitted(res.data);
      setStep(6);
    } catch (err: any) {
      setSubmitError(err?.response?.data?.error || 'Submission failed. Please check your connection and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const docsReady = isTrading ? !!tradingDoc : (!!bylaws && !!memberRoster);

  const stepLabels = isTrading
    ? ['Identity', 'Tax Check', 'Consent', 'Documents', 'Review & Submit', 'Confirmation']
    : ['Identity Verification', 'Regulatory Check', 'Consent', 'Documents', 'Review & Submit', 'Confirmation'];

  if (submitted && step === 6) {
    return (
      <ConfirmationScreen
        referenceNumber={submitted.referenceNumber}
        applicationId={submitted.id}
        persona={persona}
        serviceCode={serviceParam}
        onTrack={() => navigate(`/portal/application/${submitted.id}?persona=${persona}`)}
        onPortal={() => navigate(`/portal?persona=${persona}`)}
      />
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-navy-700">
          {isTrading ? 'Trading Licence Application' : 'Cooperative Registration & Agribusiness Permit'}
        </h1>
        <div className="w-16 h-0.5 bg-gold-500 mt-1 mb-1" />
        <p className="text-sm text-gray-600">
          Mbarara District Local Government ·{' '}
          {serviceInfo ? (serviceInfo.feeAmount > 0 ? `${serviceInfo.feeCurrency} ${Number(serviceInfo.feeAmount).toLocaleString()} fee` : 'No fee') : '…'}{' '}
          · SLA: {serviceInfo ? `${Math.round(serviceInfo.slaResolveHours / 24)} working days` : '…'}
        </p>
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

          {/* Contact details for real notifications */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="form-label">Phone Number <span className="text-gold-500 font-semibold">(for SMS & WhatsApp)</span></label>
              <input
                className="form-input"
                value={phoneNumber}
                onChange={e => setPhoneNumber(e.target.value)}
                placeholder="+256700000000"
                type="tel"
              />
              <p className="text-xs text-gray-400 mt-1">Used for SMS and WhatsApp notifications</p>
            </div>
            <div>
              <label className="form-label">Email Address <span className="text-gold-500 font-semibold">(for email notifications)</span></label>
              <input
                className="form-input"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com"
                type="email"
              />
              <p className="text-xs text-gray-400 mt-1">Used for ZeptoMail transactional email</p>
            </div>
          </div>

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
            <button onClick={() => setStep(2)} disabled={!niraData} className="btn-primary">Continue →</button>
          </div>
        </div>
      )}

      {/* STEP 2: Business/Cooperative + URA */}
      {step === 2 && (
        <div className="card space-y-5">
          <h2 className="section-title">Step 2 — {isTrading ? 'Business Details' : 'Cooperative Details'} & Tax Status (URA)</h2>

          {isTrading ? (
            <div>
              <label className="form-label">Business / Trading Name</label>
              <input
                className="form-input"
                value={businessName}
                onChange={e => setBusinessName(e.target.value)}
                placeholder="e.g. Nakayima General Merchandise"
              />
            </div>
          ) : (
            <div>
              <label className="form-label">Cooperative Name</label>
              <input
                className="form-input"
                value={cooperativeName}
                onChange={e => setCooperativeName(e.target.value)}
                placeholder="e.g. Mbarara Coffee Growers Cooperative"
              />
            </div>
          )}

          <div>
            <label className="form-label">Tax Identification Number (TIN)</label>
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
            <p className="text-xs text-gray-500 mt-1">Demo TIN: 1000000042</p>
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
            <button onClick={() => setStep(3)} disabled={!uraData || (isTrading ? !businessName.trim() : !cooperativeName.trim())} className="btn-primary">Continue →</button>
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
              <li>{isTrading ? 'Business details' : 'Cooperative registration details'} provided by you</li>
              <li>Uploaded documents</li>
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
            {isTrading ? (
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-5 hover:border-navy-700 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-sm text-gray-700">Business Registration Certificate / Application Letter</p>
                    <p className="text-xs text-gray-500 mt-0.5">PDF or image · Max 5MB · Required</p>
                  </div>
                  {tradingDoc ? (
                    <div className="flex items-center gap-2 text-status-green text-sm font-medium">
                      <span>✅</span>
                      <span className="max-w-[160px] truncate">{tradingDoc.name}</span>
                      <button onClick={() => setTradingDoc(null)} className="text-gray-400 hover:text-status-red text-xs ml-1">✕</button>
                    </div>
                  ) : (
                    <button onClick={() => tradingDocRef.current?.click()} className="btn-secondary text-sm py-2">Choose File</button>
                  )}
                </div>
                <input ref={tradingDocRef} type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden"
                  onChange={e => handleFile(e.target.files?.[0] || null, setTradingDoc)} />
              </div>
            ) : (
              [
                { label: 'Cooperative Bylaws', file: bylaws, setter: setBylaws, ref: bylawsRef },
                { label: 'Member Roster', file: memberRoster, setter: setMemberRoster, ref: rosterRef },
              ].map(doc => (
                <div key={doc.label} className="border-2 border-dashed border-gray-300 rounded-xl p-5 hover:border-navy-700 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-sm text-gray-700">{doc.label}</p>
                      <p className="text-xs text-gray-500 mt-0.5">PDF or image · Max 5MB · Required</p>
                    </div>
                    {doc.file ? (
                      <div className="flex items-center gap-2 text-status-green text-sm font-medium">
                        <span>✅</span>
                        <span className="max-w-[160px] truncate">{doc.file.name}</span>
                        <button onClick={() => doc.setter(null)} className="text-gray-400 hover:text-status-red text-xs ml-1">✕</button>
                      </div>
                    ) : (
                      <button onClick={() => doc.ref.current?.click()} className="btn-secondary text-sm py-2">Choose File</button>
                    )}
                  </div>
                  <input ref={doc.ref} type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden"
                    onChange={e => handleFile(e.target.files?.[0] || null, doc.setter)} />
                </div>
              ))
            )}
          </div>

          <div className="flex justify-between">
            <button onClick={() => setStep(3)} className="btn-secondary">← Back</button>
            <button onClick={() => setStep(5)} disabled={!docsReady} className="btn-primary">Continue →</button>
          </div>
        </div>
      )}

      {/* STEP 5: Review & Submit */}
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
              <h3 className="font-bold text-navy-700 text-sm uppercase tracking-wide">
                {isTrading ? 'Business Details' : 'Cooperative Details'}
              </h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {isTrading ? (
                  <><span className="text-gray-500">Business Name</span><span className="font-medium">{businessName}</span></>
                ) : (
                  <><span className="text-gray-500">Cooperative Name</span><span className="font-medium">{cooperativeName}</span></>
                )}
                <span className="text-gray-500">TIN</span><span className="font-medium">{proposedTin}</span>
                <span className="text-gray-500">Tax Status</span><span className="font-medium text-status-green">{uraData?.taxStatus}</span>
                <span className="text-gray-500">Valid Until</span><span className="font-medium">{uraData?.clearanceValidUntil}</span>
              </div>
            </div>

            <div className="bg-navy-50 rounded-xl p-4 space-y-2">
              <h3 className="font-bold text-navy-700 text-sm uppercase tracking-wide">Documents</h3>
              <div className="space-y-1 text-sm">
                {isTrading && tradingDoc && <div className="flex items-center gap-2"><span className="text-status-green">✓</span>{tradingDoc.name}</div>}
                {!isTrading && bylaws && <div className="flex items-center gap-2"><span className="text-status-green">✓</span>{bylaws.name}</div>}
                {!isTrading && memberRoster && <div className="flex items-center gap-2"><span className="text-status-green">✓</span>{memberRoster.name}</div>}
              </div>
            </div>

            {isTrading && serviceInfo && (
              <div className="bg-gold-50 border-2 border-gold-500 rounded-xl p-4">
                <p className="text-sm font-bold text-yellow-900 mb-1">💳 Fee: {serviceInfo.feeCurrency} {Number(serviceInfo.feeAmount).toLocaleString()}</p>
                <p className="text-sm text-yellow-800">Payment will be required after submission. You can pay via MTN Mobile Money, Airtel Money, Card, or Bank Transfer through the Pesapal Sandbox (simulation only).</p>
              </div>
            )}

            <div className="bg-gold-50 border border-gold-500 rounded-lg p-4 text-sm text-yellow-900">
              <strong>SLA Commitment:</strong> Mbarara District Local Government will respond within <strong>2 working days</strong> and resolve within{' '}
              <strong>{isTrading ? '10' : '14'} working days</strong>.
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
