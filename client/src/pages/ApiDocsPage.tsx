import { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { useSearchParams } from 'react-router-dom';

const BASE = 'http://localhost:3001';

interface Endpoint {
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  path: string;
  summary: string;
  module: string;
  auth: string;
  request?: string;
  response: string;
  notes?: string;
}

const ENDPOINTS: Endpoint[] = [
  { method: 'GET', path: '/api/health', summary: 'System health check', module: 'System', auth: 'None',
    response: `{ "status": "ok", "version": "1.0.0-demo", "timestamp": "...", "database": "connected", "applicationCount": 25, "disclaimer": "Prototype only." }` },
  { method: 'GET', path: '/api/services', summary: 'List all services in the catalogue', module: 'MOD-08 Service Catalogue', auth: 'None',
    response: `[{ "id": 1, "code": "cooperative-permit", "name": "Cooperative Registration & Agribusiness Permit", "category": "Agriculture", "slaResponseHours": 48, "slaResolveHours": 336, "feeAmount": 0, "feeCurrency": "UGX", "requiredDocs": "Cooperative Bylaws,Member Roster", "active": 1 }]` },
  { method: 'GET', path: '/api/officers', summary: 'List all officers', module: 'MOD-04 Assignment', auth: 'Officer',
    response: `[{ "id": 1, "name": "Tumusiime Robert", "role": "officer", "district": "Mbarara" }]` },
  { method: 'GET', path: '/api/applications', summary: 'List applications (filtered by persona)', module: 'Core', auth: 'Persona',
    request: `Query params: ?persona=citizen&nin=CM93019100ABC1J\n?persona=officer\n?persona=supervisor`,
    response: `[{ "id": 1, "referenceNumber": "NGS-2026-0001", "serviceCode": "cooperative-permit", "fullName": "...", "status": "approved", "escalationState": "not_escalated", ... }]` },
  { method: 'POST', path: '/api/applications', summary: 'Submit a new application', module: 'Core', auth: 'Citizen',
    request: `FormData fields:\nnin, fullName, dateOfBirth, district, gender,\nserviceCode, cooperativeName OR businessName,\nproposedTin, taxStatus, taxClearanceValidUntil,\nconsentTimestamp, bylaws (file), memberRoster (file) OR bizReg (file)`,
    response: `{ "referenceNumber": "NGS-2026-0026", "id": 26 }` },
  { method: 'GET', path: '/api/applications/:id', summary: 'Get single application with docs, audit log, fee, payment status', module: 'Core', auth: 'Persona',
    response: `{ ...application fields, "documents": [...], "auditLog": [...], "feeAmount": 120000, "feeCurrency": "UGX", "paymentStatus": "verified" }` },
  { method: 'GET', path: '/api/track/:ref', summary: 'Public reference number tracker (no auth)', module: 'Core', auth: 'None',
    request: `URL param: /api/track/NGS-2026-0001`,
    response: `{ "referenceNumber": "NGS-2026-0001", "serviceType": "...", "status": "approved", "submittedAt": "...", "resolvedAt": "..." }` },
  { method: 'PATCH', path: '/api/applications/:id/claim', summary: 'Officer claims application for review', module: 'MOD-04 Assignment', auth: 'Officer',
    response: `{ ...full application with documents, auditLog, feeAmount, paymentStatus }` },
  { method: 'PATCH', path: '/api/applications/:id/officer-decision', summary: 'Submit officer decision', module: 'MOD-04 Assignment', auth: 'Officer',
    request: `{ "decision": "approved" | "rejected" | "more_info_requested", "notes": "..." }`,
    response: `{ "ok": true }`, notes: 'Fires SMS, email, portal, internal notifications. Moves to pending_countersign if approved.' },
  { method: 'PATCH', path: '/api/applications/:id/supervisor-decision', summary: 'Supervisor countersignature', module: 'MOD-04 Assignment', auth: 'Supervisor',
    request: `{ "decision": "approved" | "rejected", "notes": "..." }`,
    response: `{ "ok": true }`, notes: 'Final decision. Fires permit-granted notification to citizen.' },
  { method: 'PATCH', path: '/api/applications/:id/citizen-response', summary: 'Citizen responds to more_info_requested', module: 'Core', auth: 'Citizen',
    request: `FormData: message (text), additionalDoc (file, optional)`,
    response: `{ "ok": true }` },
  { method: 'PATCH', path: '/api/applications/:id/escalate', summary: 'Escalate application to supervisor', module: 'MOD-05 SLA Escalation', auth: 'Officer',
    response: `{ "ok": true }`, notes: 'Sets escalationState=escalated. Fires internal notification to supervisor.' },
  { method: 'PATCH', path: '/api/applications/:id/reassign', summary: 'Reassign to different officer', module: 'MOD-04 Assignment', auth: 'Officer',
    request: `{ "officerId": 3 }`,
    response: `{ "ok": true }` },
  { method: 'PATCH', path: '/api/applications/:id/withdraw', summary: 'Citizen withdraws application', module: 'Core', auth: 'Citizen',
    response: `{ "ok": true }`, notes: 'Only allowed when status=submitted. Sets status=withdrawn.' },
  { method: 'PATCH', path: '/api/applications/:id/rate', summary: 'Citizen rates the service', module: 'MOD-09 M&E', auth: 'Citizen',
    request: `{ "rating": 5, "comment": "..." }`,
    response: `{ "ok": true }` },
  { method: 'GET', path: '/api/applications/:id/notifications', summary: 'Notification log for application', module: 'MOD-06 Notifications', auth: 'Persona',
    response: `[{ "id": 1, "type": "citizen", "channel": "sms", "recipient": "+256...", "message": "...", "status": "simulated_sent", "createdAt": "..." }]` },
  { method: 'GET', path: '/api/applications/:id/payments', summary: 'Payment records for application', module: 'MOD-07 Payments', auth: 'Persona',
    response: `[{ "id": 1, "purpose": "Trading Licence Processing Fee", "amount": 120000, "currency": "UGX", "method": "mobile_money_mtn", "status": "verified", "receiptRef": "SIM-RECEIPT-...", "verifiedAt": "..." }]` },
  { method: 'POST', path: '/api/applications/:id/initiate-payment', summary: 'Initiate payment for fee-based service', module: 'MOD-07 Payments', auth: 'Citizen',
    request: `{ "purpose": "...", "amount": 120000, "currency": "UGX", "method": "mobile_money_mtn", "mobileNumber": "+256700..." }`,
    response: `{ "ok": true }` },
  { method: 'POST', path: '/api/applications/:id/simulate-payment', summary: 'Simulate Pesapal payment verification', module: 'MOD-07 Payments', auth: 'Citizen',
    request: `{ "paymentId": 5 }`,
    response: `{ "ok": true }`, notes: 'Pesapal API 3.0 Sandbox. Sets status=verified, generates receipt ref, fires notification.' },
  { method: 'PATCH', path: '/api/documents/:docId/verify', summary: 'Officer verifies or rejects a document', module: 'MOD-03 Evidence', auth: 'Officer',
    request: `{ "status": "verified" | "rejected", "notes": "..." }`,
    response: `{ "ok": true }` },
  { method: 'POST', path: '/api/simulate/nira', summary: 'Simulate NIRA identity verification', module: 'MOD-01 Identity / MOD-10 API Interop', auth: 'None',
    request: `{ "nin": "CM93019100ABC1J" }`,
    response: `{ "fullName": "Akello Sarah Namugenyi", "dateOfBirth": "1991-04-12", "district": "Mbarara", "gender": "Female", "_simulated": true, "correlationId": "NIRA-...", "source": "NIRA Identity API (UGHub Pattern — SIMULATED)" }`,
    notes: 'SIMULATED. No connection to live NIRA systems. UGHub envelope pattern.' },
  { method: 'POST', path: '/api/simulate/ura', summary: 'Simulate URA tax clearance check', module: 'MOD-10 API Interop', auth: 'None',
    request: `{ "tin": "1000000042" }`,
    response: `{ "taxStatus": "Compliant", "clearanceValidUntil": "2026-12-31", "_simulated": true, "correlationId": "URA-..." }`,
    notes: 'SIMULATED. No connection to live URA systems.' },
  { method: 'POST', path: '/api/simulate/pesapal', summary: 'Simulate Pesapal payment gateway', module: 'MOD-07 Payments', auth: 'None',
    request: `{ "amount": 120000, "currency": "UGX", "reference": "NGS-2026-0018", "method": "mobile_money_mtn" }`,
    response: `{ "orderId": "PES-...", "transactionRef": "SIM-PAY-...", "status": "COMPLETED", "_simulated": true }`,
    notes: 'SIMULATED. Pesapal API 3.0 Sandbox pattern only.' },
  { method: 'GET', path: '/api/dashboard', summary: 'Leadership dashboard KPIs', module: 'MOD-09 M&E', auth: 'Leadership',
    response: `{ "todayProcessed": 3, "weekProcessed": 12, "avgResolutionHours": 48, "slaCompliancePercent": 94, "activeApplications": 6, "escalatedCount": 1, "bottlenecks": [...], "districtStats": [...], "weeklyTrend": [...] }` },
  { method: 'GET', path: '/api/dashboard/reports', summary: 'Full M&E snapshot with all metrics', module: 'MOD-09 M&E', auth: 'Leadership',
    response: `{ "totals": { "total": 25, "resolved": 19, "approved": 17, "approvalRate": 89, "slaCompliance": 100, "escalated": 1, "avgRating": 4.5 }, "notifications": { "total": 146, "byChannel": {...} }, "payments": { "totalVerifiedAmount": 720000, "verifiedCount": 6 }, "byService": [...] }` },
  { method: 'GET', path: '/api/dashboard/officers', summary: 'Officer performance statistics', module: 'MOD-09 M&E', auth: 'Leadership',
    response: `[{ "id": 1, "name": "Tumusiime Robert", "role": "officer", "total": 8, "active": 2, "resolved": 6, "slaCompliance": 100, "avgResolutionHours": 36 }]` },
  { method: 'GET', path: '/api/dashboard/district-trend', summary: '5-week SLA compliance trend by district', module: 'MOD-09 M&E', auth: 'Leadership',
    response: `{ "trend": { "Mbarara": [{ "week": "2026-W18", "compliance": 100, "total": 5, "onTime": 5, "slaBreached": 0 }, ...] } }` },
  { method: 'POST', path: '/api/simulate/erp-sync', summary: 'Simulate ERP / IFMIS / OPM enterprise integration sync', module: 'MOD-10 API Interop — Enterprise', auth: 'None',
    request: `{
  "target": "erpnext" | "ifmis" | "opm",
  "applicationId": 5,
  "referenceNumber": "NGS-2026-0005",
  "serviceCode": "trading-licence",
  "permitNumber": "MDLG-TL-2026-0005",
  "feeAmount": 120000,
  "feeCurrency": "UGX",
  "receiptRef": "SIM-RECEIPT-ABC123",
  "tin": "1000000042",
  "fullName": "Akello Sarah Namugenyi",
  "district": "Mbarara"
}`,
    response: `{
  "schemaVersion": "1.0",
  "correlationId": "ERP-1748952000000-A3F9K",
  "idempotencyKey": "IDEM-NGS-2026-0005-1748952000000",
  "timestamp": "2026-06-06T10:00:00.000Z",
  "source": "NileGov Stack / Mbarara District Local Government",
  "destination": "ERPNext / Frappe ERP",
  "action": "create_journal_entry",
  "status": "SIMULATED_SUCCESS",
  "payload": {
    "doctype": "Journal Entry",
    "voucher_type": "Journal Entry",
    "accounts": [
      { "account": "1110 - Cash and Bank", "debit_in_account_currency": 120000 },
      { "account": "4110 - Non-Tax Revenue — Licences", "credit_in_account_currency": 120000 }
    ],
    "custom_permit_number": "MDLG-TL-2026-0005",
    "currency": "UGX"
  },
  "_simulated": true
}`,
    notes: 'SIMULATED. Three targets: erpnext (journal entry), ifmis (NTR receipt), opm (KPI event). Each response is wrapped in the UGHub envelope with correlationId + idempotencyKey. Production integration requires signed DSA and NITA-U routing.' },
];

const METHOD_COLOR: Record<string, string> = {
  GET: 'bg-status-green text-white',
  POST: 'bg-navy-700 text-white',
  PATCH: 'bg-status-orange text-white',
  DELETE: 'bg-status-red text-white',
};

export default function ApiDocsPage() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';
  const [expanded, setExpanded] = useState<string | null>(null);
  const [filter, setFilter] = useState('');
  const [testResult, setTestResult] = useState<Record<string, string>>({});

  const filtered = ENDPOINTS.filter(e =>
    filter === '' ||
    e.path.toLowerCase().includes(filter.toLowerCase()) ||
    e.summary.toLowerCase().includes(filter.toLowerCase()) ||
    e.module.toLowerCase().includes(filter.toLowerCase())
  );

  const testEndpoint = async (e: Endpoint) => {
    try {
      const url = `${BASE}${e.path.replace(':id', '1').replace(':ref', 'NGS-2026-0001').replace(':docId', '1')}`;
      const res = await fetch(url);
      const data = await res.json();
      setTestResult(prev => ({ ...prev, [e.path]: JSON.stringify(data, null, 2).slice(0, 500) + (JSON.stringify(data).length > 500 ? '\n...' : '') }));
    } catch {
      setTestResult(prev => ({ ...prev, [e.path]: 'Could not reach server. Start with `npm run dev`.' }));
    }
  };

  return (
    <div>
      <Header persona={persona} />
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-10 space-y-8">
        <div>
          <h1 className="text-3xl font-extrabold text-navy-700">API Documentation</h1>
          <div className="w-16 h-0.5 bg-gold-500 mt-2 mb-3" />
          <p className="text-gray-600">NileGov Stack REST API · Base URL: <code className="bg-gray-100 px-2 py-0.5 rounded text-sm font-mono">{BASE}</code></p>
          <div className="bg-gold-50 border border-gold-500 rounded-xl p-4 mt-4 text-sm text-yellow-900">
            <strong>Prototype API:</strong> All endpoints are open — no authentication tokens required. Access is controlled by <code className="font-mono">?persona=</code> URL parameter for demonstration purposes. Production would require NIDA-integrated SSO and role-based JWT.
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Endpoints', value: ENDPOINTS.length },
            { label: 'Modules Covered', value: 11 },
            { label: 'Simulated Integrations', value: 3 },
            { label: 'API Version', value: '1.0' },
          ].map(s => (
            <div key={s.label} className="bg-navy-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-extrabold text-navy-700">{s.value}</div>
              <div className="text-xs text-gray-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>

        <input
          className="form-input"
          placeholder="Search endpoints by path, summary or module…"
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />

        <div className="space-y-3">
          {filtered.map(e => {
            const key = `${e.method}:${e.path}`;
            const isOpen = expanded === key;
            return (
              <div key={key} className="card border border-gray-200 hover:border-navy-700 transition-colors">
                <button className="w-full flex items-center gap-3 text-left" onClick={() => setExpanded(isOpen ? null : key)}>
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-full shrink-0 ${METHOD_COLOR[e.method]}`}>{e.method}</span>
                  <code className="text-sm font-mono text-navy-700 flex-1">{e.path}</code>
                  <span className="text-xs bg-navy-50 text-navy-700 px-2 py-0.5 rounded-full font-semibold shrink-0 hidden md:inline">{e.module}</span>
                  <span className="text-gray-400 ml-2">{isOpen ? '↑' : '↓'}</span>
                </button>
                <p className="text-sm text-gray-600 mt-1 ml-16">{e.summary}</p>

                {isOpen && (
                  <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">
                    <div className="flex flex-wrap gap-3 text-xs">
                      <span className="bg-navy-50 text-navy-700 px-2 py-1 rounded font-semibold">Module: {e.module}</span>
                      <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded font-semibold">Auth: {e.auth}</span>
                    </div>
                    {e.notes && (
                      <div className="bg-gold-50 border border-gold-500 rounded-lg p-3 text-xs text-yellow-900">{e.notes}</div>
                    )}
                    {e.request && (
                      <div>
                        <p className="text-xs font-bold text-gray-500 uppercase mb-1">Request</p>
                        <pre className="bg-gray-900 text-green-400 text-xs font-mono p-3 rounded-lg overflow-auto whitespace-pre-wrap">{e.request}</pre>
                      </div>
                    )}
                    <div>
                      <p className="text-xs font-bold text-gray-500 uppercase mb-1">Response</p>
                      <pre className="bg-gray-900 text-green-400 text-xs font-mono p-3 rounded-lg overflow-auto whitespace-pre-wrap">{e.response}</pre>
                    </div>
                    {e.method === 'GET' && (
                      <div>
                        <button
                          onClick={() => testEndpoint(e)}
                          className="btn-secondary text-xs py-1.5"
                        >
                          ▶ Test (GET only)
                        </button>
                        {testResult[e.path] && (
                          <pre className="mt-2 bg-navy-900 text-green-400 text-xs font-mono p-3 rounded-lg overflow-auto max-h-48 whitespace-pre-wrap">{testResult[e.path]}</pre>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="card border border-gold-500 bg-gold-50">
          <h2 className="font-bold text-yellow-900 mb-3">UGHub Integration Envelope Pattern</h2>
          <p className="text-sm text-yellow-800 mb-3">All inter-agency API calls use the following envelope schema for traceability and idempotency:</p>
          <pre className="bg-gray-900 text-green-400 text-xs font-mono p-4 rounded-xl overflow-auto whitespace-pre-wrap">{`{
  "schemaVersion": "1.0",
  "correlationId": "CORR-2026-0001-A3F9K2",
  "idempotencyKey": "IDEM-NGS-2026-0001-1748952000000",
  "timestamp": "2026-06-03T10:00:00.000Z",
  "source": "NileGov Stack / Mbarara District Local Government",
  "destination": "NITA-U UGHub Integration Spine (SIMULATED)",
  "disclaimer": "Prototype simulation only.",
  "payload": {
    "nira": { "status": "success", "data": { ... } },
    "ura": { "status": "success", "data": { ... } }
  }
}`}</pre>
          <p className="text-xs text-yellow-800 mt-3">In production, payloads would be signed with government-issued certificates and routed through the NITA-U Integration Spine under a formal Data Sharing Agreement (DSA).</p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
