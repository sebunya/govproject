import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';
import { v4 as uuidv4 } from 'uuid';
import { db, initSchema, uploadsDir } from './db.js';
import { notifyCitizen, integrationStatus } from './integrations/notify.js';
import { submitPesapalOrder, getPesapalTransactionStatus, isPesapalConfigured } from './integrations/pesapal.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
initSchema();

const app = express();
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(uploadsDir));

const storage = multer.diskStorage({
  destination: uploadsDir,
  filename: (_req, file, cb) => { cb(null, `${uuidv4()}${path.extname(file.originalname)}`); },
});
const upload = multer({ storage, limits: { fileSize: 5 * 1024 * 1024 } });

// ─── SIMULATED INTEGRATIONS ────────────────────────────────────────────────

app.post('/api/simulate/nira', (_req, res) => {
  res.json({
    fullName: 'Akello Sarah Namugenyi', dateOfBirth: '1991-04-12',
    district: 'Mbarara', gender: 'Female', verified: true, _simulated: true,
    correlationId: `NIRA-${uuidv4().slice(0, 8).toUpperCase()}`,
    timestamp: new Date().toISOString(),
    source: 'NIRA Identity API (UGHub Pattern — SIMULATED)',
  });
});

app.post('/api/simulate/ura', (_req, res) => {
  res.json({
    taxStatus: 'Compliant', clearanceValidUntil: '2026-12-31', _simulated: true,
    correlationId: `URA-${uuidv4().slice(0, 8).toUpperCase()}`,
    timestamp: new Date().toISOString(),
    source: 'URA Tax Clearance API (UGHub Pattern — SIMULATED)',
  });
});

// Pesapal sandbox simulation
app.post('/api/simulate/pesapal', (req, res) => {
  const { amount, currency, reference, method } = req.body;
  const orderId = `PES-${uuidv4().slice(0, 8).toUpperCase()}`;
  res.json({
    orderId,
    transactionRef: `SIM-PAY-${reference}-${Date.now()}`,
    status: 'COMPLETED',
    amount, currency,
    method: method || 'mobile_money_mtn',
    _simulated: true,
    disclaimer: 'Prototype simulation only. No live payment was processed.',
    source: 'Pesapal API 3.0 Sandbox (SIMULATED)',
    timestamp: new Date().toISOString(),
  });
});

app.post('/api/simulate/erp-sync', (req, res) => {
  const { target = 'erpnext', applicationId, referenceNumber, serviceCode, permitNumber, feeAmount, feeCurrency, receiptRef, tin, fullName, district } = req.body;
  const correlationId = `ERP-${Date.now()}-${Math.random().toString(36).slice(2, 7).toUpperCase()}`;
  const idempotencyKey = `IDEM-${referenceNumber || 'REF'}-${Date.now()}`;

  const targets: Record<string, object> = {
    erpnext: {
      target: 'ERPNext / Frappe ERP',
      action: 'create_journal_entry',
      payload: {
        doctype: 'Journal Entry',
        voucher_type: 'Journal Entry',
        posting_date: new Date().toISOString().split('T')[0],
        company: 'Mbarara District Local Government',
        accounts: [
          { account: '1110 - Cash and Bank', debit_in_account_currency: feeAmount || 0 },
          { account: '4110 - Non-Tax Revenue — Licences', credit_in_account_currency: feeAmount || 0 },
        ],
        user_remark: `Permit fee for ${referenceNumber || 'N/A'} — ${serviceCode || 'service'} — ${fullName || 'applicant'}`,
        custom_permit_number: permitNumber || `MDLG-PERM-${referenceNumber}`,
        custom_reference_number: referenceNumber,
        custom_tin: tin,
        custom_pesapal_receipt: receiptRef,
        currency: feeCurrency || 'UGX',
      },
    },
    ifmis: {
      target: 'IFMIS (Integrated Financial Management Information System)',
      action: 'record_ntr',
      payload: {
        transaction_type: 'NTR',
        revenue_head: '1421300 — Licences and Permits',
        amount: feeAmount || 0,
        currency: feeCurrency || 'UGX',
        payer_name: fullName,
        payer_tin: tin,
        district_code: 'MBR',
        district_name: district || 'Mbarara',
        reference: referenceNumber,
        pesapal_receipt: receiptRef,
        consolidated_fund_ref: `CFR-${Date.now()}-${Math.random().toString(36).slice(2, 6).toUpperCase()}`,
        posting_date: new Date().toISOString(),
      },
    },
    opm: {
      target: 'OPM Performance Scorecard',
      action: 'push_kpi_event',
      payload: {
        district: district || 'Mbarara',
        service: serviceCode,
        permit_issued: true,
        permit_number: permitNumber,
        reference: referenceNumber,
        date: new Date().toISOString().split('T')[0],
        kpi_tags: ['service_delivery', 'permit_issued', 'sla_met'],
      },
    },
  };

  const targetPayload = targets[target] || targets.erpnext;

  res.json({
    schemaVersion: '1.0',
    correlationId,
    idempotencyKey,
    timestamp: new Date().toISOString(),
    source: 'NileGov Stack / Mbarara District Local Government',
    destination: (targetPayload as any).target,
    action: (targetPayload as any).action,
    status: 'SIMULATED_SUCCESS',
    syncedAt: new Date().toISOString(),
    applicationId,
    referenceNumber,
    ...(targetPayload as any),
    _simulated: true,
    disclaimer: 'Prototype simulation only. No live ERP, IFMIS, or OPM system was contacted. Production integration requires NITA-U UGHub routing, signed DSA, and district API credentials.',
  });
});

// ─── SERVICE CATALOGUE ─────────────────────────────────────────────────────

app.get('/api/services', (_req, res) => {
  const services = db.prepare(`SELECT * FROM services ORDER BY active DESC, id ASC`).all();
  res.json(services);
});

// ─── OFFICERS ─────────────────────────────────────────────────────────────

app.get('/api/officers', (_req, res) => {
  res.json(db.prepare(`SELECT id, name, role, district FROM officers ORDER BY id`).all());
});

// ─── APPLICATIONS ──────────────────────────────────────────────────────────

