import { DatabaseSync } from 'node:sqlite';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data');
const DB_PATH = path.join(DATA_DIR, 'nilegov.db');
const uploadsDir = path.join(DATA_DIR, 'uploads');

// Ensure dirs exist and wipe DB for clean schema
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });
for (const ext of ['', '-wal', '-shm']) {
  if (fs.existsSync(DB_PATH + ext)) fs.unlinkSync(DB_PATH + ext);
}

const db = new DatabaseSync(DB_PATH);

db.exec(`PRAGMA journal_mode = WAL; PRAGMA foreign_keys = ON;`);

// Create full schema inline (avoids stale cached module)
db.exec(`
  CREATE TABLE IF NOT EXISTS officers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, role TEXT NOT NULL, district TEXT NOT NULL
  );
  CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
    description TEXT NOT NULL, category TEXT NOT NULL, icon TEXT NOT NULL DEFAULT '📄',
    slaResponseHours INTEGER NOT NULL DEFAULT 48, slaResolveHours INTEGER NOT NULL DEFAULT 336,
    feeAmount INTEGER NOT NULL DEFAULT 0, feeCurrency TEXT NOT NULL DEFAULT 'UGX',
    requiredDocs TEXT NOT NULL DEFAULT 'Application Letter', active INTEGER NOT NULL DEFAULT 1,
    disclaimer TEXT NOT NULL DEFAULT 'Prototype service catalogue only.'
  );
  CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT, referenceNumber TEXT NOT NULL UNIQUE,
    serviceCode TEXT NOT NULL DEFAULT 'cooperative-permit',
    serviceType TEXT NOT NULL DEFAULT 'Cooperative Registration & Agribusiness Permit',
    nin TEXT NOT NULL, fullName TEXT NOT NULL, dateOfBirth TEXT NOT NULL,
    district TEXT NOT NULL, gender TEXT NOT NULL,
    phoneNumber TEXT, email TEXT,
    cooperativeName TEXT, businessName TEXT,
    proposedTin TEXT NOT NULL, taxStatus TEXT NOT NULL, taxClearanceValidUntil TEXT NOT NULL,
    consentTimestamp TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'submitted',
    escalationState TEXT NOT NULL DEFAULT 'not_escalated',
    slaResponseHours INTEGER NOT NULL DEFAULT 48, slaResolveHours INTEGER NOT NULL DEFAULT 336,
    submittedAt TEXT NOT NULL, respondedAt TEXT, resolvedAt TEXT,
    assignedOfficerId INTEGER REFERENCES officers(id), assignedOfficerName TEXT,
    officerNotes TEXT, officerDecision TEXT, supervisorNotes TEXT, supervisorDecision TEXT,
    rating INTEGER, ratingComment TEXT, ratedAt TEXT
  );
  CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT, applicationId INTEGER NOT NULL REFERENCES applications(id),
    originalName TEXT NOT NULL, storedName TEXT NOT NULL, fileType TEXT NOT NULL, uploadedAt TEXT NOT NULL,
    verificationStatus TEXT NOT NULL DEFAULT 'pending',
    verificationNotes TEXT, verifiedBy TEXT, verifiedAt TEXT
  );
  CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT, applicationId INTEGER REFERENCES applications(id),
    type TEXT NOT NULL, channel TEXT NOT NULL, recipient TEXT NOT NULL,
    message TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'simulated_sent',
    disclaimer TEXT NOT NULL DEFAULT 'Prototype simulation only. No live notification was sent.',
    createdAt TEXT NOT NULL DEFAULT (datetime('now'))
  );
  CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, applicationId INTEGER REFERENCES applications(id),
    purpose TEXT NOT NULL, amount INTEGER NOT NULL, currency TEXT NOT NULL DEFAULT 'UGX',
    method TEXT, mobileNumber TEXT, transactionRef TEXT, receiptRef TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    disclaimer TEXT NOT NULL DEFAULT 'Prototype simulation only. No live payment was processed.',
    simulatedAt TEXT, verifiedAt TEXT, createdAt TEXT NOT NULL DEFAULT (datetime('now'))
  );
  CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, applicationId INTEGER REFERENCES applications(id),
    action TEXT NOT NULL, actorPersona TEXT NOT NULL, actorName TEXT NOT NULL,
    notes TEXT, createdAt TEXT NOT NULL DEFAULT (datetime('now'))
  );
`);

