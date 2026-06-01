import { db, initSchema, uploadsDir } from './db.js';
import fs from 'fs';
import path from 'path';

console.log('🌱 Seeding NileGov database to camera-ready state...');

// Ensure schema exists first
initSchema();

// Wipe existing data
db.exec(`
  DELETE FROM audit_log;
  DELETE FROM documents;
  DELETE FROM applications;
  DELETE FROM officers;
  DELETE FROM sqlite_sequence WHERE name IN ('audit_log','documents','applications','officers');
`);

initSchema();

// Officers
const insertOfficer = db.prepare(`
  INSERT INTO officers (name, role, district) VALUES (?, ?, ?)
`);
insertOfficer.run('Tumusiime Robert', 'officer', 'Mbarara');
insertOfficer.run('Nakamya Grace', 'supervisor', 'Mbarara');
insertOfficer.run('Okello James', 'officer', 'Kampala');
insertOfficer.run('Atim Doreen', 'officer', 'Gulu');
insertOfficer.run('Mugisha Peter', 'officer', 'Jinja');

// Seed historical applications for dashboard realism
const now = new Date();
const daysAgo = (d: number) => new Date(now.getTime() - d * 86400000).toISOString();

const historicalApps = [
  { ref: 'NGS-2026-0001', status: 'approved', district: 'Kampala', submittedAt: daysAgo(30), resolvedAt: daysAgo(28), officerId: 3, rating: 5 },
  { ref: 'NGS-2026-0002', status: 'approved', district: 'Gulu', submittedAt: daysAgo(25), resolvedAt: daysAgo(22), officerId: 4, rating: 4 },
  { ref: 'NGS-2026-0003', status: 'approved', district: 'Jinja', submittedAt: daysAgo(20), resolvedAt: daysAgo(18), officerId: 5, rating: 5 },
  { ref: 'NGS-2026-0004', status: 'rejected', district: 'Kampala', submittedAt: daysAgo(18), resolvedAt: daysAgo(15), officerId: 3, rating: 2 },
  { ref: 'NGS-2026-0005', status: 'approved', district: 'Mbarara', submittedAt: daysAgo(14), resolvedAt: daysAgo(12), officerId: 1, rating: 5 },
  { ref: 'NGS-2026-0006', status: 'approved', district: 'Gulu', submittedAt: daysAgo(12), resolvedAt: daysAgo(10), officerId: 4, rating: 4 },
  { ref: 'NGS-2026-0007', status: 'approved', district: 'Jinja', submittedAt: daysAgo(10), resolvedAt: daysAgo(8), officerId: 5, rating: 5 },
  { ref: 'NGS-2026-0008', status: 'approved', district: 'Kampala', submittedAt: daysAgo(8), resolvedAt: daysAgo(6), officerId: 3, rating: 4 },
  { ref: 'NGS-2026-0009', status: 'under_review', district: 'Mbarara', submittedAt: daysAgo(3), resolvedAt: null, officerId: 1, rating: null },
  { ref: 'NGS-2026-0010', status: 'pending_countersign', district: 'Kampala', submittedAt: daysAgo(2), resolvedAt: null, officerId: 3, rating: null },
  { ref: 'NGS-2026-0011', status: 'submitted', district: 'Gulu', submittedAt: daysAgo(1), resolvedAt: null, officerId: null, rating: null },
  { ref: 'NGS-2026-0012', status: 'approved', district: 'Jinja', submittedAt: daysAgo(5), resolvedAt: daysAgo(3), officerId: 5, rating: 5 },
  { ref: 'NGS-2026-0013', status: 'approved', district: 'Kampala', submittedAt: daysAgo(6), resolvedAt: daysAgo(4), officerId: 3, rating: 3 },
  { ref: 'NGS-2026-0014', status: 'more_info_requested', district: 'Mbarara', submittedAt: daysAgo(4), resolvedAt: null, officerId: 1, rating: null },
];

