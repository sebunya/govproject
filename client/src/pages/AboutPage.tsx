import Header from '../components/Header';
import Footer from '../components/Footer';
import { useSearchParams } from 'react-router-dom';

const MODULES = [
  { id: '01', name: 'Citizen Profile & Identity', icon: '🪪', desc: 'NIN-based identity verification via NIRA UGHub-pattern API simulation. Citizen data locked from verified source, consent-gated.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
  { id: '02', name: 'Informed Consent', icon: '✅', desc: 'PDPA 2019 Section 10 compliant consent capture. Timestamped consent record stored against every application.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
  { id: '03', name: 'Evidence Documents', icon: '📎', desc: 'Secure multi-file document upload. Per-document officer verify/reject workflow. Max 5MB, PDF/image.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
  { id: '04', name: 'Officer Assignment & SOP', icon: '👨‍💼', desc: 'Automatic officer assignment on claim. 8-point Standard Operating Procedure checklist auto-populated from application data.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
  { id: '05', name: 'SLA Escalation', icon: '🚨', desc: 'Real-time SLA clock. Automatic escalation warning at 75% elapsed. One-click escalation to supervisor with notification.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
  { id: '06', name: 'Multi-Channel Notifications', icon: '📣', desc: 'SMS, email, portal, and internal notifications simulated at every workflow transition. Notification log with channel stats.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
  { id: '07', name: 'Payments — Pesapal Sandbox', icon: '💳', desc: 'Service fee collection via MTN Mobile Money, Airtel Money, Visa/Mastercard, Bank Transfer. Pesapal API 3.0 Sandbox pattern.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
  { id: '08', name: 'Dynamic Service Catalogue', icon: '📋', desc: 'Database-driven service registry with SLA commitments, fee schedules, required documents, and category classification.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
  { id: '09', name: 'M&E Reporting', icon: '📊', desc: 'Executive dashboard with live KPIs, weekly trend, district drill-down, officer workload, notification stats, payment revenue, citizen satisfaction scores.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
  { id: '10', name: 'API Interoperability', icon: '🔌', desc: 'UGHub Integration Spine pattern with correlationId, idempotencyKey, and envelope schema. NIRA, URA, and Pesapal payload inspection.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
  { id: '11', name: 'Roles & Permissions', icon: '🔐', desc: 'Four-persona RBAC: Citizen, Officer, Supervisor, Leadership. URL-param persona switching for demonstration. No JWT required for prototype.', status: 'Live', color: 'bg-status-greenBg border-status-green' },
];

const TECH = [
  { layer: 'Runtime', value: 'Node.js 22 (node:sqlite built-in, experimental)' },
  { layer: 'API Server', value: 'Express 4 · REST · JSON · Multer for file uploads' },
  { layer: 'Database', value: 'SQLite (DatabaseSync) · WAL mode · 6 tables' },
  { layer: 'Frontend', value: 'React 18 · React Router v6 · TanStack Query v5' },
  { layer: 'Build', value: 'Vite 5 · TypeScript 5 · esbuild' },
  { layer: 'Styling', value: 'Tailwind CSS 3 · Custom design tokens (navy, gold)' },
  { layer: 'Charts', value: 'Recharts (BarChart, LineChart, RadarChart)' },
  { layer: 'Repository', value: 'npm workspaces monorepo (server + client)' },
  { layer: 'Deployment', value: 'Hetzner VPS · systemd · Nginx reverse proxy' },
];

export default function AboutPage() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  return (
    <div>
      <Header persona={persona} />
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-10 space-y-12">

        <div>
          <h1 className="text-3xl font-extrabold text-navy-700">About NileGov Stack</h1>
          <div className="w-16 h-0.5 bg-gold-500 mt-2 mb-4" />
          <p className="text-lg text-gray-700 leading-relaxed max-w-3xl">
            NileGov Stack is a Uganda-built operational orchestration layer for government service delivery, designed to demonstrate what accountable, citizen-centred digital public services look like at the district level.
          </p>
          <div className="bg-navy-50 rounded-xl p-5 mt-4 grid md:grid-cols-3 gap-4">
            {[
              { label: 'Submitted to', value: 'Ministry of ICT & National Guidance Innovator Showcase · June 2026' },
              { label: 'Covering', value: 'Mbarara District Local Government · Agribusiness & Trading Licensing' },
              { label: 'Status', value: 'Prototype — Camera-ready demonstration system' },
            ].map(f => (
              <div key={f.label}>
                <p className="text-xs text-gray-500 font-semibold">{f.label}</p>
                <p className="text-sm font-bold text-navy-700 mt-0.5">{f.value}</p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-xl font-bold text-navy-700 mb-4">System Architecture</h2>
          <div className="bg-navy-900 rounded-2xl p-6 text-white font-mono text-xs leading-relaxed overflow-x-auto">
            <pre>{`CITIZEN PORTAL                   OFFICER DESK              SUPERVISOR          LEADERSHIP
─────────────                    ────────────              ──────────          ──────────
Service Catalogue   ──HTTP──►    Task Queue                Review Queue        Executive Dashboard
Application Form                 Review Interface          Countersign         M&E Reports
Application Status               Document Verify           Escalation Mgmt     Officer Workload
Notification Log                 Escalate / Reassign
Payment (Pesapal)
                                          │
                                    Express REST API
                                    Node.js 22 / SQLite
                                          │
              ┌───────────────────────────┼───────────────────────────┐
              │                           │                           │
        NIRA Simulation            URA Simulation            Pesapal Sandbox
        (Identity API)            (Tax Clearance)           (Payment Gateway)
        UGHub Pattern             UGHub Pattern             API 3.0 Pattern
        [SIMULATED]               [SIMULATED]               [SIMULATED]
              │                           │                           │
              └───────────────────────────┼───────────────────────────┘
                                    UGHub Envelope
                                 (correlationId · idempotencyKey · DSA)
                                 Production: NITA-U Integration Spine`}</pre>
          </div>
        </div>

        <div>
          <h2 className="text-xl font-bold text-navy-700 mb-4">11 Operational Modules</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {MODULES.map(m => (
              <div key={m.id} className={`border rounded-xl p-4 ${m.color}`}>
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{m.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-bold text-gray-500 font-mono">MOD-{m.id}</span>
                      <span className="font-bold text-sm text-navy-700">{m.name}</span>
                      <span className="ml-auto badge-green text-xs shrink-0">{m.status}</span>
                    </div>
                    <p className="text-xs text-gray-600 leading-relaxed">{m.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-xl font-bold text-navy-700 mb-4">Technology Stack</h2>
          <div className="card">
            <div className="divide-y divide-gray-100">
              {TECH.map(t => (
                <div key={t.layer} className="flex items-center gap-4 py-3">
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wide w-28 shrink-0">{t.layer}</span>
                  <span className="text-sm text-gray-800 font-medium">{t.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-xl font-bold text-navy-700 mb-4">Design Principles</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {[
              { icon: '🔒', title: 'Privacy by Design', desc: 'PDPA 2019 consent-first. Every data field has a legal basis. Simulated integrations are clearly labelled.' },
              { icon: '⏱', title: 'SLA Accountability', desc: 'Every application has a binding clock. Officers are measured. Escalation is automatic. Citizens see the timer.' },
              { icon: '🔌', title: 'Interoperability-Ready', desc: 'UGHub envelope pattern for all API exchanges. Production-ready to connect to NITA-U Integration Spine under DSA.' },
              { icon: '📊', title: 'Evidence-Based Governance', desc: 'M&E data flows from operational transactions. No manual reporting. District leadership sees live, trustworthy numbers.' },
              { icon: '🌍', title: 'Uganda-Built', desc: 'Designed for Ugandan districts: mobile money, UGX fees, UGHub APIs, NIRA/URA, local government SOP.' },
              { icon: '🎯', title: 'Zero-Dependency Auth', desc: 'No external auth providers. Persona-based access for prototype. Production would use NIDA-integrated SSO.' },
            ].map(p => (
              <div key={p.title} className="card">
                <div className="text-3xl mb-2">{p.icon}</div>
                <h3 className="font-bold text-navy-700 mb-1">{p.title}</h3>
                <p className="text-xs text-gray-600 leading-relaxed">{p.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Enterprise Integration */}
        <div>
          <h2 className="text-xl font-bold text-navy-700 mb-2">Enterprise System Integration</h2>
          <p className="text-sm text-gray-600 mb-5 max-w-3xl">
            NileGov Stack is designed as a <strong>citizen-facing workflow orchestration layer</strong> — not a replacement for enterprise back-office systems.
            Its REST API acts as a clean integration surface, allowing downstream enterprise platforms (ERPNext, IFMIS, OPM scorecards) to consume
            verified, structured permit data without needing to touch the citizen workflow engine directly.
          </p>

          {/* Architecture diagram */}
          <div className="bg-navy-900 rounded-2xl p-6 text-white font-mono text-xs leading-relaxed overflow-x-auto mb-6">
            <pre>{`CITIZEN / OFFICER / SUPERVISOR / LEADERSHIP
─────────────────────────────────────────────────────────────────────────────
        │                                │
   NileGov Stack REST API          NileGov Stack Workflow Engine
   (27 documented endpoints)       (SLA · Notifications · Payments · M&E)
        │                                │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼────────────────────────────────────────────────┐
        │              Enterprise Integration Layer                    │
        │                                                              │
        │   Webhook / Scheduled Sync / REST Pull                       │
        │   Authorization: District-issued API key (production)        │
        │   Envelope: UGHub correlationId + idempotencyKey             │
        └──┬──────────────┬───────────────┬──────────────┬────────────┘
           │              │               │              │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌────▼──────────┐
    │  ERPNext /  │ │   IFMIS    │ │    OPM     │ │  NITA-U UGHub │
    │  Frappe ERP │ │ (Treasury) │ │ Scorecard  │ │ Integration   │
    │             │ │            │ │            │ │ Spine         │
    │ - Revenue   │ │ - Fee      │ │ - KPI      │ │ - NIRA        │
    │   ledger    │ │   receipts │ │   reports  │ │ - URA         │
    │ - Asset     │ │ - Budget   │ │ - District │ │ - Pesapal     │
    │   register  │ │   codes    │ │   ranking  │ │   (Payment)   │
    └─────────────┘ └────────────┘ └────────────┘ └───────────────┘

    [SIMULATED — production integration requires signed DSAs and NITA-U approval]`}</pre>
          </div>

          {/* Integration cards */}
          <div className="grid md:grid-cols-2 gap-5 mb-5">
            {[
              {
                icon: '🏢',
                title: 'ERPNext / Frappe ERP',
                role: 'Back-office Finance & Asset Management',
                how: 'NileGov Stack fires a webhook (or accepts a scheduled pull) when a permit is approved and fee is verified. ERPNext receives a structured payload — permit number, applicant TIN, service code, amount, receipt reference — and creates the corresponding revenue ledger entry under the correct budget code. District assets tied to permits (market stalls, premises) update the asset register.',
                endpoint: 'POST /api/simulate/erp-sync',
                status: 'SIMULATED',
                why: 'ERPNext handles treasury accounting. NileGov handles the citizen workflow. Separation of concerns — neither system does the other\'s job.',
              },
              {
                icon: '🏦',
                title: 'IFMIS (Integrated Financial Management)',
                role: 'Ministry of Finance Treasury System',
                how: 'Verified fee payments from NileGov\'s Pesapal integration are forwarded to IFMIS as non-tax revenue receipts. The UGHub envelope (correlationId + idempotencyKey) ensures each payment is recorded exactly once. IFMIS assigns a consolidated fund reference that NileGov stores against the application for audit.',
                endpoint: 'POST /api/simulate/erp-sync (target: ifmis)',
                status: 'SIMULATED',
                why: 'IFMIS is the authoritative treasury ledger. NileGov does not attempt to replicate it — it feeds it.',
              },
              {
                icon: '📊',
                title: 'OPM Performance Scorecards',
                role: 'Office of the Prime Minister — District Rankings',
                how: 'The /api/dashboard/reports endpoint exposes structured M&E data (SLA compliance, approval rates, avg resolution time, officer workload) in a format designed to feed OPM\'s district service delivery scorecards. A scheduled export (daily or weekly) pushes this snapshot via NITA-U UGHub to the national reporting spine.',
                endpoint: 'GET /api/dashboard/reports',
                status: 'SIMULATED',
                why: 'OPM rankings currently rely on manual district returns. NileGov makes this automatic and trustworthy.',
              },
              {
                icon: '🔌',
                title: 'NITA-U UGHub Integration Spine',
                role: 'National IT Authority — Inter-Agency Middleware',
                how: 'All external API calls (NIRA identity, URA tax clearance, Pesapal payments, ERP sync) are wrapped in the UGHub envelope schema: schemaVersion, correlationId, idempotencyKey, source, destination, timestamp, and payload. In production, each call is routed through UGHub, logged for audit, and signed with government certificates under a Data Sharing Agreement.',
                endpoint: 'POST /api/simulate/nira · /api/simulate/ura · /api/simulate/pesapal · /api/simulate/erp-sync',
                status: 'SIMULATED',
                why: 'NITA-U is the single gateway for all government API traffic. NileGov is designed to plug in — not bypass it.',
              },
            ].map(item => (
              <div key={item.title} className="card border-l-4 border-l-navy-700 space-y-3">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{item.icon}</span>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-bold text-navy-700">{item.title}</h3>
                      <span className="text-xs bg-status-orange text-white font-bold px-2 py-0.5 rounded-full">{item.status}</span>
                    </div>
                    <p className="text-xs text-gray-500 font-semibold">{item.role}</p>
                  </div>
                </div>
                <p className="text-xs text-gray-700 leading-relaxed">{item.how}</p>
                <div className="bg-navy-50 rounded-lg p-2">
                  <span className="text-xs text-gray-500 font-semibold">Endpoint: </span>
                  <code className="text-xs font-mono text-navy-700">{item.endpoint}</code>
                </div>
                <div className="bg-gold-50 border border-gold-500 rounded-lg p-2 text-xs text-yellow-900">
                  <strong>Why separate?</strong> {item.why}
                </div>
              </div>
            ))}
          </div>

          {/* Integration decision note */}
          <div className="bg-navy-50 border border-navy-700 rounded-xl p-5">
            <h3 className="font-bold text-navy-700 mb-2">The Integration Decision</h3>
            <p className="text-sm text-gray-700 leading-relaxed mb-3">
              Whether Mbarara District adopts ERPNext, continues with IFMIS, or connects to a future national ERP is a procurement and policy decision
              for the Ministry of Finance and Ministry of Local Government. NileGov Stack is <strong>neutral on that decision</strong>.
            </p>
            <p className="text-sm text-gray-700 leading-relaxed mb-3">
              What NileGov Stack provides is a <strong>clean, documented REST API</strong> and a <strong>UGHub-compatible envelope pattern</strong>
              so that whatever enterprise system is chosen downstream can consume permit data, fee receipts, and M&E metrics without
              requiring changes to the citizen-facing workflow.
            </p>
            <div className="grid md:grid-cols-3 gap-3 text-xs mt-3">
              {[
                { label: 'Integration method', value: 'Webhook push or REST pull — configurable per system' },
                { label: 'Auth in production', value: 'District-issued API key + NITA-U UGHub certificate' },
                { label: 'Data format', value: 'JSON with UGHub envelope (correlationId + idempotencyKey)' },
                { label: 'Idempotency', value: 'Each event carries a unique idempotencyKey — safe to retry' },
                { label: 'Audit trail', value: 'Every sync event logged in NileGov audit log with correlationId' },
                { label: 'DSA requirement', value: 'Formal Data Sharing Agreement required per PDPA 2019 §28' },
              ].map(f => (
                <div key={f.label} className="bg-white rounded-lg p-3 border border-navy-100">
                  <p className="text-gray-500 font-semibold mb-0.5">{f.label}</p>
                  <p className="text-navy-700 font-medium">{f.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-gold-50 border border-gold-500 rounded-xl p-5 text-sm text-yellow-900">
          <strong>Prototype Disclaimer:</strong> NileGov Stack is a demonstration prototype. All government integrations (NIRA, URA, Pesapal) are simulated. No real citizen data is processed. This system is not connected to any live government database. Presented for evaluation purposes only.
        </div>
      </main>
      <Footer />
    </div>
  );
}