app.post('/api/applications', upload.fields([
  { name: 'bylaws', maxCount: 1 },
  { name: 'memberRoster', maxCount: 1 },
  { name: 'bizReg', maxCount: 1 },
  { name: 'premisesProof', maxCount: 1 },
  { name: 'taxClearance', maxCount: 1 },
]), (req, res) => {
  const body = req.body;
  const files = req.files as Record<string, Express.Multer.File[]>;
  const year = new Date().getFullYear();
  const count = (db.prepare('SELECT COUNT(*) as c FROM applications').get() as { c: number }).c;
  const refNum = `NGS-${year}-${String(count + 1).padStart(4, '0')}`;
  const now = new Date().toISOString();

  const svc = db.prepare(`SELECT slaResponseHours, slaResolveHours, name FROM services WHERE code = ?`)
    .get(body.serviceCode || 'cooperative-permit') as { slaResponseHours: number; slaResolveHours: number; name: string } | undefined;

  const result = db.prepare(`
    INSERT INTO applications (
      referenceNumber, serviceCode, serviceType,
      nin, fullName, dateOfBirth, district, gender, phoneNumber, email,
      cooperativeName, businessName,
      proposedTin, taxStatus, taxClearanceValidUntil,
      consentTimestamp, status, escalationState,
      slaResponseHours, slaResolveHours, submittedAt
    ) VALUES (
      ?, ?, ?,
      ?, ?, ?, ?, ?, ?, ?,
      ?, ?,
      ?, ?, ?,
      ?, 'submitted', 'not_escalated',
      ?, ?, ?
    )
  `).run(
    refNum, body.serviceCode || 'cooperative-permit', svc?.name || body.serviceType || 'Government Service',
    body.nin, body.fullName, body.dateOfBirth, body.district, body.gender,
    body.phoneNumber || null, body.email || null,
    body.cooperativeName || null, body.businessName || null,
    body.proposedTin, body.taxStatus, body.taxClearanceValidUntil,
    now, svc?.slaResponseHours || 48, svc?.slaResolveHours || 336, now,
  );

  const appId = result.lastInsertRowid as number;

  const insertDoc = db.prepare(`
    INSERT INTO documents (applicationId, originalName, storedName, fileType, uploadedAt)
    VALUES (?, ?, ?, ?, ?)
  `);
  for (const [, fileArr] of Object.entries(files || {})) {
    if (fileArr?.[0]) insertDoc.run(appId, fileArr[0].originalname, fileArr[0].filename, fileArr[0].mimetype, now);
  }

  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, 'Application submitted via citizen portal', 'citizen', ?, null, ?)
  `).run(appId, body.fullName, now);

  const submitMsg = `Application ${refNum} received. We will notify you when an officer begins review. Track at: nilegov.mbarara.go.ug/track`;

  // Portal log always inserted immediately
  db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, createdAt)
    VALUES (?, 'citizen', 'portal', ?, ?, 'simulated_sent', ?)
  `).run(appId, body.fullName, `Application ${refNum} received. Track status at the NileGov portal.`, now);

  // Fire real SMS + Email + WhatsApp asynchronously (don't block response)
  notifyCitizen(
    { phoneNumber: body.phoneNumber, email: body.email, fullName: body.fullName },
    { referenceNumber: refNum, subject: `NileGov — Application ${refNum} Received`, message: submitMsg },
  ).then(results => {
    const insertN = db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, disclaimer, createdAt) VALUES (?, 'citizen', ?, ?, ?, ?, ?, ?)`);
    const note = (r: any) => r.simulated ? 'simulated_sent' : r.sent ? 'sent' : 'failed';
    const disc = (r: any) => r.simulated ? 'Prototype simulation — no live message sent' : r.sent ? `Sent via ${r.provider}` : `Failed: ${r.error}`;
    if (body.phoneNumber) {
      insertN.run(appId, 'sms', body.phoneNumber, submitMsg, note(results.sms), disc(results.sms), now);
      insertN.run(appId, 'whatsapp', body.phoneNumber, submitMsg, note(results.whatsapp), disc(results.whatsapp), now);
    }
    if (body.email) insertN.run(appId, 'email', body.email, submitMsg, note(results.email), disc(results.email), now);
  }).catch(console.error);

  res.json({ referenceNumber: refNum, id: appId });
});

app.get('/api/applications', (req, res) => {
  const { persona, nin } = req.query;
  let rows: unknown[];

  if (persona === 'citizen') {
    if (!nin || typeof nin !== 'string' || nin.trim().length < 5) return res.json([]);
    rows = db.prepare(`
      SELECT a.* FROM applications a WHERE a.nin = ? ORDER BY a.submittedAt DESC
    `).all(nin.trim());
  } else if (persona === 'officer') {
    rows = db.prepare(`
      SELECT a.* FROM applications a
      WHERE a.status IN ('submitted','under_review','more_info_requested')
      ORDER BY a.escalationState DESC, (julianday(a.submittedAt) + a.slaResponseHours / 24.0) ASC
    `).all();
  } else if (persona === 'supervisor') {
    rows = db.prepare(`
      SELECT a.* FROM applications a
      WHERE a.status IN ('pending_countersign') OR a.escalationState = 'escalated'
      GROUP BY a.id ORDER BY a.escalationState DESC, a.submittedAt ASC
    `).all();
  } else {
    rows = db.prepare(`SELECT * FROM applications ORDER BY submittedAt DESC LIMIT 100`).all();
  }

  res.json(rows);
});

app.get('/api/applications/:id', (req, res) => {
  const row = db.prepare(`SELECT * FROM applications WHERE id = ? OR referenceNumber = ?`)
    .get(req.params.id, req.params.id) as Record<string, unknown> | undefined;
  if (!row) return res.status(404).json({ error: 'Not found' });

  const id = row.id as number;
  const docs = db.prepare(`SELECT * FROM documents WHERE applicationId = ? ORDER BY uploadedAt ASC`).all(id);
  const auditLog = db.prepare(`SELECT * FROM audit_log WHERE applicationId = ? ORDER BY createdAt ASC`).all(id);
  const svc = db.prepare(`SELECT feeAmount, feeCurrency FROM services WHERE code = ?`).get(row.serviceCode as string) as { feeAmount: number; feeCurrency: string } | undefined;
  const payment = db.prepare(`SELECT status FROM payments WHERE applicationId = ? ORDER BY createdAt DESC LIMIT 1`).get(id) as { status: string } | undefined;

  res.json({ ...row, documents: docs, auditLog, feeAmount: svc?.feeAmount ?? 0, feeCurrency: svc?.feeCurrency ?? 'UGX', paymentStatus: payment?.status ?? null });
});

// ─── MODULE: NOTIFICATIONS ─────────────────────────────────────────────────

app.get('/api/applications/:id/notifications', (req, res) => {
  const notifications = db.prepare(`
    SELECT * FROM notifications WHERE applicationId = ? ORDER BY createdAt ASC
  `).all(req.params.id);
  res.json(notifications);
});

// ─── MODULE: PAYMENTS ──────────────────────────────────────────────────────

app.get('/api/applications/:id/payments', (req, res) => {
  const payments = db.prepare(`SELECT * FROM payments WHERE applicationId = ? ORDER BY createdAt ASC`).all(req.params.id);
  res.json(payments);
});

app.post('/api/applications/:id/initiate-payment', async (req, res) => {
  const { purpose, amount, currency, method, mobileNumber } = req.body;
  const now = new Date().toISOString();

  const existing = db.prepare(`SELECT id FROM payments WHERE applicationId = ? AND status NOT IN ('failed')`).get(req.params.id);
  if (existing) return res.status(409).json({ error: 'Payment already initiated for this application.' });

  const appRow = db.prepare(`SELECT referenceNumber, fullName, phoneNumber, email FROM applications WHERE id = ?`).get(req.params.id) as any;

  const result = db.prepare(`
    INSERT INTO payments (applicationId, purpose, amount, currency, method, mobileNumber, status, createdAt)
    VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
  `).run(req.params.id, purpose, amount, currency || 'UGX', method, mobileNumber || null, now);

  const paymentId = result.lastInsertRowid as number;

  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, 'Payment initiated', 'citizen', 'Citizen', ?, ?)
  `).run(req.params.id, `${purpose} — UGX ${Number(amount).toLocaleString()} via ${method}`, now);

  // If Pesapal is configured, submit real order
  if (isPesapalConfigured() && appRow) {
    const appUrl = process.env.APP_URL || 'http://localhost:3001';
    const callbackUrl = `${appUrl}/api/pesapal/callback?applicationId=${req.params.id}&paymentId=${paymentId}`;
    submitPesapalOrder({
      reference: `${appRow.referenceNumber}-${paymentId}`,
      amount: Number(amount),
      currency: currency || 'UGX',
      description: purpose,
      callbackUrl,
      phoneNumber: mobileNumber || appRow.phoneNumber,
      email: appRow.email,
      firstName: appRow.fullName?.split(' ')[0],
      lastName: appRow.fullName?.split(' ').slice(1).join(' '),
    }).then(order => {
      if (order.trackingId) {
        db.prepare(`UPDATE payments SET transactionRef = ? WHERE id = ?`).run(order.trackingId, paymentId);
      }
    }).catch(console.error);
  }

  res.json({ id: paymentId, status: 'pending' });
});

