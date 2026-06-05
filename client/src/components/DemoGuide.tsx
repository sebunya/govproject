import { useState } from 'react';
import { useLocation } from 'react-router-dom';

const STEPS = [
  {
    id: 1,
    persona: 'citizen',
    path: '/portal',
    label: 'Citizen Landing',
    action: 'Show live stats. Explain SLA-bound service delivery.',
    next: 'Click "Apply for a Service →"',
  },
  {
    id: 2,
    persona: 'citizen',
    path: '/portal/services',
    label: 'Service Catalogue',
    action: 'Point to the active Agribusiness Permit service. 4 coming soon.',
    next: 'Click "Apply Now →"',
  },
  {
    id: 3,
    persona: 'citizen',
    path: '/portal/apply',
    label: 'Application Form — Step 1 (NIRA)',
    action: 'NIN is pre-filled. Click "Verify Identity" — watch NIRA SIMULATED banner.',
    next: 'Continue through all 5 steps',
  },
  {
    id: 4,
    persona: 'citizen',
    path: '/portal/apply',
    label: 'Application Form — Steps 2–5',
    action: 'Step 2: URA tax check (SIMULATED). Step 3: Consent. Step 4: Upload docs. Step 5: Review.',
    next: 'Submit. Copy reference number from confirmation screen.',
  },
  {
    id: 5,
    persona: 'citizen',
    path: '/portal/my-applications',
    label: 'My Applications',
    action: 'New app appears with pulsing NEW badge. SLA timer ticking live.',
    next: 'Switch persona → Officer (Tumusiime Robert)',
  },
  {
    id: 6,
    persona: 'officer',
    path: '/desk',
    label: 'Officer Task Queue',
    action: 'New submission appears at top (most urgent first). Red = SLA breach risk.',
    next: 'Click new application to open review',
  },
  {
    id: 7,
    persona: 'officer',
    path: '/desk/review',
    label: 'Officer Review Interface',
    action: 'SOP checklist auto-populates. NIRA + URA data shown. Check all 8 items.',
    next: 'Select ✅ Approve → add note → Submit Decision',
  },
  {
    id: 8,
    persona: 'supervisor',
    path: '/supervisor',
    label: 'Supervisor Queue',
    action: 'App now shows as Pending Countersignature. Expand to see officer\'s recommendation.',
    next: 'Select ✅ Countersign & Approve → Confirm Decision',
  },
  {
    id: 9,
    persona: 'citizen',
    path: '/portal/my-applications',
    label: 'Citizen — Application Approved',
    action: 'Status shows APPROVED — Permit Granted. Green banner with supervisor note.',
    next: 'Click into the application. Rate the service ⭐⭐⭐⭐⭐',
  },
  {
    id: 10,
    persona: 'leadership',
    path: '/dashboard',
    label: 'Leadership Dashboard',
    action: 'Live KPIs updated. SLA compliance, weekly trend, district drill-down.',
    next: 'Click a district row → 5-week trend chart. Scroll to Responsible Officers.',
  },
];

function matchStep(pathname: string, persona: string) {
  if (pathname.includes('/desk/review')) return STEPS.find(s => s.id === 7);
  if (pathname.startsWith('/desk')) return STEPS.find(s => s.id === 6);
  if (pathname.startsWith('/supervisor')) return STEPS.find(s => s.id === 8);
  if (pathname.startsWith('/dashboard')) return STEPS.find(s => s.id === 10);
  if (pathname.includes('/my-applications')) {
    return persona === 'citizen' ? STEPS.find(s => s.id === 5) : null;
  }
  if (pathname.includes('/apply')) return STEPS.find(s => s.id === 3);
  if (pathname.includes('/services')) return STEPS.find(s => s.id === 2);
  if (pathname.includes('/application/')) return STEPS.find(s => s.id === 9);
  if (pathname.startsWith('/portal')) return STEPS.find(s => s.id === 1);
  return null;
}

export default function DemoGuide({ persona }: { persona: string }) {
  const [open, setOpen] = useState(true);
  const [allOpen, setAllOpen] = useState(false);
  const location = useLocation();

  const current = matchStep(location.pathname, persona);

  return (
    <div className="fixed bottom-4 right-4 z-50 w-80 print:hidden">
      {open ? (
        <div className="bg-navy-900 text-white rounded-xl shadow-2xl border border-navy-700 overflow-hidden">
          {/* Header */}
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
                  </div>
                  <p className="text-gray-400 ml-6 leading-relaxed">{s.action}</p>
                </div>
              ))}
            </div>
          ) : current ? (
            <div className="px-4 py-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="bg-gold-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">Step {current.id} of {STEPS.length}</span>
                <span className="text-xs font-semibold text-gray-300">{current.label}</span>
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
