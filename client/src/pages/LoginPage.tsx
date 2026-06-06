import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const DEMO_NIN = 'CM93019100ABC1J';

const PERSONAS = [
  {
    id: 'citizen',
    name: 'Akello Sarah Namugenyi',
    title: 'Community Member',
    dept: 'Mbarara District',
    avatar: '👩🏾‍🌾',
    route: '/portal',
    badge: 'Start Here',
    color: 'border-gold-500',
    accent: 'bg-gold-50',
    abilities: [
      'Browse and apply for government services',
      'Track your application in real time',
      'Upload documents and respond to officer queries',
      'Download your permit certificate',
      'Rate your service experience',
    ],
    credential: { label: 'Demo NIN', value: DEMO_NIN },
  },
  {
    id: 'officer',
    name: 'Tumusiime Robert',
    title: 'District Agricultural Officer',
    dept: 'Mbarara District Local Government',
    avatar: '👨🏾‍💼',
    route: '/desk',
    badge: null,
    color: 'border-gray-200',
    accent: '',
    abilities: [
      'Review and process incoming applications',
      'Verify documents and run the 8-point SOP checklist',
      'Approve, reject, or request additional information',
      'Escalate SLA-breached cases to supervisor',
      'Inspect API interoperability payloads',
    ],
    credential: null,
  },
  {
    id: 'supervisor',
    name: 'Nakamya Grace',
    title: 'Senior District Officer',
    dept: 'Mbarara District Local Government',
    avatar: '👩🏾‍💼',
    route: '/supervisor',
    badge: null,
    color: 'border-gray-200',
    accent: '',
    abilities: [
      'Countersign officer-approved applications',
      'Review and resolve escalated (SLA-breached) cases',
      'Reassign applications between officers',
      'Monitor officer workload and performance',
    ],
    credential: null,
  },
  {
    id: 'leadership',
    name: 'Executive Dashboard',
    title: 'District Leadership',
    dept: 'Mbarara District Local Government',
    avatar: '📊',
    route: '/dashboard',
    badge: null,
    color: 'border-gray-200',
    accent: '',
    abilities: [
      'View live M&E metrics and KPI dashboards',
      'Drill down by district, officer, and service type',
      'Export scorecard data as CSV',
      'Print executive-ready performance reports',
    ],
    credential: null,
  },
] as const;

type PersonaId = typeof PERSONAS[number]['id'];

const PERSONA_ROUTES: Record<PersonaId, string> = {
  citizen:    '/portal',
  officer:    '/desk',
  supervisor: '/supervisor',
  leadership: '/dashboard',
};

function NileLogo() {
  return (
    <svg width="48" height="48" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <rect width="36" height="36" rx="7" fill="#1A1A1A" stroke="#F5C000" strokeWidth="1.5"/>
      <rect x="0" y="28" width="12" height="8" fill="#1A1A1A"/>
      <rect x="12" y="28" width="12" height="8" fill="#F5C000"/>
      <rect x="24" y="28" width="12" height="8" fill="#C8102E"/>
      <text x="18" y="25" fontFamily="system-ui,sans-serif" fontWeight="800" fontSize="22"
            fill="#F5C000" textAnchor="middle" dominantBaseline="auto">N</text>
    </svg>
  );
}