app.post('/api/applications/:id/simulate-payment', async (req, res) => {
  const { paymentId } = req.body;
  const now = new Date().toISOString();
  const appRow = db.prepare(`SELECT referenceNumber, fullName, phoneNumber, email FROM applications WHERE id = ?`).get(req.params.id) as any;
  const payRow = db.prepare(`SELECT transactionRef FROM payments WHERE id = ?`).get(paymentId) as any;

  let txRef: string;
  let rcptRef: string;

  // If Pesapal configured and we have a real tracking ID, fetch real status
  if (isPesapalConfigured() && payRow?.transactionRef && !payRow.transactionRef.startsWith('SIM-')) {
    const status = await getPesapalTransactionStatus(payRow.transactionRef);
    txRef = payRow.transactionRef;
    rcptRef = status.confirmationCode || `PESA-${payRow.transactionRef}`;
  } else {
    txRef = `SIM-PAY-${req.params.id}-${Date.now()}`;
    rcptRef = `SIM-RECEIPT-${req.params.id}-${uuidv4().slice(0, 6).toUpperCase()}`;
  }

  db.prepare(`
    UPDATE payments SET status = 'verified', transactionRef = ?, receiptRef = ?,
      simulatedAt = ?, verifiedAt = ?
    WHERE id = ? AND applicationId = ?
  `).run(txRef, rcptRef, now, now, paymentId, req.params.id);

  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, ?, 'system', 'NileGov Stack (Pesapal ${isPesapalConfigured() ? 'Live' : 'Sandbox'})', ?, ?)
  `).run(req.params.id, `Payment verified — ${isPesapalConfigured() ? 'real' : 'simulated'}`, `Transaction: ${txRef} | Receipt: ${rcptRef}`, now);

  const payMsg = `Payment confirmed. Receipt: ${rcptRef}. ${isPesapalConfigured() ? 'Processed via Pesapal.' : 'Prototype simulation — no live payment processed.'}`;

  db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, disclaimer, createdAt)
    VALUES (?, 'citizen', 'portal', ?, ?, 'simulated_sent', 'Portal notification', ?)
  `).run(req.params.id, appRow?.fullName || 'Citizen', payMsg, now);

  if (appRow) {
    notifyCitizen(
      { phoneNumber: appRow.phoneNumber, email: appRow.email, fullName: appRow.fullName },
      { referenceNumber: appRow.referenceNumber, subject: `NileGov — Payment Confirmed: ${appRow.referenceNumber}`, message: payMsg },
    ).then(r => {
      const insertN = db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, disclaimer, createdAt) VALUES (?, 'citizen', ?, ?, ?, ?, ?, ?)`);
      const note = (x: any) => x.simulated ? 'simulated_sent' : x.sent ? 'sent' : 'failed';
      const disc = (x: any) => x.simulated ? 'Prototype simulation' : x.sent ? `Sent via ${x.provider}` : `Failed: ${x.error}`;
      if (appRow.phoneNumber) {
        insertN.run(req.params.id, 'sms', appRow.phoneNumber, payMsg, note(r.sms), disc(r.sms), now);
        insertN.run(req.params.id, 'whatsapp', appRow.phoneNumber, payMsg, note(r.whatsapp), disc(r.whatsapp), now);
      }
      if (appRow.email) insertN.run(req.params.id, 'email', appRow.email, payMsg, note(r.email), disc(r.email), now);
    }).catch(console.error);
  }

  const payment = db.prepare(`SELECT * FROM payments WHERE id = ?`).get(paymentId);
  res.json(payment);
});

// Pesapal IPN callback (GET) — called by Pesapal after payment
app.get('/api/pesapal/ipn', (req, res) => {
  const { OrderTrackingId, OrderMerchantReference, OrderNotificationType } = req.query;
  console.log(`[PESAPAL IPN] TrackingId: ${OrderTrackingId} | Ref: ${OrderMerchantReference} | Type: ${OrderNotificationType}`);
  // In production: verify status with getPesapalTransactionStatus and update DB
  res.json({ orderNotificationType: OrderNotificationType, orderTrackingId: OrderTrackingId, orderMerchantReference: OrderMerchantReference, status: '200' });
});

// Pesapal callback after redirect (GET) — citizen returns from Pesapal hosted page
app.get('/api/pesapal/callback', async (req, res) => {
  const { OrderTrackingId, applicationId, paymentId } = req.query;
  if (OrderTrackingId && paymentId) {
    const status = await getPesapalTransactionStatus(String(OrderTrackingId));
    if (status.status === 'COMPLETED') {
      const now = new Date().toISOString();
      const rcptRef = status.confirmationCode || String(OrderTrackingId);
      db.prepare(`UPDATE payments SET status = 'verified', receiptRef = ?, verifiedAt = ? WHERE id = ?`).run(rcptRef, now, paymentId);
    }
  }
  res.redirect(`/portal/application/${applicationId}?persona=citizen`);
});

// ─── MODULE: DOCUMENT VERIFICATION ────────────────────────────────────────

app.patch('/api/documents/:docId/verify', (req, res) => {
  const { status, notes, verifiedBy } = req.body;
  const now = new Date().toISOString();

  db.prepare(`
    UPDATE documents SET verificationStatus = ?, verificationNotes = ?, verifiedBy = ?, verifiedAt = ?
    WHERE id = ?
  `).run(status, notes || null, verifiedBy || 'Officer', now, req.params.docId);

  const doc = db.prepare(`SELECT * FROM documents WHERE id = ?`).get(req.params.docId) as Record<string, unknown>;

  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, ?, 'officer', ?, ?, ?)
  `).run(doc.applicationId, `Document ${status}: ${doc.originalName}`, verifiedBy || 'Officer', notes || '', now);

  res.json(doc);
});

