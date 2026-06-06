import { useState } from 'react';
import axios from 'axios';

interface ApiInteropPanelProps {
  niraData?: Record<string, unknown> | null;
  uraData?: Record<string, unknown> | null;
  applicationRef?: string;
  app?: any;
}

export default function ApiInteropPanel({ niraData, uraData, applicationRef, app }: ApiInteropPanelProps) {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<'nira' | 'ura' | 'envelope' | 'erp'>('nira');
  const [erpTarget, setErpTarget] = useState<'erpnext' | 'ifmis' | 'opm'>('erpnext');
  const [erpResult, setErpResult] = useState<Record<string, unknown> | null>(null);
  const [erpLoading, setErpLoading] = useState(false);

  const simulateErpSync = async () => {
    setErpLoading(true);
    try {
      const res = await axios.post('/api/simulate/erp-sync', {
        target: erpTarget,
        applicationId: app?.id,
        referenceNumber: applicationRef || app?.referenceNumber,
        serviceCode: app?.serviceCode,
        permitNumber: app ? `MDLG-${app.serviceCode === 'trading-licence' ? 'TL' : 'AP'}-${(applicationRef || '').replace('NGS-', '')}` : undefined,
        feeAmount: app?.feeAmount,
        feeCurrency: app?.feeCurrency || 'UGX',
        receiptRef: app?.paymentStatus === 'verified' ? `SIM-RECEIPT-${applicationRef}` : null,
        tin: app?.proposedTin,
        fullName: app?.fullName,
        district: app?.district,
      });
      setErpResult(res.data);
    } finally {
      setErpLoading(false);
    }
  };

  const corrId = applicationRef
    ? `CORR-${applicationRef.replace('NGS-', '')}-${Date.now().toString(36).toUpperCase()}`
    : `CORR-${Math.random().toString(36).slice(2, 10).toUpperCase()}`;

  const envelope = {
    schemaVersion: '1.0',
    correlationId: corrId,
    idempotencyKey: `IDEM-${applicationRef || 'DEMO'}-${Date.now()}`,
    timestamp: new Date().toISOString(),
    source: 'NileGov Stack / Mbarara District Local Government',
    destination: 'NITA-U UGHub Integration Spine (SIMULATED)',
    disclaimer: 'Prototype simulation only. This payload does not reach live government systems.',
    payload: {
      nira: niraData ? { status: 'success', data: niraData } : { status: 'not_called' },
      ura: uraData ? { status: 'success', data: uraData } : { status: 'not_called' },
    },
  };

  return (
    <div className="card border border-gold-500 bg-gold-50">
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-controls="api-interop-panel"
        className="w-full flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-gold-500 text-lg" aria-hidden="true">🔌</span>
          <div>
            <p className="font-bold text-yellow-900 text-sm">API / Interoperability Readiness</p>
            <p className="text-xs text-yellow-800">UGHub-pattern integration payloads · Module 10</p>
          </div>
        </div>
        <span className="text-gold-500 font-bold" aria-hidden="true">{open ? '↑' : '↓'}</span>
      </button>

      {open && (
        <div id="api-interop-panel" className="mt-4 border-t border-gold-500 pt-4">
          <div className="flex flex-wrap gap-2 mb-3">
            {(['nira', 'ura', 'envelope', 'erp'] as const).map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`text-xs font-bold px-3 py-1.5 rounded-full transition-colors ${
                  tab === t ? 'bg-navy-700 text-white' : 'bg-white text-navy-700 border border-navy-700'
                }`}
              >
                {t === 'nira' ? 'NIRA Response' : t === 'ura' ? 'URA Response' : t === 'envelope' ? 'API Envelope' : '🏢 ERP Sync'}
              </button>
            ))}
          </div>

          {tab !== 'erp' && (
            <div className="bg-gray-900 rounded-lg p-4 overflow-auto max-h-64">
              <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap leading-relaxed">
                {JSON.stringify(
                  tab === 'nira' ? (niraData || { status: 'not_called', note: 'Verify identity in Step 1 first' })
                  : tab === 'ura' ? (uraData || { status: 'not_called', note: 'Check tax status in Step 2 first' })
                  : envelope,
                  null, 2
                )}
              </pre>
            </div>
          )}

          {tab === 'erp' && (
            <div className="space-y-3">
              <p className="text-xs text-yellow-800 leading-relaxed">
                NileGov Stack's REST API acts as a <strong>workflow layer</strong> that feeds verified permit data into enterprise back-office systems.
                Select a target system and fire a simulated sync — the response shows the exact payload NileGov would push in production.
              </p>
              <div className="flex gap-2 flex-wrap">
                {[
                  { id: 'erpnext', label: 'ERPNext / Frappe', desc: 'Journal entry' },
                  { id: 'ifmis', label: 'IFMIS Treasury', desc: 'NTR receipt' },
                  { id: 'opm', label: 'OPM Scorecard', desc: 'KPI event' },
                ].map(t => (
                  <button
                    key={t.id}
                    onClick={() => { setErpTarget(t.id as any); setErpResult(null); }}
                    className={`text-xs px-3 py-2 rounded-lg border-2 transition-colors ${
                      erpTarget === t.id ? 'border-navy-700 bg-navy-700 text-white' : 'border-gray-300 text-gray-700 hover:border-navy-700'
                    }`}
                  >
                    <span className="font-bold block">{t.label}</span>
                    <span className="opacity-70">{t.desc}</span>
                  </button>
                ))}
              </div>
              <button
                onClick={simulateErpSync}
                disabled={erpLoading}
                className="btn-primary text-sm py-2 w-full disabled:opacity-50"
              >
                {erpLoading ? 'Syncing…' : `▶ Simulate sync → ${erpTarget === 'erpnext' ? 'ERPNext' : erpTarget === 'ifmis' ? 'IFMIS' : 'OPM'}`}
              </button>
              {erpResult && (
                <>
                  <div className="flex items-center gap-2 text-xs text-status-green font-semibold">
                    <span>✅</span>
                    <span>SIMULATED_SUCCESS · correlationId: <span className="font-mono">{String(erpResult.correlationId)}</span></span>
                  </div>
                  <div className="bg-gray-900 rounded-lg p-4 overflow-auto max-h-64">
                    <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap leading-relaxed">
                      {JSON.stringify(erpResult, null, 2)}
                    </pre>
                  </div>
                </>
              )}
              <p className="text-xs text-yellow-800">
                ⚠ SIMULATED. Production integration requires NITA-U UGHub routing, signed DSA, and district API credentials.
              </p>
            </div>
          )}

          <div className="mt-3 space-y-1 text-xs text-yellow-800">
            <p>
              <strong>Correlation ID:</strong> <span className="font-mono">{corrId}</span>
            </p>
            <p>
              In production, all payloads are signed and routed through the NITA-U UGHub Integration Spine
              under formal Data Sharing Agreements (DSAs) with NIRA, URA, ERPNext, and IFMIS.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
