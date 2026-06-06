import { useState } from 'react';
import { useLocation } from 'react-router-dom';

const STEPS = [
  {
    id: 1,
    persona: 'citizen',
    label: 'Citizen Landing',
    paths: ['/portal'],
    action: 'Show live KPI stats pulled from the database — services available, avg resolution time, SLA compliance %. Explain citizen-centred service delivery.',
    next: 'Click "Apply for a Service →" or navigate to Service Catalogue',
  },
  {
    id: 2,
    persona: 'citizen',
    label: 'Service Catalogue (Module 08)',
    paths: ['/portal/services'],
    action: 'Two services active: Agribusiness Permit (free) and Trading Licence (UGX 120,000 fee). Point to requiredDocs chips, SLA commitments, and fee labels. Coming-soon services shown greyed out.',
    next: 'Click "Apply Now →" on Trading Licence to demo the payment flow',
  },
  {
    id: 3,
    persona: 'citizen',
    label: 'Application Form — Identity (Module 01)',
    paths: ['/portal/apply'],
    action: 'NIN pre-filled as CM93019100ABC1J. Click "Verify Identity via NIRA" — watch NIRA SIMULATED banner appear. Fields (name, DOB, gender, district) lock from verified NIRA response.',
    next: 'Continue → Step 2',
  },
  {
    id: 4,
    persona: 'citizen',
    label: 'Application Form — Business, Tax & Consent',
    paths: ['/portal/apply'],
    action: 'Business name entered. Click "Verify Tax Status via URA" — URA SIMULATED banner shows clearance date. Consent checkbox (Module 02 — PDPA 2019). Upload documents. Review summary → Submit.',
    next: 'Submit. Copy the reference number shown.',
  },
  {
    id: 5,
    persona: 'citizen',
    label: 'Application Status + Payment (Module 07)',
    paths: ['/portal/application/', '/portal/my-applications'],
    action: 'Open the new application. See SLA timers ticking. Scroll to Notification Log (Module 06) — SMS, email, portal events. Scroll to Payment panel — select MTN Mobile Money → Pay Now.',
    next: 'Watch Pesapal Sandbox simulation (2.5s). Receipt appears.',
  },
  {
    id: 6,
    persona: 'officer',
    label: 'Officer Task Queue',
    paths: ['/desk'],
    action: 'Escalated apps sorted to top (red 🚨 badge). NEW badge on recent submission. SLA progress bars visible. Search bar filters by name or reference. Click the Trading Licence application.',
    next: 'Click the Trading Licence application',
  },
  {
    id: 7,
    persona: 'officer',
    label: 'Review Interface — Docs, SOP, Escalate (Modules 03–05)',
    paths: ['/desk/review'],
    action: 'SOP checklist (8 items) auto-populated from data — "fee paid" item for Trading Licence. Per-document View / ✓ Verify / ✕ Reject. SLA >75% elapsed → red escalation banner → "🚨 Escalate". Open API Interop panel (Module 10): tabs show NIRA response, URA response, UGHub envelope, and 🏢 ERP Sync — fire a live simulated sync to ERPNext, IFMIS, or OPM Scorecard.',
    next: 'Select ✅ Approve → Submit Decision',
  },
  {
    id: 8,
    persona: 'supervisor',
    label: 'Supervisor Queue — Countersign & Escalated',
    paths: ['/supervisor'],
    action: 'Two tabs: Pending Countersignature and 🚨 Escalated. Show escalated app NGS-2026-0014 with SLA timer in red. Switch to Countersign tab → expand application details → ✅ Countersign & Approve.',
    next: 'Switch to citizen persona → open NGS-2026-0005',
  },
  {
    id: 9,
    persona: 'citizen',
    label: 'Approved — Permit Certificate & Notifications',
    paths: ['/portal/application/'],
    action: 'Navigate to My Applications → open NGS-2026-0005 (Akello Sarah, approved). Green APPROVED banner. Click "View Permit →" — official certificate with Republic of Uganda letterhead, signatures, stamp area, print/download. Notification Log shows SMS + portal events. Rate the service ⭐⭐⭐⭐⭐.',
    next: 'Switch to leadership persona',
  },
  {
    id: 10,
    persona: 'leadership',
    label: 'Leadership Dashboard + M&E Reports (Module 09)',
    paths: ['/dashboard'],
    action: 'Live KPIs — active applications, weekly trend chart, district drill-down, officer workload. Click "📋 M&E Reports" tab — notification delivery by channel, payment revenue in UGX, service approval breakdown, avg satisfaction rating. Click "📊 Export CSV" for executive scorecard.',
    next: 'Navigate to /track — public reference tracker',
  },
  {
    id: 11,
    persona: 'citizen',
    label: 'Public Reference Tracker',
    paths: ['/track'],
    action: 'No login required. Enter any reference e.g. NGS-2026-0005 → see status, SLA timers, citizen-friendly message. Useful for citizens without portal access. Try NGS-2026-0014 (under review + escalated).',
    next: 'Navigate to /about for architecture overview',
  },
  {
    id: 12,
    persona: 'citizen',
    label: 'About NileGov Stack',
    paths: ['/about'],
    action: 'Architecture ASCII diagram showing all tiers. 11 operational modules with status badges (all Live). Technology stack table — Node.js 22 built-in SQLite, React 18, Recharts. Six design principles. Prototype disclaimer.',
    next: 'Navigate to /api-docs',
  },
  {
    id: 13,
    persona: 'citizen',
    label: 'API Documentation (27 endpoints)',
    paths: ['/api-docs'],
    action: 'Search filter across all 27 endpoints. Method badges (GET/POST/PATCH). Expand any endpoint to see request/response schema. Click "▶ Test" on GET endpoints — live data returned from the running server. UGHub envelope pattern documented at bottom.',
    next: 'Switch back to citizen → demo withdrawal',
  },
  {
    id: 14,
    persona: 'citizen',
    label: 'Application Withdrawal',
    paths: ['/portal/application/'],
    action: 'Open a "submitted" application (e.g. NGS-2026-0018 or a freshly submitted one). Scroll to bottom — "Withdraw this application" link. Confirm → status changes to Withdrawn (grey badge). Demonstrates citizen control of their data (PDPA right to erasure principle).',
    next: '🎬 End of demo — all 11 modules demonstrated.',
  },
];