// Tables freshly created above — no wipe needed

// ─── SERVICES ────────────────────────────────────────────────────────────────
const insertService = db.prepare(`
  INSERT INTO services (code, name, description, category, icon, slaResponseHours, slaResolveHours, feeAmount, feeCurrency, requiredDocs, active)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
`);

insertService.run(
  'cooperative-permit',
  'Cooperative Registration & Agribusiness Permit',
  'Register your farming cooperative and apply for an agribusiness operating permit with Mbarara District Local Government.',
  'Agriculture', '🌿', 48, 336, 0, 'UGX',
  'Cooperative Bylaws,Member Roster', 1
);
insertService.run(
  'trading-licence',
  'Trading Licence',
  'Apply for a trading licence to legally operate a business within the district. Required for all commercial premises.',
  'Business Licensing', '🏪', 24, 240, 120000, 'UGX',
  'Business Registration Certificate,Tax Clearance Certificate,Premises Ownership/Lease Proof', 1
);
insertService.run(
  'land-permit',
  'Land Development Permit',
  'Apply for permission to develop or subdivide land within the district.',
  'Land & Property', '🏗', 48, 720, 50000, 'UGX',
  'Land Title,Site Plan,Environmental Impact Assessment', 0
);
insertService.run(
  'birth-certificate',
  'Birth Certificate Application',
  'Apply for or replace a birth certificate through the district registration office.',
  'Civil Registration', '📄', 24, 168, 0, 'UGX',
  'Parent NIN,Hospital Birth Record', 0
);
insertService.run(
  'health-permit',
  'Food Handler Health Permit',
  'Health clearance certificate for food handlers and food establishments.',
  'Health & Safety', '🏥', 24, 120, 30000, 'UGX',
  'Medical Clearance Form,ID Document', 0
);

// ─── OFFICERS ────────────────────────────────────────────────────────────────
const insertOfficer = db.prepare(`INSERT INTO officers (name, role, district) VALUES (?, ?, ?)`);
insertOfficer.run('Tumusiime Robert', 'District Agricultural Officer', 'Mbarara');
insertOfficer.run('Nakamya Grace', 'Senior District Officer', 'Mbarara');
insertOfficer.run('Okello James', 'District Commercial Officer', 'Kampala');
insertOfficer.run('Atim Doreen', 'District Agricultural Officer', 'Gulu');
insertOfficer.run('Mugisha Peter', 'District Agricultural Officer', 'Jinja');
insertOfficer.run('Asiimwe Ruth', 'District Commercial Officer', 'Mbarara');

const officerNames: Record<number, string> = {
  1: 'Tumusiime Robert', 2: 'Nakamya Grace', 3: 'Okello James',
  4: 'Atim Doreen', 5: 'Mugisha Peter', 6: 'Asiimwe Ruth',
};

const daysAgo = (d: number) => new Date(Date.now() - d * 86400000).toISOString();
const hoursAgo = (h: number) => new Date(Date.now() - h * 3600000).toISOString();

// ─── APPLICATIONS ────────────────────────────────────────────────────────────
interface AppDef {
  ref: string;
  serviceCode: 'cooperative-permit' | 'trading-licence';
  status: string;
  district: string;
  submittedAt: string;
  resolvedAt: string | null;
  officerId: number | null;
  rating: number | null;
  escalated?: boolean;
  moreInfo?: boolean;
  feeVerified?: boolean;
}

const DEMO_NIN = 'CM93019100ABC1J';

