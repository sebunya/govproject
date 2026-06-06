import { useState } from 'react';
import { useLocation } from 'react-router-dom';

const STEPS = [
  {
    id: 1,
    persona: 'citizen',
    label: 'Citizen Landing',
    paths: ['/portal'],
    action: 'Show live KPI stats. Explain SLA-bound, citizen-centred service delivery.',
    next: 'Click "Apply for a Service →"',
  },
  {
    id: 2,
    persona: 'citizen',
    label: 'Service Catalogue (Module 08)',
    paths: ['/portal/services'],
    action: 'Two services active: Agribusiness Permit (free) and Trading Licence (UGX 120k fee). Point to requiredDocs chips and fee labels.',
    next: 'Click "Apply Now →" on Trading Licence to demo the payment flow',
  },
  {
    id: 3,
    persona: 'citizen',
    label: 'Application Form — Identity (Step 1)',
    paths: ['/portal/apply'],
    action: 'NIN pre-filled as CM93019100ABC1J. Click "Verify Identity" — watch NIRA SIMULATED banner appear. Fields lock from NIRA data.',
    next: 'Continue → Step 2',
  },
  {
    id: 4,
    persona: 'citizen',
    label: 'Application Form — Business & Tax (Step 2)',
    paths: ['/portal/apply'],
    action: 'Business name entered. Click "Verify Tax Status" — URA SIMULATED banner. Clearance date shown. Consent → Documents → Review.',
    next: 'Submit. Copy reference number.',
  },
  {
    id: 5,
    persona: 'citizen',
    label: 'Application Status + Payment (Module 07)',
    paths: ['/portal/application/', '/portal/my-applications'],
    action: 'Open the new application. See Notification Log (Module 06) — SMS, email, portal events. Scroll to Payment panel — select MTN Mobile Money and pay.',
    next: 'Watch Pesapal Sandbox simulation (2.5s). Receipt appears.',
  },
  {
    id: 6,
    persona: 'officer',
    label: 'Officer Task Queue',
    paths: ['/desk'],
    action: 'Escalated apps sorted to top (red 🚨 badge). New Trading Licence submission visible. Click to open review.',
    next: 'Click the Trading Licence application',
  },
  {
    id: 7,
    persona: 'officer',
    label: 'Review Interface — Doc Verify + Escalate',
    paths: ['/desk/review'],
    action: 'SOP checklist shows "fee paid" item. Per-document ✓ Verify / ✕ Reject buttons. If SLA >75% → red escalation banner → "🚨 Escalate Now". Open API Interop panel.',
    next: 'Select ✅ Approve → Submit Decision',
  },
  {
    id: 8,
    persona: 'supervisor',
    label: 'Supervisor Queue — Escalated Tab',
    paths: ['/supervisor'],
    action: 'Two tabs: Pending Countersignature and 🚨 Escalated. Show escalated app (NGS-2026-0014) with SLA timer in red.',
    next: 'Switch to Countersign tab → expand → ✅ Countersign & Approve',
  },
  {
    id: 9,
    persona: 'citizen',
    label: 'Citizen — Approved + Notifications',
    paths: ['/portal/application/'],
    action: 'Status APPROVED — green banner. Scroll to Notification Log — system SMS + portal notifications fired on each status change. Rate the service ⭐⭐⭐⭐⭐',
    next: 'Switch to leadership persona',
  },
  {
    id: 10,
    persona: 'leadership',
    label: 'Leadership Dashboard + M&E Reports (Module 09)',
    paths: ['/dashboard'],
    action: 'Live KPIs, weekly trend, district drill-down. Click "📋 M&E Reports" tab — notification stats by channel, payment revenue (UGX), service breakdown, citizen satisfaction rating.',
    next: 'Click "📊 Export CSV" to download executive scorecard.',
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
                <span className="bg-gold-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">Step {current.id} of {STEPS.length}</span>
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