// ─── MODULE: SLA ESCALATION ────────────────────────────────────────────────

app.patch('/api/applications/:id/escalate', (req, res) => {
  const { reason } = req.body;
  const now = new Date().toISOString();

  db.prepare(`UPDATE applications SET escalationState = 'escalated' WHERE id = ?`).run(req.params.id);

  const row = db.prepare(`SELECT fullName, referenceNumber, phoneNumber, email FROM applications WHERE id = ?`)
    .get(req.params.id) as { fullName: string; referenceNumber: string; phoneNumber: string; email: string };

  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, 'Application escalated to supervisor — SLA breach', 'officer', 'Tumusiime Robert', ?, ?)
  `).run(req.params.id, reason || 'SLA deadline exceeded. Escalated for supervisor intervention.', now);

  db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, createdAt)
    VALUES (?, 'supervisor', 'internal', 'Nakamya Grace', ?, 'simulated_sent', ?)
  `).run(req.params.id,
    `ESCALATION: Application ${row.referenceNumber} has exceeded SLA. Requires immediate supervisor review.`, now);

  notifyCitizen(
    { phone: row.phoneNumber, email: row.email, name: row.fullName },
    { type: 'escalation', referenceNumber: row.referenceNumber,
      message: `Your application ${row.referenceNumber} has been escalated to a supervisor due to SLA delays. We apologise for the wait and are prioritising your case.` }
  ).catch(() => {});

  const updated = db.prepare(`SELECT * FROM applications WHERE id = ?`).get(req.params.id);
  res.json(updated);
});

// ─── MODULE: OFFICER REASSIGNMENT ─────────────────────────────────────────

app.patch('/api/applications/:id/reassign', (req, res) => {
  const { officerId } = req.body;
  const now = new Date().toISOString();

  const officer = db.prepare(`SELECT id, name FROM officers WHERE id = ?`).get(officerId) as { id: number; name: string } | undefined;
  if (!officer) return res.status(404).json({ error: 'Officer not found' });

  db.prepare(`UPDATE applications SET assignedOfficerId = ?, assignedOfficerName = ? WHERE id = ?`)
    .run(officer.id, officer.name, req.params.id);

  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, ?, 'supervisor', 'Nakamya Grace', ?, ?)
  `).run(req.params.id, `Application reassigned to ${officer.name}`, `Workload rebalancing — reassigned to ${officer.name}`, now);

  const appRow = db.prepare(`SELECT fullName, referenceNumber, phoneNumber, email FROM applications WHERE id = ?`).get(req.params.id) as any;
  if (appRow) {
    notifyCitizen(
      { phone: appRow.phoneNumber, email: appRow.email, name: appRow.fullName },
      { type: 'reassignment', referenceNumber: appRow.referenceNumber,
        message: `Your application ${appRow.referenceNumber} has been reassigned to a different officer. It remains active in our system and will be processed promptly.` }
    ).catch(() => {});
  }

  res.json(db.prepare(`SELECT * FROM applications WHERE id = ?`).get(req.params.id));
});

// ─── OFFICER QUEUE + CLAIM ─────────────────────────────────────────────────

app.patch('/api/applications/:id/claim', (req, res) => {
  const now = new Date().toISOString();
  const row = db.prepare(`SELECT status, assignedOfficerId FROM applications WHERE id = ?`)
    .get(req.params.id) as { status: string; assignedOfficerId: number | null } | undefined;
  if (!row) return res.status(404).json({ error: 'Not found' });

  if (row.status === 'submitted') {
    db.prepare(`UPDATE applications SET status = 'under_review', assignedOfficerId = COALESCE(assignedOfficerId, 1),
      assignedOfficerName = COALESCE(assignedOfficerName, 'Tumusiime Robert'),
      respondedAt = COALESCE(respondedAt, ?) WHERE id = ?`).run(now, req.params.id);
    db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
      VALUES (?, 'Application claimed for review', 'officer', 'Tumusiime Robert', 'Opened in officer desk', ?)
    `).run(req.params.id, now);
  }
  const updated = db.prepare(`SELECT * FROM applications WHERE id = ?`).get(req.params.id) as Record<string,unknown>;
  const docs = db.prepare(`SELECT * FROM documents WHERE applicationId = ? ORDER BY uploadedAt`).all(req.params.id);
  const auditLog = db.prepare(`SELECT * FROM audit_log WHERE applicationId = ? ORDER BY createdAt`).all(req.params.id);
  const svc2 = db.prepare(`SELECT feeAmount, feeCurrency FROM services WHERE code = ?`).get(updated.serviceCode as string) as { feeAmount: number; feeCurrency: string } | undefined;
  const pay2 = db.prepare(`SELECT status FROM payments WHERE applicationId = ? ORDER BY createdAt DESC LIMIT 1`).get(req.params.id) as { status: string } | undefined;
  res.json({ ...updated, documents: docs, auditLog, feeAmount: svc2?.feeAmount ?? 0, feeCurrency: svc2?.feeCurrency ?? 'UGX', paymentStatus: pay2?.status ?? null });
});