const apps: AppDef[] = [
  // Cooperative permit — approved history
  { ref: 'NGS-2026-0001', serviceCode: 'cooperative-permit', status: 'approved', district: 'Kampala', submittedAt: daysAgo(60), resolvedAt: daysAgo(57), officerId: 3, rating: 4 },
  { ref: 'NGS-2026-0002', serviceCode: 'cooperative-permit', status: 'approved', district: 'Gulu', submittedAt: daysAgo(55), resolvedAt: daysAgo(52), officerId: 4, rating: 5 },
  { ref: 'NGS-2026-0003', serviceCode: 'cooperative-permit', status: 'rejected', district: 'Jinja', submittedAt: daysAgo(50), resolvedAt: daysAgo(47), officerId: 5, rating: null },
  { ref: 'NGS-2026-0004', serviceCode: 'cooperative-permit', status: 'approved', district: 'Kampala', submittedAt: daysAgo(45), resolvedAt: daysAgo(42), officerId: 3, rating: 5 },
  // Akello Sarah's prior permit — index 4
  { ref: 'NGS-2026-0005', serviceCode: 'cooperative-permit', status: 'approved', district: 'Mbarara', submittedAt: daysAgo(44), resolvedAt: daysAgo(41), officerId: 1, rating: 5 },
  { ref: 'NGS-2026-0006', serviceCode: 'cooperative-permit', status: 'approved', district: 'Gulu', submittedAt: daysAgo(30), resolvedAt: daysAgo(27), officerId: 4, rating: 4 },
  { ref: 'NGS-2026-0007', serviceCode: 'cooperative-permit', status: 'approved', district: 'Jinja', submittedAt: daysAgo(25), resolvedAt: daysAgo(22), officerId: 5, rating: 5 },
  // Trading licence — approved
  { ref: 'NGS-2026-0008', serviceCode: 'trading-licence', status: 'approved', district: 'Kampala', submittedAt: daysAgo(20), resolvedAt: daysAgo(17), officerId: 3, rating: 4, feeVerified: true },
  { ref: 'NGS-2026-0009', serviceCode: 'trading-licence', status: 'approved', district: 'Mbarara', submittedAt: daysAgo(18), resolvedAt: daysAgo(15), officerId: 6, rating: 5, feeVerified: true },
  { ref: 'NGS-2026-0010', serviceCode: 'cooperative-permit', status: 'approved', district: 'Kampala', submittedAt: daysAgo(15), resolvedAt: daysAgo(12), officerId: 3, rating: 3 },
  { ref: 'NGS-2026-0011', serviceCode: 'cooperative-permit', status: 'rejected', district: 'Gulu', submittedAt: daysAgo(14), resolvedAt: daysAgo(11), officerId: 4, rating: null },
  { ref: 'NGS-2026-0012', serviceCode: 'trading-licence', status: 'approved', district: 'Jinja', submittedAt: daysAgo(12), resolvedAt: daysAgo(9), officerId: 5, rating: 5, feeVerified: true },
  { ref: 'NGS-2026-0013', serviceCode: 'cooperative-permit', status: 'approved', district: 'Kampala', submittedAt: daysAgo(10), resolvedAt: daysAgo(7), officerId: 3, rating: 4 },
  // SLA-breached escalated app
  { ref: 'NGS-2026-0014', serviceCode: 'cooperative-permit', status: 'under_review', district: 'Mbarara', submittedAt: daysAgo(16), resolvedAt: null, officerId: 1, rating: null, escalated: true },
  // Active queue
  { ref: 'NGS-2026-0015', serviceCode: 'trading-licence', status: 'pending_countersign', district: 'Kampala', submittedAt: daysAgo(3), resolvedAt: null, officerId: 3, rating: null, feeVerified: true },
  { ref: 'NGS-2026-0016', serviceCode: 'cooperative-permit', status: 'under_review', district: 'Mbarara', submittedAt: daysAgo(2), resolvedAt: null, officerId: 1, rating: null },
  { ref: 'NGS-2026-0017', serviceCode: 'cooperative-permit', status: 'more_info_requested', district: 'Gulu', submittedAt: daysAgo(5), resolvedAt: null, officerId: 4, rating: null, moreInfo: true },
  { ref: 'NGS-2026-0018', serviceCode: 'trading-licence', status: 'submitted', district: 'Jinja', submittedAt: hoursAgo(4), resolvedAt: null, officerId: null, rating: null },
  { ref: 'NGS-2026-0019', serviceCode: 'cooperative-permit', status: 'submitted', district: 'Gulu', submittedAt: hoursAgo(2), resolvedAt: null, officerId: null, rating: null },
  // More recent approved for dashboard stats
  { ref: 'NGS-2026-0020', serviceCode: 'cooperative-permit', status: 'approved', district: 'Mbarara', submittedAt: daysAgo(6), resolvedAt: daysAgo(4), officerId: 1, rating: 5 },
  { ref: 'NGS-2026-0021', serviceCode: 'trading-licence', status: 'approved', district: 'Kampala', submittedAt: daysAgo(5), resolvedAt: daysAgo(3), officerId: 3, rating: 4, feeVerified: true },
  { ref: 'NGS-2026-0022', serviceCode: 'cooperative-permit', status: 'approved', district: 'Gulu', submittedAt: daysAgo(4), resolvedAt: daysAgo(2), officerId: 4, rating: 5 },
  { ref: 'NGS-2026-0023', serviceCode: 'cooperative-permit', status: 'approved', district: 'Jinja', submittedAt: daysAgo(3), resolvedAt: daysAgo(1), officerId: 5, rating: 4 },
  { ref: 'NGS-2026-0024', serviceCode: 'trading-licence', status: 'approved', district: 'Mbarara', submittedAt: daysAgo(2), resolvedAt: hoursAgo(8), officerId: 6, rating: 5, feeVerified: true },
  { ref: 'NGS-2026-0025', serviceCode: 'cooperative-permit', status: 'approved', district: 'Kampala', submittedAt: daysAgo(1), resolvedAt: hoursAgo(4), officerId: 3, rating: 5 },
];

