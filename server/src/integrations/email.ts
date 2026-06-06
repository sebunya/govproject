// ZeptoMail transactional email — Zoho's dedicated transactional mail service
// Docs: https://www.zoho.com/zeptomail/help/api/email-sending.html
// Env: ZEPTO_API_KEY, ZEPTO_FROM_EMAIL, ZEPTO_FROM_NAME

export interface EmailResult {
  success: boolean;
  requestId?: string;
  simulated: boolean;
  provider: string;
  error?: string;
}

function buildHtml(subject: string, body: string, referenceNumber?: string): string {
  return `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
  body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
  .wrapper { max-width: 600px; margin: 20px auto; background: #fff; border-radius: 8px; overflow: hidden; }
  .header { background: #1F3864; color: #fff; padding: 24px 32px; }
  .header h1 { margin: 0; font-size: 18px; }
  .gold-bar { height: 4px; background: #BF8F00; }
  .body { padding: 32px; color: #333; line-height: 1.6; }
  .ref { background: #f0f4ff; border-left: 4px solid #1F3864; padding: 12px 16px; font-family: monospace; font-size: 16px; font-weight: bold; margin: 16px 0; }
  .footer { padding: 16px 32px; background: #f9f9f9; font-size: 11px; color: #999; border-top: 1px solid #eee; }
</style></head>
<body>
<div class="wrapper">
  <div class="header">
    <h1>🇺🇬 Mbarara District Local Government</h1>
    <p style="margin:4px 0 0;font-size:13px;opacity:0.8;">NileGov Stack — Government Service Notification</p>
  </div>
  <div class="gold-bar"></div>
  <div class="body">
    <p>${body.replace(/\n/g, '<br>')}</p>
    ${referenceNumber ? `<div class="ref">Reference: ${referenceNumber}</div>` : ''}
    <p style="color:#666;font-size:13px;margin-top:24px;">Track your application at <strong>nilegov.mbarara.go.ug</strong> or call Mbarara District Agricultural Office.</p>
  </div>
  <div class="footer">
    This is an automated notification from NileGov Stack. Data Protection &amp; Privacy Act 2019 compliant.
    <br>⚠ Prototype — not a live government system.
  </div>
</div>
</body></html>`;
}

export async function sendEmail(
  to: string,
  subject: string,
  textBody: string,
  referenceNumber?: string,
): Promise<EmailResult> {
  const apiKey   = process.env.ZEPTO_API_KEY;
  const fromEmail = process.env.ZEPTO_FROM_EMAIL || 'noreply@mbarara.go.ug';
  const fromName  = process.env.ZEPTO_FROM_NAME  || 'NileGov Stack';

  if (!apiKey) {
    console.log(`[EMAIL SIMULATED] → ${to} | ${subject}`);
    return { success: true, simulated: true, provider: 'ZeptoMail (SIMULATED)', requestId: `SIM-MAIL-${Date.now()}` };
  }

  try {
    const res = await fetch('https://api.zeptomail.com/v1.1/email', {
      method: 'POST',
      headers: {
        Authorization: `Zoho-enczapikey ${apiKey}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        from: { address: fromEmail, name: fromName },
        to: [{ email_address: { address: to, name: to } }],
        subject,
        htmlbody: buildHtml(subject, textBody, referenceNumber),
        textbody: textBody,
      }),
    });

    const data = await res.json() as any;
    if (res.ok && data.request_id) {
      console.log(`[EMAIL SENT] → ${to} | requestId: ${data.request_id}`);
      return { success: true, simulated: false, provider: 'ZeptoMail', requestId: data.request_id };
    }
    console.error(`[EMAIL FAILED] → ${to} | ${data.message}`);
    return { success: false, simulated: false, provider: 'ZeptoMail', error: data.message || `HTTP ${res.status}` };
  } catch (err: any) {
    console.error(`[EMAIL ERROR] ${err.message}`);
    return { success: false, simulated: false, provider: 'ZeptoMail', error: err.message };
  }
}
