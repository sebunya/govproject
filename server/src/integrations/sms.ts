// Africa's Talking SMS — Uganda's primary carrier-grade SMS gateway
// Docs: https://developers.africastalking.com/docs/sms/sending
// Env: AT_API_KEY, AT_USERNAME (default: sandbox), AT_SENDER_ID (default: NILEGOV)

export interface SmsResult {
  success: boolean;
  messageId?: string;
  simulated: boolean;
  provider: string;
  error?: string;
}

export async function sendSms(to: string, message: string): Promise<SmsResult> {
  const apiKey  = process.env.AT_API_KEY;
  const username = process.env.AT_USERNAME || 'sandbox';
  const senderId = process.env.AT_SENDER_ID || 'NILEGOV';

  if (!apiKey) {
    console.log(`[SMS SIMULATED] → ${to} | ${message.slice(0, 60)}…`);
    return { success: true, simulated: true, provider: 'Africa\'s Talking (SIMULATED)', messageId: `SIM-SMS-${Date.now()}` };
  }

  try {
    const params = new URLSearchParams({ username, to, message, from: senderId });
    const res = await fetch('https://api.africastalking.com/version1/messaging', {
      method: 'POST',
      headers: {
        apiKey,
        'Content-Type': 'application/x-www-form-urlencoded',
        Accept: 'application/json',
      },
      body: params.toString(),
    });

    const data = await res.json() as any;
    const recipient = data?.SMSMessageData?.Recipients?.[0];

    if (recipient?.statusCode === 101) {
      console.log(`[SMS SENT] → ${to} | msgId: ${recipient.messageId}`);
      return { success: true, simulated: false, provider: 'Africa\'s Talking', messageId: recipient.messageId };
    }
    console.error(`[SMS FAILED] → ${to} | ${recipient?.status}`);
    return { success: false, simulated: false, provider: 'Africa\'s Talking', error: recipient?.status || 'Unknown error' };
  } catch (err: any) {
    console.error(`[SMS ERROR] ${err.message}`);
    return { success: false, simulated: false, provider: 'Africa\'s Talking', error: err.message };
  }
}