const serviceTypes: Record<string, string> = {
  'cooperative-permit': 'Cooperative Registration & Agribusiness Permit',
  'trading-licence': 'Trading Licence',
};
const serviceSla: Record<string, { r: number; res: number }> = {
  'cooperative-permit': { r: 48, res: 336 },
  'trading-licence': { r: 24, res: 240 },
};

const names = [
  'Ochieng Paul', 'Nabirye Rose', 'Ssali John', 'Akello Grace', 'Akello Sarah Namugenyi',
  'Nakato Juliet', 'Byaruhanga Frank', 'Atuhaire Olive', 'Kato Emmanuel', 'Nankya Prossy',
  'Walusimbi Simon', 'Apio Harriet', 'Tumwesigye Richard', 'Nassimbwa Fatuma', 'Omara Geoffrey',
  'Bwire Charles', 'Kyomuhendo Agnes', 'Mugerwa David', 'Amoding Irene', 'Sekandi Joseph',
  'Tusiime Flavia', 'Rwamwenge Patrick', 'Acayo Christine', 'Bazira Emmanuel', 'Nakabugo Sandra',
];
const coopNames = [
  'Kampala Urban Farmers Coop', 'Gulu Grain Growers Coop', 'Jinja Sugar Cane Coop',
  'Mbarara Dairy Farmers Coop', 'Mbarara Highlands Coffee Growers Cooperative',
  'Mbale Arabica Coffee Coop', 'Soroti Millet Cooperative', 'Lira Sunflower Coop',
  'Masaka Banana Growers Coop', 'Kabale Irish Potato Coop', 'Arua Sesame Coop',
  'Hoima Oil Palm Coop', 'Fort Portal Tea Growers Coop', 'Mubende Cotton Coop',
  'Iganga Rice Farmers Coop', 'Bushenyi Cattle Coop', 'Tororo Maize Growers Coop',
  'Moroto Livestock Coop', 'Kasese Minerals Coop', 'Mukono Horticulture Coop',
  'Wakiso Poultry Farmers Coop', 'Mityana Sunflower Coop', 'Kiboga Cassava Coop',
  'Rakai Coffee Coop', 'Kyotera Cotton Coop',
];
const bizNames = [
  'Kampala Hardware Supplies', 'Gulu General Store', 'Jinja Electronics',
  'Mbarara Farm Inputs Ltd', 'Highlands Agro Supplies',
  'Mbale Wholesale Traders', 'Soroti Motor Parts', 'Lira Building Materials',
  'Masaka Supermarket', 'Kabale Retail Traders',
  'Arua General Merchants', 'Hoima Petroleum Dealers', 'Fort Portal Pharmacy',
  'Mubende Hardware', 'Iganga Textiles',
  'Bushenyi Agro Dealers', 'Tororo Spare Parts', 'Moroto General Traders',
  'Kasese Hardware', 'Mukono Wholesale',
  'Wakiso Retail Traders', 'Mityana General Store', 'Kiboga Merchants',
  'Rakai Wholesale Supplies', 'Kyotera Agro Traders',
];

