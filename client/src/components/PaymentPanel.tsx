import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

const METHODS = [
  { id: 'mobile_money_mtn', label: 'MTN Mobile Money', icon: '📱', color: 'bg-yellow-400 text-yellow-900' },
  { id: 'mobile_money_airtel', label: 'Airtel Money', icon: '📱', color: 'bg-red-500 text-white' },
  { id: 'card', label: 'Visa / Mastercard', icon: '💳', color: 'bg-navy-700 text-white' },
  { id: 'bank', label: 'Bank Transfer', icon: '🏦', color: 'bg-gray-700 text-white' },
];

interface PaymentPanelProps {
  applicationId: number;
  serviceCode: string;
  feeAmount: number;
  feeCurrency: string;
  readOnly?: boolean;
}

export default function PaymentPanel({ applicationId, feeAmount, feeCurrency, readOnly = false }: PaymentPanelProps) {
  const qc = useQueryClient();
  const [method, setMethod] = useState('mobile_money_mtn');
  const [mobileNumber, setMobileNumber] = useState('');
  const [stage, setStage] = useState<'form' | 'processing' | 'done'>('form');
  const [submitting, setSubmitting] = useState(false);

  const { data: payments = [] } = useQuery({
    queryKey: ['payments', applicationId],
    queryFn: () => axios.get(`/api/applications/${applicationId}/payments`).then(r => r.data),
    refetchInterval: 5000,
  });

  const existingPayment = (payments as any[])[0];

  const handleInitiate = async () => {
    setSubmitting(true);
    try {
      await axios.post(`/api/applications/${applicationId}/initiate-payment`, {
        purpose: 'Trading Licence Processing Fee',
        amount: feeAmount,
        currency: feeCurrency,
        method,
        mobileNumber,
      });
      qc.invalidateQueries({ queryKey: ['payments', applicationId] });
      setStage('processing');
      // Auto-simulate after 2.5s for demo
      setTimeout(async () => {
        const pays = await axios.get(`/api/applications/${applicationId}/payments`).then(r => r.data);
        if (pays[0]) {
          await axios.post(`/api/applications/${applicationId}/simulate-payment`, { paymentId: pays[0].id });
          qc.invalidateQueries({ queryKey: ['payments', applicationId] });
          qc.invalidateQueries({ queryKey: ['application', String(applicationId)] });
          setStage('done');
        }
      }, 2500);
    } finally {
      setSubmitting(false);
    }
  };

  if (existingPayment?.status === 'verified') {
    return (
      <div className="bg-status-greenBg border-2 border-status-green rounded-xl p-5">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-3xl">✅</span>
          <div>
            <p className="font-bold text-status-green text-lg">Payment Verified</p>
            <p className="text-sm text-gray-700">Receipt: <strong>{existingPayment.receiptRef}</strong></p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 bg-white rounded-lg p-3 border border-status-green">
          <div><span className="text-gray-400 block">Amount</span><span className="font-bold">{feeCurrency} {Number(feeAmount).toLocaleString()}</span></div>
          <div><span className="text-gray-400 block">Method</span><span className="font-bold capitalize">{existingPayment.method?.replace(/_/g, ' ')}</span></div>
          <div><span className="text-gray-400 block">Transaction Ref</span><span className="font-mono text-xs">{existingPayment.transactionRef}</span></div>
          <div><span className="text-gray-400 block">Verified At</span><span className="font-medium">{new Date(existingPayment.verifiedAt).toLocaleString('en-UG')}</span></div>
        </div>
        <p className="text-xs text-yellow-800 bg-gold-50 border border-gold-500 rounded-lg p-2 mt-3">
          ⚠ Prototype simulation only. No live payment was processed. (Pesapal API 3.0 Sandbox Pattern)
        </p>
      </div>
    );
  }

  if (existingPayment?.status === 'pending' || stage === 'processing') {
    return (
      <div className="bg-status-orangeBg border-2 border-status-orange rounded-xl p-5" role="status" aria-busy="true" aria-label="Payment processing">
        <div className="flex items-center gap-3 mb-3">
          <div className="animate-spin h-6 w-6 border-3 border-status-orange border-t-transparent rounded-full" aria-hidden="true" />
          <div>
            <p className="font-bold text-status-orange">Payment Processing…</p>
            <p className="text-sm text-gray-700">Simulating Pesapal gateway verification</p>
          </div>
        </div>
        <div className="space-y-1 text-xs text-gray-600">
          <p>✓ Order submitted to Pesapal Sandbox</p>
          <p className="animate-pulse">⟳ Awaiting payment confirmation…</p>
        </div>
      </div>
    );
  }

  if (readOnly) {
    return (
      <div className="bg-status-orangeBg border-2 border-status-orange rounded-xl p-5">
        <div className="flex items-center gap-3">
          <span className="text-3xl">💳</span>
          <div>
            <p className="font-bold text-status-orange">Service Fee Required</p>
            <p className="text-sm text-gray-700">{feeCurrency} {Number(feeAmount).toLocaleString()} must be paid before processing.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card border-2 border-gold-500">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl">💳</span>
        <div>
          <h3 className="font-bold text-navy-700 text-lg">Service Fee Payment</h3>
          <p className="text-sm text-gray-600">Required before your application can be processed</p>
        </div>
      </div>

      <div className="bg-navy-50 rounded-xl p-4 mb-5 text-center">
        <p className="text-xs text-gray-500 mb-1">Amount Due</p>
        <p className="text-3xl font-extrabold text-navy-700">{feeCurrency} {Number(feeAmount).toLocaleString()}</p>
        <p className="text-xs text-gray-500 mt-1">Trading Licence Processing Fee</p>
      </div>

      <div className="mb-4">
        <label className="form-label">Payment Method</label>
        <div className="grid grid-cols-2 gap-2">
          {METHODS.map(m => (
            <button
              key={m.id}
              onClick={() => setMethod(m.id)}
              className={`border-2 rounded-lg p-3 text-left transition-all ${
                method === m.id ? 'border-navy-700 bg-navy-50' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <span className="text-xl block mb-1">{m.icon}</span>
              <span className="text-xs font-semibold text-gray-700">{m.label}</span>
            </button>
          ))}
        </div>
      </div>

      {(method === 'mobile_money_mtn' || method === 'mobile_money_airtel') && (
        <div className="mb-4">
          <label className="form-label">Mobile Number</label>
          <input
            className="form-input"
            placeholder="+256 7XX XXX XXX"
            value={mobileNumber}
            onChange={e => setMobileNumber(e.target.value)}
          />
        </div>
      )}

      <button
        onClick={handleInitiate}
        disabled={submitting || (method.startsWith('mobile') && !mobileNumber.trim())}
        className="btn-primary w-full text-center"
      >
        {submitting ? 'Initiating…' : `Pay ${feeCurrency} ${Number(feeAmount).toLocaleString()} — Simulate via Pesapal Sandbox →`}
      </button>

      <p className="text-xs text-yellow-800 bg-gold-50 border border-gold-500 rounded-lg p-2 mt-3">
        ⚠ Prototype simulation only. No live payment will be processed. Pesapal API 3.0 Sandbox Pattern.
      </p>
    </div>
  );
}
