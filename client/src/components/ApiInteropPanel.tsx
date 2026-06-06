import { useState } from 'react';

interface ApiInteropPanelProps {
  niraData?: Record<string, unknown> | null;
  uraData?: Record<string, unknown> | null;
  applicationRef?: string;
}

export default function ApiInteropPanel({ niraData, uraData, applicationRef }: ApiInteropPanelProps) {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<'nira' | 'ura' | 'envelope'>('nira');

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
        className="w-full flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-gold-500 text-lg">🔌</span>
          <div>
            <p className="font-bold text-yellow-900 text-sm">API / Interoperability Readiness</p>
            <p className="text-xs text-yellow-800">UGHub-pattern integration payloads · Module 10</p>
          </div>
        </div>
        <span className="text-gold-500 font-bold">{open ? '↑' : '↓'}</span>
      </button>

      {open && (
        <div className="mt-4 border-t border-gold-500 pt-4">
          <div className="flex gap-2 mb-3">
            {(['nira', 'ura', 'envelope'] as const).map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`text-xs font-bold px-3 py-1.5 rounded-full transition-colors ${
                  tab === t ? 'bg-navy-700 text-white' : 'bg-white text-navy-700 border border-navy-700'
                }`}
              >
                {t === 'nira' ? 'NIRA Response' : t === 'ura' ? 'URA Response' : 'API Envelope'}
              </button>
            ))}
          </div>

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

          <div className="mt-3 space-y-1 text-xs text-yellow-800">
            <p>
              <strong>Correlation ID:</strong> <span className="font-mono">{corrId}</span>
            </p>
            <p>
              In production, these payloads would be signed and routed through the NITA-U UGHub Integration Spine
              under a formal Data Sharing Agreement (DSA) with NIRA and URA.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