app.patch('/api/applications/:id/officer-decision', (req, res) => {
  const { decision, notes } = req.body;
  const now = new Date().toISOString();

  const newStatus = decision === 'approved' ? 'pending_countersign'
    : decision === 'rejected' ? 'rejected' : 'more_info_requested';

  db.prepare(`UPDATE applications SET status = ?, officerDecision = ?, officerNotes = ?,
    respondedAt = COALESCE(respondedAt, ?), assignedOfficerId = COALESCE(assignedOfficerId, 1)
    WHERE id = ?`).run(newStatus, decision, notes, now, req.params.id);

  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, ?, 'officer', 'Tumusiime Robert', ?, ?)
  `).run(req.params.id, `Officer decision: ${decision}`, notes || '', now);

  const row = db.prepare(`SELECT fullName, referenceNumber, phoneNumber, email FROM applications WHERE id = ?`)
    .get(req.params.id) as { fullName: string; referenceNumber: string; phoneNumber?: string; email?: string };

  if (decision === 'approved') {
    db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, createdAt)
      VALUES (?, 'supervisor', 'internal', 'Nakamya Grace', ?, 'simulated_sent', ?)
    `).run(req.params.id, `Application ${row.referenceNumber} approved by officer — pending your countersignature.`, now);
  } else if (decision === 'more_info_requested') {
    const moreInfoMsg = `Action needed: Your application ${row.referenceNumber} requires additional information. Log in to the NileGov portal to respond.`;
    db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, createdAt)
      VALUES (?, 'citizen', 'sms', ?, ?, 'simulated_sent', ?)
    `).run(req.params.id, row.phoneNumber || row.fullName, moreInfoMsg, now);
    notifyCitizen(
      { phoneNumber: row.phoneNumber, email: row.email, fullName: row.fullName },
      { referenceNumber: row.referenceNumber, subject: `NileGov — Action Required: ${row.referenceNumber}`, message: moreInfoMsg },
    ).then(r => {
      const insertN = db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, disclaimer, createdAt) VALUES (?, 'citizen', ?, ?, ?, ?, ?, ?)`);
      const note = (x: any) => x.simulated ? 'simulated_sent' : x.sent ? 'sent' : 'failed';
      const disc = (x: any) => x.simulated ? 'Prototype simulation' : x.sent ? `Sent via ${x.provider}` : `Failed: ${x.error}`;
      if (row.phoneNumber) insertN.run(req.params.id, 'whatsapp', row.phoneNumber, moreInfoMsg, note(r.whatsapp), disc(r.whatsapp), now);
      if (row.email) insertN.run(req.params.id, 'email', row.email, moreInfoMsg, note(r.email), disc(r.email), now);
    }).catch(console.error);
  } else if (decision === 'rejected') {
    const rejMsg = `Your application ${row.referenceNumber} has been reviewed. The officer was unable to approve it at this time. Please visit the district office for guidance.`;
    notifyCitizen(
      { phoneNumber: row.phoneNumber, email: row.email, fullName: row.fullName },
      { referenceNumber: row.referenceNumber, subject: `NileGov — Application Update: ${row.referenceNumber}`, message: rejMsg },
    ).catch(console.error);
  }

  res.json(db.prepare('SELECT * FROM applications WHERE id = ?').get(req.params.id));
});

app.patch('/api/applications/:id/supervisor-decision', (req, res) => {
  const { decision, notes } = req.body;
  const now = new Date().toISOString();

  db.prepare(`UPDATE applications SET status = ?, supervisorDecision = ?, supervisorNotes = ?, resolvedAt = ?
    WHERE id = ?`).run(decision === 'approved' ? 'approved' : 'rejected', decision, notes, now, req.params.id);

  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, ?, 'supervisor', 'Nakamya Grace', ?, ?)
  `).run(req.params.id, `Supervisor decision: ${decision}`, notes || '', now);

  const row = db.prepare(`SELECT fullName, referenceNumber, phoneNumber, email FROM applications WHERE id = ?`)
    .get(req.params.id) as { fullName: string; referenceNumber: string; phoneNumber?: string; email?: string };

  const msg = decision === 'approved'
    ? `APPROVED: Your application ${row.referenceNumber} has been approved. Your permit has been granted by Mbarara District Local Government. Visit the NileGov portal to download your certificate.`
    : `Your application ${row.referenceNumber} could not be approved at this time. Please visit the district office for guidance or reapply.`;

  db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, createdAt)
    VALUES (?, 'citizen', 'portal', ?, ?, 'simulated_sent', ?)
  `).run(req.params.id, row.fullName, msg, now);

  // Fire real multi-channel notifications
  notifyCitizen(
    { phoneNumber: row.phoneNumber, email: row.email, fullName: row.fullName },
    { referenceNumber: row.referenceNumber, subject: decision === 'approved' ? `✅ NileGov — Permit Granted: ${row.referenceNumber}` : `NileGov — Application Update: ${row.referenceNumber}`, message: msg },
  ).then(r => {
    const insertN = db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, disclaimer, createdAt) VALUES (?, 'citizen', ?, ?, ?, ?, ?, ?)`);
    const note = (x: any) => x.simulated ? 'simulated_sent' : x.sent ? 'sent' : 'failed';
    const disc = (x: any) => x.simulated ? 'Prototype simulation' : x.sent ? `Sent via ${x.provider}` : `Failed: ${x.error}`;
    if (row.phoneNumber) {
      insertN.run(req.params.id, 'sms', row.phoneNumber, msg, note(r.sms), disc(r.sms), now);
      insertN.run(req.params.id, 'whatsapp', row.phoneNumber, msg, note(r.whatsapp), disc(r.whatsapp), now);
    }
    if (row.email) insertN.run(req.params.id, 'email', row.email, msg, note(r.email), disc(r.email), now);
  }).catch(console.error);

  res.json(db.prepare('SELECT * FROM applications WHERE id = ?').get(req.params.id));
});

app.patch('/api/applications/:id/rate', (req, res) => {
  const { rating, comment } = req.body;
  const now = new Date().toISOString();

  db.prepare(`UPDATE applications SET rating = ?, ratingComment = ?, ratedAt = ? WHERE id = ?`)
    .run(rating, comment || null, now, req.params.id);

  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, 'Service rated by citizen', 'citizen', 'Citizen', ?, ?)
  `).run(req.params.id, `${rating}/5 stars — ${comment || 'No comment'}`, now);

  res.json(db.prepare('SELECT * FROM applications WHERE id = ?').get(req.params.id));
});

