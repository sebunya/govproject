// Meta WhatsApp Business API (Cloud API)
// Docs: https://developers.facebook.com/docs/whatsapp/cloud-api/messages/text-messages
// Env: META_WHATSAPP_TOKEN, META_PHONE_NUMBER_ID
// Number format: international without + (e.g. 256700000000)

export interface WhatsAppResult {
  success: boolean;
  messageId?: string;
  simulated: boolean;
  provider: string;
  error?: string;
}

function normaliseNumber(phone: string): string {
  // Strip all non-digits, ensure Uganda prefix 256
  let digits = phone.replace(/\D/g, '');
  if (digits.startsWith('0') && digits.length === 10) digits = '256' + digits.slice(1);
  if (!digits.startsWith('256')) digits = '256' + digits;
  return digits;
}

export async function sendWhatsApp(to: string, message: string): Promise<WhatsAppResult> {
  const token         = process.env.META_WHATSAPP_TOKEN;
  const phoneNumberId = process.env.META_PHONE_NUMBER_ID;

  if (!token || !phoneNumberId) {
    console.log(`[WHATSAPP SIMULATED] → ${to} | ${message.slice(0, 60)}…`);
    return { success: true, simulated: true, provider: 'Meta WhatsApp Business API (SIMULATED)', messageId: `SIM-WA-${Date.now()}` };
  }

  const formattedTo = normaliseNumber(to);

  try {
    const res = await fetch(`https://graph.facebook.com/v19.0/${phoneNumberId}/messages`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messaging_product: 'whatsapp',
        recipient_type: 'individual',
        to: formattedTo,
        type: 'text',
        text: {
          preview_url: false,
          body: `🇺🇬 *NileGov Stack — Mbarara District*\n\n${message}\n\n_Track at: nilegov.mbarara.go.ug_`,
        },
      }),
    });

    const data = await res.json() as any;
    if (res.ok && data.messages?.[0]?.id) {
      console.log(`[WHATSAPP SENT] → ${formattedTo} | msgId: ${data.messages[0].id}`);
      return { success: true, simulated: false, provider: 'Meta WhatsApp Business API', messageId: data.messages[0].id };
    }
    const errMsg = data.error?.message || `HTTP ${res.status}`;
    console.error(`[WHATSAPP FAILED] → ${formattedTo} | ${errMsg}`);
    return { success: false, simulated: false, provider: 'Meta WhatsApp Business API', error: errMsg };
  } catch (err: any) {
    console.error(`[WHATSAPP ERROR] ${err.message}`);
    return { success: false, simulated: false, provider: 'Meta WhatsApp Business API', error: err.message };
  }
}