const names = [
  'Ochieng Paul', 'Nabirye Rose', 'Ssali John', 'Akello Grace', 'Mugisha Denis',
  'Nakato Juliet', 'Byaruhanga Frank', 'Atuhaire Olive', 'Kato Emmanuel', 'Nankya Prossy',
  'Walusimbi Simon', 'Apio Harriet', 'Tumwesigye Richard', 'Nassimbwa Fatuma', 'Omara Geoffrey'
];

const coopNames = [
  'Kampala Urban Farmers Coop', 'Gulu Grain Growers Coop', 'Jinja Sugar Cane Coop',
  'Mbarara Dairy Farmers Coop', 'Tororo Maize Growers Coop', 'Mbale Arabica Coffee Coop',
  'Soroti Millet Cooperative', 'Lira Sunflower Coop', 'Masaka Banana Growers Coop',
  'Kabale Irish Potato Coop', 'Arua Sesame Coop', 'Hoima Oil Palm Coop',
  'Fort Portal Tea Growers Coop', 'Mubende Cotton Coop', 'Iganga Rice Farmers Coop'
];

const insertApp = db.prepare(`
  INSERT INTO applications (
    referenceNumber, nin, fullName, dateOfBirth, district, gender,
    cooperativeName, proposedTin, taxStatus, taxClearanceValidUntil,
    consentTimestamp, status, slaResponseHours, slaResolveHours,
    submittedAt, respondedAt, resolvedAt, assignedOfficerId,
    officerNotes, officerDecision, supervisorNotes, supervisorDecision,
    rating, ratingComment, ratedAt
  ) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, 48, 336, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?
  )
`);

historicalApps.forEach((app, i) => {
  const name = names[i] || `Citizen ${i + 1}`;
  const coop = coopNames[i] || `Cooperative ${i + 1}`;
  const respondedAt = app.resolvedAt ? new Date(new Date(app.submittedAt).getTime() + 86400000).toISOString() : null;
  const rating = app.rating;
  const ratedAt = rating && app.resolvedAt ? new Date(new Date(app.resolvedAt).getTime() + 3600000).toISOString() : null;

  insertApp.run(
    app.ref,
    `CM9301910${String(i).padStart(4, '0')}ABC`,
    name,
    `199${(i % 9) + 1}-0${(i % 9) + 1}-1${(i % 9) + 5}`,
    app.district,
    i % 2 === 0 ? 'Male' : 'Female',
    coop,
    `100${String(i + 1).padStart(9, '0')}`,
    'Compliant',
    '2026-12-31',
    app.submittedAt,
    app.status,
    app.submittedAt,
    respondedAt,
    app.resolvedAt,
    app.officerId,
    app.status !== 'submitted' ? 'Documents reviewed. All requirements met.' : null,
    ['approved', 'rejected'].includes(app.status) ? app.status : (app.status === 'pending_countersign' ? 'approved' : null),
    ['approved', 'rejected'].includes(app.status) ? 'Reviewed and concurred.' : null,
    ['approved', 'rejected'].includes(app.status) ? app.status : null,
    rating,
    rating ? (rating >= 4 ? 'Excellent service, very prompt!' : rating === 3 ? 'Satisfactory service.' : 'Process was slow and unclear.') : null,
    ratedAt
  );
});

// Seed audit entries for historical apps
const insertAudit = db.prepare(`
  INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
  VALUES (?, ?, ?, ?, ?, ?)
`);

for (let i = 1; i <= historicalApps.length; i++) {
  insertAudit.run(i, 'Application submitted', 'citizen', names[i - 1], 'Application submitted via citizen portal', historicalApps[i - 1].submittedAt);
}

// Clean uploads dir for fresh demo
const files = fs.readdirSync(uploadsDir);
files.forEach(f => fs.unlinkSync(path.join(uploadsDir, f)));

console.log('✅ Database seeded successfully.');
console.log(`   Officers: 5`);
console.log(`   Applications: ${historicalApps.length} historical records`);
console.log(`   Uploads directory cleared: ${uploadsDir}`);
console.log('');
console.log('🎬 Camera-ready state achieved. Run `npm run dev` to start the demo server.');