const insertApp = db.prepare(`
  INSERT INTO applications (
    referenceNumber, serviceCode, serviceType, nin, fullName, dateOfBirth,
    district, gender, cooperativeName, businessName,
    proposedTin, taxStatus, taxClearanceValidUntil,
    consentTimestamp, status, escalationState, slaResponseHours, slaResolveHours,
    submittedAt, respondedAt, resolvedAt, assignedOfficerId, assignedOfficerName,
    officerNotes, officerDecision, supervisorNotes, supervisorDecision,
    rating, ratingComment, ratedAt
  ) VALUES (
    ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?,
    ?, 'Compliant', '2026-12-31',
    ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?,
    ?, ?, ?, ?,
    ?, ?, ?
  )
`);

const insertNotif = db.prepare(`
  INSERT INTO notifications (applicationId, type, channel, recipient, message, status, createdAt)
  VALUES (?, ?, ?, ?, ?, 'simulated_sent', ?)
`);

const insertPayment = db.prepare(`
  INSERT INTO payments (applicationId, purpose, amount, currency, method, mobileNumber, transactionRef, receiptRef, status, simulatedAt, verifiedAt)
  VALUES (?, ?, ?, 'UGX', ?, ?, ?, ?, ?, ?, ?)
`);

const insertAudit = db.prepare(`
  INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
  VALUES (?, ?, ?, ?, ?, ?)
`);

const insertDoc = db.prepare(`
  INSERT INTO documents (applicationId, originalName, storedName, fileType, uploadedAt, verificationStatus, verifiedBy, verifiedAt)
  VALUES (?, ?, ?, 'application/pdf', ?, ?, ?, ?)
`);

