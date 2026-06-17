// Pesapal API 3.0 — East Africa's leading payment gateway
// Docs: https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json/api-reference
// Sandbox: https://cybqa.pesapal.com/pesapalv3
// Live:    https://pay.pesapal.com/v3
// Env: PESAPAL_CONSUMER_KEY, PESAPAL_CONSUMER_SECRET, PESAPAL_IPN_URL, PESAPAL_SANDBOX=true

let cachedToken: { token: string; expiresAt: number } | null = null;
let cachedIpnId: string | null = null;

function baseUrl(): string {
  return process.env.PESAPAL_SANDBOX !== 'false'
    ? 'https://cybqa.pesapal.com/pesapalv3'
    : 'https://pay.pesapal.com/v3';
}

export function isPesapalConfigured(): boolean {
  return !!(process.env.PESAPAL_CONSUMER_KEY && process.env.PESAPAL_CONSUMER_SECRET);
}

async function getToken(): Promise<string> {
  if (cachedToken && cachedToken.expiresAt > Date.now() + 60_000) return cachedToken.token;

  const res = await fetch(`${baseUrl()}/api/Auth/RequestToken`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({
      consumer_key: process.env.PESAPAL_CONSUMER_KEY,
      consumer_secret: process.env.PESAPAL_CONSUMER_SECRET,
    }),
  });
  const data = await res.json() as any;
  if (!data.token) throw new Error(`Pesapal auth failed: ${data.error?.message || res.status}`);

  const expiresAt = data.expiryDate
    ? new Date(data.expiryDate).getTime()
    : Date.now() + 5 * 60_000;
  cachedToken = { token: data.token, expiresAt };
  return data.token;
}

async function getIpnId(token: string): Promise<string> {
  if (cachedIpnId) return cachedIpnId;

  const ipnUrl = process.env.PESAPAL_IPN_URL ||
    `${process.env.APP_URL || 'http://localhost:3001'}/api/pesapal/ipn`;

  const res = await fetch(`${baseUrl()}/api/URLSetup/RegisterIPN`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ url: ipnUrl, ipn_notification_type: 'GET' }),
  });
  const data = await res.json() as any;
  if (!data.ipn_id) throw new Error(`IPN registration failed: ${data.error?.message || res.status}`);
  cachedIpnId = data.ipn_id;
  return cachedIpnId!;
}

export interface PesapalOrderParams {
  reference: string;
  amount: number;
  currency: string;
  description: string;
  callbackUrl: string;
  phoneNumber?: string;
  email?: string;
  firstName?: string;
  lastName?: string;
}

export interface PesapalOrderResult {
  success: boolean;
  trackingId?: string;
  redirectUrl?: string;
  simulated: boolean;
  error?: string;
}

export async function submitPesapalOrder(params: PesapalOrderParams): Promise<PesapalOrderResult> {
  if (!isPesapalConfigured()) {
    console.log(`[PESAPAL SIMULATED] ref: ${params.reference} amount: ${params.currency} ${params.amount}`);
    return {
      success: true,
      simulated: true,
      trackingId: `SIM-TRACK-${params.reference}-${Date.now()}`,
      redirectUrl: params.callbackUrl,
    };
  }

  try {
    const token = await getToken();
    const ipnId = await getIpnId(token);

    const res = await fetch(`${baseUrl()}/api/Transactions/SubmitOrderRequest`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        id: params.reference,
        currency: params.currency,
        amount: params.amount,
        description: params.description,
        callback_url: params.callbackUrl,
        redirect_mode: 0,
        notification_id: ipnId,
        billing_address: {
          email_address: params.email || 'citizen@mbarara.go.ug',
          phone_number: params.phoneNumber || '',
          first_name: params.firstName || 'Citizen',
          last_name: params.lastName || '',
          country_code: 'UG',
        },
      }),
    });
    const data = await res.json() as any;
    if (data.order_tracking_id) {
      console.log(`[PESAPAL ORDER] trackingId: ${data.order_tracking_id} ref: ${params.reference}`);
      return { success: true, simulated: false, trackingId: data.order_tracking_id, redirectUrl: data.redirect_url };
    }
    return { success: false, simulated: false, error: data.error?.message || `HTTP ${res.status}` };
  } catch (err: any) {
    console.error(`[PESAPAL ERROR] ${err.message}`);
    return { success: false, simulated: false, error: err.message };
  }
}

export interface PesapalStatusResult {
  success: boolean;
  status?: 'COMPLETED' | 'FAILED' | 'PENDING' | 'INVALID' | string;
  paymentMethod?: string;
  amount?: number;
  currency?: string;
  confirmationCode?: string;
  simulated: boolean;
  error?: string;
}

export async function getPesapalTransactionStatus(trackingId: string): Promise<PesapalStatusResult> {
  if (!isPesapalConfigured()) {
    return { success: true, simulated: true, status: 'COMPLETED', confirmationCode: `SIM-CONF-${Date.now()}` };
  }
  try {
    const token = await getToken();
    const res = await fetch(`${baseUrl()}/api/Transactions/GetTransactionStatus?orderTrackingId=${trackingId}`, {
      headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' },
    });
    const data = await res.json() as any;
    return {
      success: true,
      simulated: false,
      status: data.payment_status_description,
      paymentMethod: data.payment_method,
      amount: data.amount,
      currency: data.currency,
      confirmationCode: data.confirmation_code,
    };
  } catch (err: any) {
    return { success: false, simulated: false, error: err.message };
  }
}