export default function LoginPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const personaParam = searchParams.get('persona') as PersonaId | null;

  // Auto-redirect if a valid persona is already in the URL (backward-compat)
  useEffect(() => {
    if (personaParam && PERSONA_ROUTES[personaParam]) {
      navigate(`${PERSONA_ROUTES[personaParam]}?persona=${personaParam}`, { replace: true });
    }
  }, [personaParam, navigate]);

  const handleSelect = (p: typeof PERSONAS[number]) => {
    navigate(`${p.route}?persona=${p.id}`);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">

      {/* ── Page header ─────────────────────────────────────────────────── */}
      <div className="bg-navy-700 text-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-5 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <NileLogo />
            <div>
              <div className="font-extrabold text-lg leading-tight">NileGov Stack</div>
              <div className="text-gray-300 text-xs opacity-80">Mbarara District Local Government</div>
            </div>
          </div>
          <span className="bg-ug-red text-white text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wider hidden sm:inline">
            Prototype Demo
          </span>
        </div>
        {/* Uganda flag tri-stripe */}
        <div className="flex" style={{ height: '4px' }} aria-hidden="true">
          <div className="flex-1 bg-navy-900"/>
          <div className="flex-1 bg-gold-500"/>
          <div className="flex-1 bg-ug-red"/>
        </div>
      </div>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-8 sm:py-12" id="main-content">

        {/* Intro */}
        <div className="text-center mb-8 sm:mb-10">
          <div className="inline-flex items-center gap-2 bg-ug-redLight text-ug-red text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wider mb-4">
            <span aria-hidden="true">⚠</span>
            Prototype — Not a live government system
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-navy-700 mb-2 text-balance">
            Select your demo role to continue
          </h1>
          <p className="text-gray-500 text-sm sm:text-base max-w-lg mx-auto text-pretty">
            This showcase demonstrates government service delivery workflows for Mbarara District.
            Choose a persona to explore the system from that perspective.
          </p>
        </div>

        {/* Persona cards */}
        <div
          className="grid sm:grid-cols-2 gap-4 sm:gap-6"
          role="list"
          aria-label="Available demo personas"
        >
          {PERSONAS.map(p => (
            <article
              key={p.id}
              role="listitem"
              className={`bg-white rounded-2xl border-2 ${p.color} p-6 flex flex-col gap-4
                         hover:border-gold-500 hover:shadow-card-hover transition-all duration-200
                         cursor-pointer group ${p.accent}`}
              onClick={() => handleSelect(p)}
              tabIndex={0}
              onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSelect(p); } }}
              aria-label={`Continue as ${p.name}, ${p.title}`}
            >
              {/* Card header */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-14 h-14 rounded-2xl bg-navy-50 flex items-center justify-center text-3xl flex-shrink-0 group-hover:bg-gold-50 transition-colors">
                    {p.avatar}
                  </div>
                  <div>
                    <div className="font-extrabold text-navy-700 text-base leading-tight">{p.name}</div>
                    <div className="text-xs font-semibold text-ug-red mt-0.5 uppercase tracking-wide">{p.title}</div>
                    <div className="text-xs text-gray-400 mt-0.5">{p.dept}</div>
                  </div>
                </div>
                {p.badge && (
                  <span className="bg-ug-red text-white text-xs font-bold px-2 py-1 rounded-lg flex-shrink-0">
                    {p.badge}
                  </span>
                )}
              </div>

              {/* Abilities */}
              <ul className="space-y-1.5 flex-1" aria-label="Capabilities">
                {p.abilities.map(a => (
                  <li key={a} className="flex items-start gap-2 text-xs text-gray-600">
                    <span className="text-gold-500 mt-0.5 flex-shrink-0" aria-hidden="true">✓</span>
                    {a}
                  </li>
                ))}
              </ul>

              {/* Demo credentials */}
              {p.credential && (
                <div className="bg-navy-50 rounded-xl px-3 py-2.5 border border-navy-100">
                  <div className="text-2xs font-bold text-gray-400 uppercase tracking-widest mb-0.5">
                    Demo {p.credential.label}
                  </div>
                  <div className="font-mono text-sm font-bold text-navy-700 tracking-wider">
                    {p.credential.value}
                  </div>
                </div>
              )}

              {/* CTA */}
              <button
                className="w-full btn-primary group-hover:bg-navy-800 transition-colors"
                tabIndex={-1}
                aria-hidden="true"
              >
                Continue as {p.name.split(' ')[0]}
                <span aria-hidden="true">→</span>
              </button>
            </article>
          ))}
        </div>
      </main>

      {/* ── Footer disclaimer ─────────────────────────────────────────────── */}
      <footer className="border-t border-gray-200 bg-white py-6 px-4 print:hidden" role="contentinfo">
        <div className="max-w-5xl mx-auto text-center space-y-1">
          <p className="text-xs text-gray-400">
            <strong className="text-gray-600">NileGov Stack v1.0 — Prototype Only.</strong>{' '}
            This system uses simulated data and does not connect to live government databases.
            No real personal data is collected or processed.
          </p>
          <p className="text-xs text-gray-400">
            Built for the Ministry of ICT &amp; National Guidance Innovator Showcase, June 2026 ·
            Mbarara District Local Government · Uganda 🇺🇬
          </p>
          <div className="flex items-center justify-center gap-4 mt-2 text-xs text-gray-300">
            <span>Data Protection &amp; Privacy Act 2019</span>
            <span aria-hidden="true">·</span>
            <span>Electronic Transactions Act 2011</span>
            <span aria-hidden="true">·</span>
            <span>Local Governments Act (Cap 243)</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