app.patch('/api/applications/:id/citizen-response', upload.single('additionalDoc'), (req, res) => {
  const { message } = req.body;
  const now = new Date().toISOString();
  const file = req.file;

  const row = db.prepare(`SELECT status, fullName, phoneNumber, email, referenceNumber FROM applications WHERE id = ?`)
    .get(req.params.id) as { status: string; fullName: string; phoneNumber: string; email: string; referenceNumber: string } | undefined;
  if (!row) return res.status(404).json({ error: 'Not found' });
  if (row.status !== 'more_info_requested')
    return res.status(400).json({ error: 'Application is not awaiting additional information.' });

  db.prepare(`UPDATE applications SET status = 'submitted' WHERE id = ?`).run(req.params.id);

  if (file) {
    db.prepare(`INSERT INTO documents (applicationId, originalName, storedName, fileType, uploadedAt)
      VALUES (?, ?, ?, ?, ?)`).run(req.params.id, file.originalname, file.filename, file.mimetype, now);
  }

  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, 'Citizen provided additional information — resubmitted', 'citizen', ?, ?, ?)
  `).run(req.params.id, row.fullName, message || 'Additional documents provided', now);

  db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, createdAt)
    VALUES (?, 'citizen', 'portal', ?, 'Application resubmitted with additional information.', 'simulated_sent', ?)
  `).run(req.params.id, row.fullName, now);

  notifyCitizen(
    { phone: row.phoneNumber, email: row.email, name: row.fullName },
    { type: 'resubmission', referenceNumber: row.referenceNumber,
      message: `Your application ${row.referenceNumber} has been resubmitted with additional information and is back in the review queue.` }
  ).catch(() => {});

  const updated = db.prepare(`SELECT * FROM applications WHERE id = ?`).get(req.params.id);
  const docs = db.prepare(`SELECT * FROM documents WHERE applicationId = ? ORDER BY uploadedAt`).all(req.params.id);
  const auditLog = db.prepare(`SELECT * FROM audit_log WHERE applicationId = ? ORDER BY createdAt`).all(req.params.id);
  res.json({ ...(updated as object), documents: docs, auditLog });
});

// ─── DASHBOARD ─────────────────────────────────────────────────────────────

app.get('/api/dashboard', (_req, res) => {
  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];
  const weekAgo = new Date(today.getTime() - 7 * 86400000).toISOString();

  const todayProcessed = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE resolvedAt >= ? AND status IN ('approved','rejected')`).get(`${todayStr}T00:00:00.000Z`) as { c: number }).c;
  const weekProcessed = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE resolvedAt >= ? AND status IN ('approved','rejected')`).get(weekAgo) as { c: number }).c;
  const avgRes = (db.prepare(`SELECT AVG((julianday(resolvedAt) - julianday(submittedAt)) * 24) as avg FROM applications WHERE resolvedAt IS NOT NULL`).get() as { avg: number | null }).avg;
  const totalResolved = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE resolvedAt IS NOT NULL`).get() as { c: number }).c;
  const onTime = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE resolvedAt IS NOT NULL AND (julianday(resolvedAt) - julianday(submittedAt)) * 24 <= slaResolveHours`).get() as { c: number }).c;
  const slaCompliancePercent = totalResolved > 0 ? Math.round((onTime / totalResolved) * 100) : 100;
  const activeApplications = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE status NOT IN ('approved','rejected')`).get() as { c: number }).c;
  const escalatedCount = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE escalationState = 'escalated'`).get() as { c: number }).c;

  const bottlenecks = [
    { stage: 'Awaiting Officer Review', count: 0, avgWaitHours: 0 },
    { stage: 'Pending Countersignature', count: 0, avgWaitHours: 0 },
    { stage: 'More Information Requested', count: 0, avgWaitHours: 0 },
  ];
  (db.prepare(`SELECT status, COUNT(*) as c, AVG((julianday('now') - julianday(submittedAt)) * 24) as avgWait FROM applications WHERE status IN ('submitted','pending_countersign','more_info_requested') GROUP BY status`).all() as any[]).forEach(r => {
    if (r.status === 'submitted') { bottlenecks[0].count = r.c; bottlenecks[0].avgWaitHours = Math.round(r.avgWait); }
    else if (r.status === 'pending_countersign') { bottlenecks[1].count = r.c; bottlenecks[1].avgWaitHours = Math.round(r.avgWait); }
    else if (r.status === 'more_info_requested') { bottlenecks[2].count = r.c; bottlenecks[2].avgWaitHours = Math.round(r.avgWait); }
  });

  const districtStats = db.prepare(`
    SELECT district, COUNT(*) as total,
      SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) as approved,
      SUM(CASE WHEN resolvedAt IS NOT NULL AND (julianday(resolvedAt)-julianday(submittedAt))*24>slaResolveHours THEN 1 ELSE 0 END) as slaBreached
    FROM applications GROUP BY district ORDER BY total DESC
  `).all();

  const weekLabels = ['4 wks ago', '3 wks ago', '2 wks ago', 'Last week', 'This week'];
  const weeklyTrend = Array.from({ length: 5 }, (_, idx) => {
    const w = 4 - idx;
    const wStart = new Date(today.getTime() - (w + 1) * 7 * 86400000).toISOString();
    const wEnd = new Date(today.getTime() - w * 7 * 86400000).toISOString();
    return {
      week: weekLabels[idx],
      submitted: (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE submittedAt >= ? AND submittedAt < ?`).get(wStart, wEnd) as { c: number }).c,
      resolved: (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE resolvedAt >= ? AND resolvedAt < ?`).get(wStart, wEnd) as { c: number }).c,
      slaBreached: (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE resolvedAt >= ? AND resolvedAt < ? AND (julianday(resolvedAt)-julianday(submittedAt))*24>slaResolveHours`).get(wStart, wEnd) as { c: number }).c,
    };
  });

  const categoryStats = (db.prepare(`
    SELECT serviceCode, serviceType as category,
      COUNT(*) as total,
      SUM(CASE WHEN resolvedAt IS NOT NULL AND (julianday(resolvedAt)-julianday(submittedAt))*24>slaResolveHours THEN 1 ELSE 0 END) as slaBreached,
      ROUND(AVG(CASE WHEN resolvedAt IS NOT NULL THEN (julianday(resolvedAt)-julianday(submittedAt))*24 END)) as avgResolutionHours
    FROM applications GROUP BY serviceCode ORDER BY total DESC
  `).all() as any[]);

  const notifStats = db.prepare(`SELECT status, COUNT(*) as c FROM notifications GROUP BY status`).all() as { status: string; c: number }[];
  const notifTotal = notifStats.reduce((s, r) => s + r.c, 0);

  const payStats = db.prepare(`SELECT status, SUM(amount) as total, COUNT(*) as count FROM payments GROUP BY status`).all() as any[];
  const payVerified = payStats.find(r => r.status === 'verified');

  const avgRating = (db.prepare(`SELECT AVG(rating) as avg FROM applications WHERE rating IS NOT NULL`).get() as { avg: number | null }).avg;

  res.json({
    todayProcessed, weekProcessed,
    avgResolutionHours: Math.round(avgRes || 0),
    slaCompliancePercent, activeApplications, escalatedCount,
    bottlenecks, districtStats, weeklyTrend, categoryStats,
    notifTotal, notifStats,
    payVerifiedAmount: payVerified?.total || 0,
    payVerifiedCount: payVerified?.count || 0,
    avgCitizenRating: avgRating ? Math.round(avgRating * 10) / 10 : null,
  });
});

app.get('/api/dashboard/officers', (_req, res) => {
  const officers = db.prepare(`SELECT id, name, role, district FROM officers`).all() as { id: number; name: string; role: string; district: string }[];
  const result = officers.map(o => {
    const total = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE assignedOfficerId = ?`).get(o.id) as { c: number }).c;
    const resolved = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE assignedOfficerId = ? AND resolvedAt IS NOT NULL`).get(o.id) as { c: number }).c;
    const onTime = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE assignedOfficerId = ? AND resolvedAt IS NOT NULL AND (julianday(resolvedAt)-julianday(submittedAt))*24<=slaResolveHours`).get(o.id) as { c: number }).c;
    const active = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE assignedOfficerId = ? AND status NOT IN ('approved','rejected')`).get(o.id) as { c: number }).c;
    const avgRes = (db.prepare(`SELECT AVG((julianday(resolvedAt)-julianday(submittedAt))*24) as avg FROM applications WHERE assignedOfficerId = ? AND resolvedAt IS NOT NULL`).get(o.id) as { avg: number | null }).avg;
    return { id: o.id, name: o.name, role: o.role, district: o.district, total, resolved, active, onTime, slaBreached: resolved - onTime, slaCompliance: resolved > 0 ? Math.round((onTime / resolved) * 100) : 100, avgResolutionHours: Math.round(avgRes || 0) };
  });
  res.json(result);
});

app.get('/api/dashboard/district-trend', (_req, res) => {
  const now = new Date();
  const districts = ['Mbarara', 'Kampala', 'Gulu', 'Jinja'];
  const weekLabels = ['4 wks ago', '3 wks ago', '2 wks ago', 'Last week', 'This week'];
  const trend: Record<string, any[]> = {};
  for (const d of districts) {
    trend[d] = Array.from({ length: 5 }, (_, idx) => {
      const w = 4 - idx;
      const wS = new Date(now.getTime() - (w + 1) * 7 * 86400000).toISOString();
      const wE = new Date(now.getTime() - w * 7 * 86400000).toISOString();
      const total = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE district=? AND submittedAt>=? AND submittedAt<?`).get(d, wS, wE) as { c: number }).c;
      const breached = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE district=? AND resolvedAt>=? AND resolvedAt<? AND (julianday(resolvedAt)-julianday(submittedAt))*24>slaResolveHours`).get(d, wS, wE) as { c: number }).c;
      const onTimeCount = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE district=? AND resolvedAt>=? AND resolvedAt<? AND (julianday(resolvedAt)-julianday(submittedAt))*24<=slaResolveHours`).get(d, wS, wE) as { c: number }).c;
      return { week: weekLabels[idx], total, slaBreached: breached, onTime: onTimeCount, compliance: total > 0 ? Math.round(((total - breached) / total) * 100) : 100 };
    });
  }
  res.json({ districts, trend });
});