function matchStep(pathname: string) {
  if (pathname.includes('/desk/review')) return STEPS.find(s => s.id === 7);
  if (pathname.startsWith('/desk')) return STEPS.find(s => s.id === 6);
  if (pathname.startsWith('/supervisor')) return STEPS.find(s => s.id === 8);
  if (pathname.startsWith('/dashboard')) return STEPS.find(s => s.id === 10);
  if (pathname.includes('/my-applications')) return STEPS.find(s => s.id === 5);
  if (pathname.includes('/application/')) return STEPS.find(s => s.id === 9);
  if (pathname.includes('/apply')) return STEPS.find(s => s.id === 3);
  if (pathname.includes('/services')) return STEPS.find(s => s.id === 2);
  if (pathname.startsWith('/track')) return STEPS.find(s => s.id === 11);
  if (pathname.startsWith('/about')) return STEPS.find(s => s.id === 12);
  if (pathname.startsWith('/api-docs')) return STEPS.find(s => s.id === 13);
  if (pathname.startsWith('/portal')) return STEPS.find(s => s.id === 1);
  return null;
}

const PERSONA_COLOR: Record<string, string> = {
  citizen: 'bg-status-green',
  officer: 'bg-navy-700',
  supervisor: 'bg-gold-500',
  leadership: 'bg-status-red',
};

export default function DemoGuide({ persona }: { persona: string }) {
  const [open, setOpen] = useState(true);
  const [allOpen, setAllOpen] = useState(false);
  const location = useLocation();

  const current = matchStep(location.pathname);

  return (
    <div className="fixed bottom-4 right-4 z-50 w-80 print:hidden">
      {open ? (
        <div className="bg-navy-900 text-white rounded-xl shadow-2xl border border-navy-700 overflow-hidden">
          <div className="bg-gold-500 px-4 py-2.5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-white">🎬 Demo Guide</span>
              <button
                onClick={() => setAllOpen(!allOpen)}
                className="text-xs text-white opacity-70 hover:opacity-100 underline"
              >
                {allOpen ? 'hide all' : 'all steps'}
              </button>
            </div>
            <button onClick={() => setOpen(false)} className="text-white opacity-60 hover:opacity-100 text-lg leading-none">✕</button>
          </div>

          {allOpen ? (
            <div className="max-h-96 overflow-y-auto divide-y divide-navy-700">
              {STEPS.map(s => (
                <div key={s.id} className={`px-4 py-2.5 text-xs ${s === current ? 'bg-navy-700' : ''}`}>
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${s === current ? 'bg-gold-500 text-white' : 'bg-navy-700 text-gray-400'}`}>{s.id}</span>
                    <span className={`font-semibold ${s === current ? 'text-gold-500' : 'text-gray-300'}`}>{s.label}</span>
                    <span className={`text-white text-xs px-1.5 py-0.5 rounded-full ml-auto shrink-0 ${PERSONA_COLOR[s.persona] || 'bg-navy-700'}`}>{s.persona}</span>
                  </div>
                  <p className="text-gray-400 ml-6 leading-relaxed">{s.action}</p>
                </div>
              ))}
            </div>
          ) : current ? (
            <div className="px-4 py-3">
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                <span className="bg-gold-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">Step {current.id}/{STEPS.length}</span>
                <span className={`text-white text-xs font-bold px-2 py-0.5 rounded-full ${PERSONA_COLOR[current.persona] || 'bg-navy-700'}`}>{current.persona}</span>
                <span className="text-xs font-semibold text-gray-300 flex-1">{current.label}</span>
              </div>
              <p className="text-sm text-white leading-relaxed mb-3">{current.action}</p>
              <div className="bg-navy-700 rounded-lg px-3 py-2">
                <p className="text-xs text-gold-500 font-semibold mb-0.5">Next →</p>
                <p className="text-xs text-gray-200">{current.next}</p>
              </div>
            </div>
          ) : (
            <div className="px-4 py-3 text-sm text-gray-400">Navigate to a demo screen to see guidance.</div>
          )}
        </div>
      ) : (
        <button
          onClick={() => setOpen(true)}
          className="bg-gold-500 hover:bg-yellow-600 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-xl transition-colors flex items-center gap-2"
        >
          🎬 Demo Guide
        </button>
      )}
    </div>
  );
}