apps.forEach((app, i) => {
  const issarah = i === 4;
  const name = names[i] || `Citizen ${i + 1}`;
  const nin = issarah ? DEMO_NIN : `CM9301910${String(i).padStart(4, '0')}ABC`;
  const fullName = issarah ? 'Akello Sarah Namugenyi' : name;
  const gender = issarah ? 'Female' : (i % 2 === 0 ? 'Male' : 'Female');
  const isTL = app.serviceCode === 'trading-licence';
  const cooperativeName = isTL ? null : (issarah ? 'Mbarara Highlands Coffee Growers Cooperative' : coopNames[i] || `Cooperative ${i + 1}`);
  const businessName = isTL ? (issarah ? 'Highlands Agro Supplies' : bizNames[i] || `Business ${i + 1}`) : null;
  const sla = serviceSla[app.serviceCode];
  const respondedAt = app.resolvedAt ? new Date(new Date(app.submittedAt).getTime() + 3 * 3600000).toISOString() : null;
  const escalationState = app.escalated ? 'escalated' : 'not_escalated';
  const offName = app.officerId ? officerNames[app.officerId] : null;

  const officerNotes = app.status !== 'submitted'
    ? (app.status === 'rejected' ? 'Application did not meet requirements. Incomplete documentation.' : 'Documents reviewed. All SOP checks passed.')
    : null;
  const officerDecision = ['approved', 'rejected'].includes(app.status) ? app.status
    : app.status === 'pending_countersign' ? 'approved' : null;
  const supervisorNotes = ['approved', 'rejected'].includes(app.status) ? 'Reviewed and concurred.' : null;
  const supervisorDecision = ['approved', 'rejected'].includes(app.status) ? app.status : null;
  const ratedAt = app.rating && app.resolvedAt ? new Date(new Date(app.resolvedAt).getTime() + 3600000).toISOString() : null;
  const ratingComment = app.rating
    ? (app.rating >= 5 ? 'Excellent service, very prompt response!' : app.rating >= 4 ? 'Good service, timely processing.' : 'Service was acceptable but could be faster.')
    : null;

  insertApp.run(
    app.ref, app.serviceCode, serviceTypes[app.serviceCode],
    nin, fullName,
    issarah ? '1991-04-12' : `199${(i % 9) + 1}-0${(i % 9) + 1}-1${(i % 9) + 1}`,
    app.district, gender, cooperativeName, businessName,
    `100${String(i + 1).padStart(9, '0')}`,
    app.submittedAt,
    app.status, escalationState, sla.r, sla.res,
    app.submittedAt, respondedAt, app.resolvedAt,
    app.officerId, offName,
    officerNotes, officerDecision, supervisorNotes, supervisorDecision,
    app.rating, ratingComment, ratedAt,
  );

  const appId = i + 1;
  const phone = `+25670${String(7000000 + appId).slice(1)}`;
  const email = `${fullName.toLowerCase().replace(/ /g, '.')}@demo.ug`;
  const submitAt = app.submittedAt;
  const claimAt = new Date(new Date(submitAt).getTime() + 2 * 3600000).toISOString();
  const decisionAt = app.resolvedAt
    ? new Date(new Date(submitAt).getTime() + 24 * 3600000).toISOString()
    : new Date(new Date(submitAt).getTime() + 28 * 3600000).toISOString();

  // ── Audit log ──
  insertAudit.run(appId, 'Application submitted via citizen portal', 'citizen', fullName, null, submitAt);
  if (app.officerId) {
    insertAudit.run(appId, `Application claimed and assigned to ${offName}`, 'officer', offName, null, claimAt);
  }
  if (app.status === 'under_review') {
    insertAudit.run(appId, 'SOP checklist initiated — documents under review', 'officer', offName, 'Identity verified via NIRA. Tax status confirmed via URA.', decisionAt);
    if (app.escalated) {
      const escAt = new Date(new Date(submitAt).getTime() + 300 * 3600000).toISOString();
      insertAudit.run(appId, 'SLA BREACHED — Escalated to supervisor for oversight', 'system', 'NileGov Stack', 'Resolution deadline passed. Escalation threshold exceeded.', escAt);
    }
  } else if (app.status === 'more_info_requested') {
    insertAudit.run(appId, 'Additional information requested from applicant', 'officer', offName, 'Cooperative bylaws require revision — membership list incomplete.', decisionAt);
  } else if (app.status === 'pending_countersign') {
    insertAudit.run(appId, 'Officer decision: approved — forwarded for countersignature', 'officer', offName, 'All 8 SOP checks passed. Documents verified.', decisionAt);
    insertAudit.run(appId, 'Queued for supervisor countersignature', 'system', 'NileGov Stack', null, new Date(new Date(decisionAt).getTime() + 300000).toISOString());
  } else if (app.status === 'approved') {
    insertAudit.run(appId, 'Officer decision: approved', 'officer', offName, 'All SOP checks passed. All documents verified.', decisionAt);
    if (app.resolvedAt) {
      const supAt = new Date(new Date(app.resolvedAt).getTime() - 3600000).toISOString();
      insertAudit.run(appId, 'Supervisor countersignature: approved', 'supervisor', 'Nakamya Grace', 'Reviewed and concurred with officer recommendation.', supAt);
      insertAudit.run(appId, 'Permit granted — application resolved', 'system', 'NileGov Stack', null, app.resolvedAt);
    }
  } else if (app.status === 'rejected') {
    insertAudit.run(appId, 'Officer decision: rejected', 'officer', offName, 'Incomplete documentation. Requirements not met.', decisionAt);
    if (app.resolvedAt) {
      insertAudit.run(appId, 'Application closed — rejected', 'system', 'NileGov Stack', null, app.resolvedAt);
    }
  }

  // ── Notifications ──
  insertNotif.run(appId, 'citizen', 'sms', phone,
    `Your application ${app.ref} has been received. Reference number: ${app.ref}. Track status at NileGov portal.`,
    submitAt);
  insertNotif.run(appId, 'citizen', 'portal',  phone,
    `Application ${app.ref} submitted successfully. Expected response within ${sla.r}h.`,
    submitAt);

  if (app.officerId) {
    insertNotif.run(appId, 'officer', 'internal', offName!,
      `New application ${app.ref} assigned to you for review. SLA deadline: ${sla.r}h response, ${sla.res}h resolution.`,
      claimAt);
  }
  if (app.status === 'more_info_requested') {
    insertNotif.run(appId, 'citizen', 'sms', phone,
      `Action required: Your application ${app.ref} requires additional information. Please log in to NileGov portal to respond.`,
      decisionAt);
    insertNotif.run(appId, 'citizen', 'portal', phone,
      `Application ${app.ref} — officer has requested additional information. Please respond within 5 working days.`,
      decisionAt);
  }
  if (app.status === 'approved' && app.resolvedAt) {
    insertNotif.run(appId, 'citizen', 'sms', phone,
      `APPROVED: Application ${app.ref} has been approved. Your permit has been granted by Mbarara District Local Government.`,
      app.resolvedAt);
    insertNotif.run(appId, 'citizen', 'email', email,
      `Congratulations! Application ${app.ref} APPROVED. Your cooperative registration and agribusiness permit is now active.`,
      app.resolvedAt);
    insertNotif.run(appId, 'citizen', 'portal', phone,
      `Your application ${app.ref} is APPROVED. Visit the portal to download your permit certificate.`,
      app.resolvedAt);
  }
  if (app.status === 'rejected' && app.resolvedAt) {
    insertNotif.run(appId, 'citizen', 'sms', phone,
      `Application ${app.ref} could not be approved. Please visit the district office or re-apply with complete documentation.`,
      app.resolvedAt);
  }
  if (app.escalated) {
    insertNotif.run(appId, 'supervisor', 'internal', 'Nakamya Grace',
      `ESCALATION ALERT: Application ${app.ref} has exceeded its SLA resolution deadline. Immediate supervisor review required.`,
      new Date(new Date(submitAt).getTime() + 300 * 3600000).toISOString());
  }
  if (app.rating && ratedAt) {
    insertNotif.run(appId, 'system', 'portal', 'system',
      `Citizen rating recorded for ${app.ref}: ${app.rating}/5 stars. Feedback logged for M&E reporting.`,
      ratedAt);
  }

  // ── Documents ──
  const docVerified = ['approved', 'pending_countersign'].includes(app.status) ? 'verified' : (app.officerId ? 'pending' : 'pending');
  const docVerifiedBy = docVerified === 'verified' ? offName : null;
  const docVerifiedAt = docVerified === 'verified' ? decisionAt : null;
  if (isTL) {
    insertDoc.run(appId, 'Business_Registration_Certificate.pdf', `seed-doc-${appId}-1.pdf`, submitAt, docVerified, docVerifiedBy, docVerifiedAt);
    insertDoc.run(appId, 'Premises_Photograph.pdf', `seed-doc-${appId}-2.pdf`, submitAt, docVerified, docVerifiedBy, docVerifiedAt);
  } else {
    insertDoc.run(appId, 'Cooperative_Bylaws.pdf', `seed-doc-${appId}-1.pdf`, submitAt, docVerified, docVerifiedBy, docVerifiedAt);
    insertDoc.run(appId, 'Member_Roster.pdf', `seed-doc-${appId}-2.pdf`, submitAt, docVerified, docVerifiedBy, docVerifiedAt);
  }

  // ── Payments (for trading-licence apps) ──
  if (isTL) {
    const payStatus = app.feeVerified ? 'verified' : (app.status === 'submitted' ? 'pending' : 'verified');
    const txRef = `SIM-PAY-TL-${app.ref.split('-').pop()}-2026`;
    const rcptRef = app.feeVerified ? `SIM-RECEIPT-${app.ref.split('-').pop()}-2026` : null;
    const simAt = new Date(new Date(app.submittedAt).getTime() + 30 * 60000).toISOString();
    const verAt = app.feeVerified ? new Date(new Date(app.submittedAt).getTime() + 45 * 60000).toISOString() : null;
    insertPayment.run(
      appId, 'Trading Licence Processing Fee', 120000, 'mobile_money_mtn',
      `+2567${String(8000000 + appId).slice(1)}`,
      txRef, rcptRef, payStatus, simAt, verAt
    );
    if (app.feeVerified) {
      insertAudit.run(appId, `Simulated payment verified — ${txRef}`, 'system', 'NileGov Stack (Pesapal Sandbox)', `Receipt: ${rcptRef}. Amount: UGX 120,000 via MTN Mobile Money.`, simAt);
    }
  }
});

// Clean uploads
const files = fs.readdirSync(uploadsDir);
files.forEach(f => fs.unlinkSync(path.join(uploadsDir, f)));

console.log('✅ Database seeded successfully.');
console.log(`   Services: 5 (2 active)`);
console.log(`   Officers: 6`);
console.log(`   Applications: ${apps.length}`);
console.log(`   Documents: ${apps.length * 2} records (2 per application)`);
console.log(`   Notifications: ~${apps.length * 3} records`);
console.log(`   Payments: ${apps.filter(a => a.serviceCode === 'trading-licence').length} fee-based records`);
console.log(`   Uploads directory cleared: ${uploadsDir}`);
console.log('');
console.log('🎬 Camera-ready state achieved. Run `npm run dev` to start the demo server.');