// ─── MODULE: M&E REPORTING SNAPSHOT ────────────────────────────────────────

app.get('/api/dashboard/reports', (_req, res) => {
  const now = new Date();
  const snapshotId = `SNAP-${now.toISOString().split('T')[0]}-001`;

  const total = (db.prepare(`SELECT COUNT(*) as c FROM applications`).get() as { c: number }).c;
  const byStatus = db.prepare(`SELECT status, COUNT(*) as c FROM applications GROUP BY status`).all() as { status: string; c: number }[];
  const byServiceRaw = db.prepare(`
    SELECT a.serviceCode, s.name as serviceName,
      COUNT(*) as total,
      SUM(CASE WHEN a.status='approved' THEN 1 ELSE 0 END) as approved,
      SUM(CASE WHEN a.status='rejected' THEN 1 ELSE 0 END) as rejected,
      SUM(CASE WHEN a.resolvedAt IS NULL THEN 1 ELSE 0 END) as active,
      ROUND(AVG(CASE WHEN a.resolvedAt IS NOT NULL THEN (julianday(a.resolvedAt)-julianday(a.submittedAt))*24 END), 0) as avgResolutionHours
    FROM applications a LEFT JOIN services s ON s.code = a.serviceCode
    GROUP BY a.serviceCode ORDER BY total DESC
  `).all() as any[];
  const byDistrict = db.prepare(`SELECT district, COUNT(*) as c FROM applications GROUP BY district ORDER BY c DESC`).all() as any[];
  const resolved = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE resolvedAt IS NOT NULL`).get() as { c: number }).c;
  const onTime = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE resolvedAt IS NOT NULL AND (julianday(resolvedAt)-julianday(submittedAt))*24<=slaResolveHours`).get() as { c: number }).c;
  const approvedCount = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE status='approved'`).get() as { c: number }).c;
  const escalated = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE escalationState='escalated'`).get() as { c: number }).c;
  const notifTotal = (db.prepare(`SELECT COUNT(*) as c FROM notifications`).get() as { c: number }).c;
  const notifSent = (db.prepare(`SELECT COUNT(*) as c FROM notifications WHERE status='simulated_sent'`).get() as { c: number }).c;
  const notifFailed = (db.prepare(`SELECT COUNT(*) as c FROM notifications WHERE status='simulated_failed'`).get() as { c: number }).c;
  const notifByChannel = db.prepare(`SELECT channel, COUNT(*) as c FROM notifications GROUP BY channel`).all() as { channel: string; c: number }[];
  const payVerified = (db.prepare(`SELECT COUNT(*) as c, COALESCE(SUM(amount),0) as total FROM payments WHERE status='verified'`).get() as { c: number; total: number });
  const payPending = (db.prepare(`SELECT COUNT(*) as c FROM payments WHERE status='pending'`).get() as { c: number }).c;
  const payByMethod = db.prepare(`SELECT method, COUNT(*) as c FROM payments WHERE status='verified' GROUP BY method`).all() as { method: string; c: number }[];
  const docsTotal = (db.prepare(`SELECT COUNT(*) as c FROM documents`).get() as { c: number }).c;
  const docsVerified = (db.prepare(`SELECT COUNT(*) as c FROM documents WHERE verificationStatus='verified'`).get() as { c: number }).c;
  const avgRating = (db.prepare(`SELECT ROUND(AVG(rating),1) as avg FROM applications WHERE rating IS NOT NULL`).get() as { avg: number | null }).avg;
  const officerWorkload = db.prepare(`
    SELECT o.id, o.name, o.role,
      COUNT(a.id) as total,
      SUM(CASE WHEN a.resolvedAt IS NULL AND a.assignedOfficerId IS NOT NULL THEN 1 ELSE 0 END) as active,
      SUM(CASE WHEN a.resolvedAt IS NOT NULL THEN 1 ELSE 0 END) as resolved,
      SUM(CASE WHEN a.status='approved' THEN 1 ELSE 0 END) as approved,
      ROUND(AVG(CASE WHEN a.resolvedAt IS NOT NULL THEN (julianday(a.resolvedAt)-julianday(a.submittedAt))*24 END),0) as avgResolutionHours,
      SUM(CASE WHEN a.resolvedAt IS NOT NULL AND (julianday(a.resolvedAt)-julianday(a.submittedAt))*24 <= a.slaResolveHours THEN 1 ELSE 0 END) as onTime,
      SUM(CASE WHEN a.resolvedAt IS NOT NULL AND (julianday(a.resolvedAt)-julianday(a.submittedAt))*24 > a.slaResolveHours THEN 1 ELSE 0 END) as slaBreached
    FROM officers o LEFT JOIN applications a ON a.assignedOfficerId=o.id
    GROUP BY o.id ORDER BY total DESC
  `).all().map((o: any) => ({
    ...o,
    slaCompliance: o.resolved > 0 ? Math.round((o.onTime / o.resolved) * 100) : 100,
  }));

  res.json({
    snapshotId,
    generatedAt: now.toISOString(),
    disclaimer: 'Prototype simulation only. These metrics reflect seeded demo data and do not represent official government statistics.',
    totals: {
      total,
      resolved,
      approved: approvedCount,
      approvalRate: resolved > 0 ? Math.round((approvedCount / resolved) * 100) : 0,
      slaCompliance: resolved > 0 ? Math.round((onTime / resolved) * 100) : 100,
      escalated,
      avgRating,
    },
    byStatus: Object.fromEntries(byStatus.map(r => [r.status, r.c])),
    byService: byServiceRaw,
    byDistrict,
    documents: { total: docsTotal, verified: docsVerified },
    notifications: {
      total: notifTotal,
      simulated_sent: notifSent,
      simulated_failed: notifFailed,
      byChannel: Object.fromEntries(notifByChannel.map(r => [r.channel, r.c])),
    },
    payments: {
      totalVerifiedAmount: payVerified.total,
      verifiedCount: payVerified.c,
      pendingCount: payPending,
      byMethod: Object.fromEntries(payByMethod.map(r => [r.method, r.c])),
    },
    officerWorkload,
  });
});

