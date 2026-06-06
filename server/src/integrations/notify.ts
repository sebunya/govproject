// Central notification dispatcher — SMS + Email + WhatsApp in parallel
// Falls back gracefully to simulation when no API keys are configured.

import { sendSms } from './sms.js';
import { sendEmail } from './email.js';
import { sendWhatsApp } from './whatsapp.js';

export interface CitizenContact {
  phoneNumber?: string | null;
  email?: string | null;
  fullName?: string;
}

export interface NotifyPayload {
  referenceNumber: string;
  subject: string;
  message: string;   // plain-text body used for SMS and WhatsApp
}

export interface ChannelResult {
  sent: boolean;
  simulated: boolean;
  provider: string;
  messageId?: string;
  error?: string;
}

export interface NotifyResult {
  sms: ChannelResult;
  email: ChannelResult;
  whatsapp: ChannelResult;
}

const SKIP: ChannelResult = { sent: false, simulated: true, provider: 'skipped — no contact info' };

export async function notifyCitizen(
  contact: CitizenContact,
  payload: NotifyPayload,
): Promise<NotifyResult> {
  const { phoneNumber, email } = contact;
  const { referenceNumber, subject, message } = payload;

  const [smsRes, emailRes, waRes] = await Promise.allSettled([
    phoneNumber
      ? sendSms(phoneNumber, `NileGov: ${message}`)
      : Promise.resolve(null),
    email
      ? sendEmail(email, subject, message, referenceNumber)
      : Promise.resolve(null),
    phoneNumber
      ? sendWhatsApp(phoneNumber, message)
      : Promise.resolve(null),
  ]);

  function toResult(settled: PromiseSettledResult<any>, skip: ChannelResult): ChannelResult {
    if (settled.status === 'rejected') return { sent: false, simulated: false, provider: 'unknown', error: String(settled.reason) };
    if (settled.value === null) return skip;
    const v = settled.value;
    return { sent: v.success, simulated: v.simulated, provider: v.provider, messageId: v.messageId, error: v.error };
  }

  return {
    sms:      toResult(smsRes,   SKIP),
    email:    toResult(emailRes, SKIP),
    whatsapp: toResult(waRes,    SKIP),
  };
}

export function integrationStatus() {
  return {
    sms:      { configured: !!process.env.AT_API_KEY,               provider: 'Africa\'s Talking' },
    email:    { configured: !!process.env.ZEPTO_API_KEY,             provider: 'ZeptoMail' },
    whatsapp: { configured: !!(process.env.META_WHATSAPP_TOKEN && process.env.META_PHONE_NUMBER_ID), provider: 'Meta WhatsApp Business API' },
    pesapal:  { configured: !!(process.env.PESAPAL_CONSUMER_KEY && process.env.PESAPAL_CONSUMER_SECRET), provider: 'Pesapal API 3.0', sandbox: process.env.PESAPAL_SANDBOX !== 'false' },
  };
}