// ─── HEALTH CHECK ──────────────────────────────────────────────────────────

app.get('/api/health', (_req, res) => {
  const appCount    = (db.prepare('SELECT COUNT(*) as c FROM applications').get() as {c:number}).c;
  const notifCount  = (db.prepare('SELECT COUNT(*) as c FROM notifications').get() as {c:number}).c;
  const sentCount   = (db.prepare("SELECT COUNT(*) as c FROM notifications WHERE status='sent'").get() as {c:number}).c;
  const integrations = integrationStatus();
  res.json({
    status: 'ok',
    version: '1.0.0-demo',
    timestamp: new Date().toISOString(),
    database: 'connected',
    applicationCount: appCount,
    notificationCount: notifCount,
    notificationsSentLive: sentCount,
    integrations,
    disclaimer: 'Prototype only. Not a live production system.',
  });
});

// Admin: test a notification channel
app.post('/api/admin/test-notification', async (req, res) => {
  const { channel, to, message } = req.body;
  if (!to || !message) return res.status(400).json({ error: 'to and message are required' });

  const { sendSms: sms } = await import('./integrations/sms.js');
  const { sendEmail: email } = await import('./integrations/email.js');
  const { sendWhatsApp: wa } = await import('./integrations/whatsapp.js');

  let result;
  if (channel === 'sms')       result = await sms(to, message);
  else if (channel === 'email') result = await email(to, `NileGov Test — ${new Date().toISOString()}`, message);
  else if (channel === 'whatsapp') result = await wa(to, message);
  else return res.status(400).json({ error: 'channel must be sms, email, or whatsapp' });

  res.json({ channel, to, result });
});

// Public reference tracker (no NIN required)
app.get('/api/track/:ref', (req, res) => {
  const row = db.prepare(`SELECT referenceNumber, serviceType, status, submittedAt, respondedAt, resolvedAt, slaResponseHours, slaResolveHours, escalationState FROM applications WHERE referenceNumber = ?`).get(req.params.ref.toUpperCase()) as any;
  if (!row) return res.status(404).json({ error: 'Reference number not found.' });
  res.json(row);
});

// Application withdrawal (citizen)
app.patch('/api/applications/:id/withdraw', (req, res) => {
  const now = new Date().toISOString();
  const row = db.prepare('SELECT status, fullName, referenceNumber, phoneNumber, email FROM applications WHERE id = ?').get(req.params.id) as any;
  if (!row) return res.status(404).json({ error: 'Not found' });
  if (!['submitted'].includes(row.status)) return res.status(409).json({ error: 'Only submitted applications can be withdrawn.' });
  db.prepare(`UPDATE applications SET status = 'withdrawn', resolvedAt = ? WHERE id = ?`).run(now, req.params.id);
  db.prepare(`INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt) VALUES (?, 'Application withdrawn by citizen', 'citizen', ?, 'Citizen requested withdrawal before officer review.', ?)`).run(req.params.id, row.fullName, now);
  db.prepare(`INSERT INTO notifications (applicationId, type, channel, recipient, message, status, createdAt) VALUES (?, 'citizen', 'portal', ?, ?, 'simulated_sent', ?)`).run(req.params.id, row.fullName, `Your application ${row.referenceNumber} has been withdrawn as requested.`, now);
  notifyCitizen(
    { phone: row.phoneNumber, email: row.email, name: row.fullName },
    { type: 'withdrawal', referenceNumber: row.referenceNumber,
      message: `Your application ${row.referenceNumber} has been withdrawn as requested. You may submit a new application at any time.` }
  ).catch(() => {});
  res.json({ ok: true });
});

// ─── ERROR HANDLER ─────────────────────────────────────────────────────────

app.use((err: any, _req: any, res: any, next: any) => {
  if (err?.code === 'LIMIT_FILE_SIZE') return res.status(413).json({ error: 'File too large. Maximum 5MB.' });
  if (err?.code === 'LIMIT_UNEXPECTED_FILE') return res.status(400).json({ error: 'Unexpected file field.' });
  if (err) { console.error('API error:', err.message); return res.status(500).json({ error: 'Internal server error.' }); }
  next();
});

// Serve built React app in production
if (process.env.NODE_ENV === 'production') {
  const clientDist = path.resolve(__dirname, '../../client/dist');
  app.use(express.static(clientDist));
  app.get('*', (_req, res) => res.sendFile(path.join(clientDist, 'index.html')));
}

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`NileGov API running on http://localhost:${PORT}`));
