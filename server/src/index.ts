import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';
import { v4 as uuidv4 } from 'uuid';
import { db, initSchema, uploadsDir } from './db.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

initSchema();

const app = express();
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(uploadsDir));

const storage = multer.diskStorage({
  destination: uploadsDir,
  filename: (_req, file, cb) => {
    const ext = path.extname(file.originalname);
    cb(null, `${uuidv4()}${ext}`);
  },
});
const upload = multer({ storage, limits: { fileSize: 5 * 1024 * 1024 } });

// ─── SIMULATED INTEGRATIONS ────────────────────────────────────────────────

app.post('/api/simulate/nira', (_req, res) => {
  res.json({
    fullName: 'Akello Sarah Namugenyi',
    dateOfBirth: '1991-04-12',
    district: 'Mbarara',
    gender: 'Female',
    verified: true,
    _simulated: true,
  });
});

app.post('/api/simulate/ura', (_req, res) => {
  res.json({
    taxStatus: 'Compliant',
    clearanceValidUntil: '2026-12-31',
    _simulated: true,
  });
});

// ─── APPLICATIONS ──────────────────────────────────────────────────────────

app.post('/api/applications', upload.fields([
  { name: 'bylaws', maxCount: 1 },
  { name: 'memberRoster', maxCount: 1 },
]), (req, res) => {
  const body = req.body;
  const files = req.files as Record<string, Express.Multer.File[]>;

  const year = new Date().getFullYear();
  const count = (db.prepare('SELECT COUNT(*) as c FROM applications').get() as { c: number }).c;
  const refNum = `NGS-${year}-${String(count + 1).padStart(4, '0')}`;
  const now = new Date().toISOString();

  const stmt = db.prepare(`
    INSERT INTO applications (
      referenceNumber, nin, fullName, dateOfBirth, district, gender,
      cooperativeName, proposedTin, taxStatus, taxClearanceValidUntil,
      consentTimestamp, status, slaResponseHours, slaResolveHours, submittedAt
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'submitted', 48, 336, ?)
  `);

  const result = stmt.run(
    refNum,
    body.nin, body.fullName, body.dateOfBirth, body.district, body.gender,
    body.cooperativeName, body.proposedTin, body.taxStatus, body.taxClearanceValidUntil,
    now, now
  );

  const appId = result.lastInsertRowid as number;

  const insertDoc = db.prepare(`
    INSERT INTO documents (applicationId, originalName, storedName, fileType, uploadedAt)
    VALUES (?, ?, ?, ?, ?)
  `);

  if (files?.bylaws?.[0]) {
    const f = files.bylaws[0];
    insertDoc.run(appId, f.originalname, f.filename, f.mimetype, now);
  }
  if (files?.memberRoster?.[0]) {
    const f = files.memberRoster[0];
    insertDoc.run(appId, f.originalname, f.filename, f.mimetype, now);
  }

  db.prepare(`
    INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, 'Application submitted', 'citizen', ?, 'Application submitted via citizen portal', ?)
  `).run(appId, body.fullName, now);

  res.json({ referenceNumber: refNum, id: appId });
});

app.get('/api/applications', (req, res) => {
  const { persona, nin } = req.query;
  let rows: unknown[];

  if (persona === 'citizen' && nin) {
    rows = db.prepare(`
      SELECT a.*, GROUP_CONCAT(d.originalName, '||') as docNames
      FROM applications a
      LEFT JOIN documents d ON d.applicationId = a.id
      WHERE a.nin = ?
      GROUP BY a.id
      ORDER BY a.submittedAt DESC
    `).all(nin as string);
  } else if (persona === 'officer') {
    rows = db.prepare(`
      SELECT a.*, GROUP_CONCAT(d.originalName, '||') as docNames
      FROM applications a
      LEFT JOIN documents d ON d.applicationId = a.id
      WHERE a.status IN ('submitted','under_review','more_info_requested')
      GROUP BY a.id
      ORDER BY a.submittedAt ASC
    `).all();
  } else if (persona === 'supervisor') {
    rows = db.prepare(`
      SELECT a.*, GROUP_CONCAT(d.originalName, '||') as docNames
      FROM applications a
      LEFT JOIN documents d ON d.applicationId = a.id
      WHERE a.status = 'pending_countersign'
      GROUP BY a.id
      ORDER BY a.submittedAt ASC
    `).all();
  } else {
    rows = db.prepare(`
      SELECT a.*, GROUP_CONCAT(d.originalName, '||') as docNames
      FROM applications a
      LEFT JOIN documents d ON d.applicationId = a.id
      GROUP BY a.id
      ORDER BY a.submittedAt DESC
      LIMIT 100
    `).all();
  }

  res.json(rows);
});

app.get('/api/applications/:id', (req, res) => {
  const app = db.prepare(`SELECT * FROM applications WHERE id = ? OR referenceNumber = ?`)
    .get(req.params.id, req.params.id);
  if (!app) return res.status(404).json({ error: 'Not found' });

  const docs = db.prepare(`SELECT * FROM documents WHERE applicationId = ?`)
    .all((app as { id: number }).id);
  const auditLog = db.prepare(`SELECT * FROM audit_log WHERE applicationId = ? ORDER BY createdAt ASC`)
    .all((app as { id: number }).id);

  res.json({ ...(app as object), documents: docs, auditLog });
});

app.patch('/api/applications/:id/officer-decision', (req, res) => {
  const { decision, notes } = req.body;
  const now = new Date().toISOString();

  let newStatus: string;
  if (decision === 'approved') newStatus = 'pending_countersign';
  else if (decision === 'rejected') newStatus = 'rejected';
  else newStatus = 'more_info_requested';

  db.prepare(`
    UPDATE applications SET
      status = ?, officerDecision = ?, officerNotes = ?,
      respondedAt = COALESCE(respondedAt, ?), assignedOfficerId = 1
    WHERE id = ?
  `).run(newStatus, decision, notes, now, req.params.id);

  db.prepare(`
    INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, ?, 'officer', 'Tumusiime Robert', ?, ?)
  `).run(req.params.id, `Officer decision: ${decision}`, notes || '', now);

  const updated = db.prepare('SELECT * FROM applications WHERE id = ?').get(req.params.id);
  res.json(updated);
});

app.patch('/api/applications/:id/supervisor-decision', (req, res) => {
  const { decision, notes } = req.body;
  const now = new Date().toISOString();

  const newStatus = decision === 'approved' ? 'approved' : 'rejected';

  db.prepare(`
    UPDATE applications SET
      status = ?, supervisorDecision = ?, supervisorNotes = ?, resolvedAt = ?
    WHERE id = ?
  `).run(newStatus, decision, notes, now, req.params.id);

  db.prepare(`
    INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, ?, 'supervisor', 'Nakamya Grace', ?, ?)
  `).run(req.params.id, `Supervisor decision: ${decision}`, notes || '', now);

  const updated = db.prepare('SELECT * FROM applications WHERE id = ?').get(req.params.id);
  res.json(updated);
});

app.patch('/api/applications/:id/rate', (req, res) => {
  const { rating, comment } = req.body;
  const now = new Date().toISOString();

  db.prepare(`
    UPDATE applications SET rating = ?, ratingComment = ?, ratedAt = ? WHERE id = ?
  `).run(rating, comment || null, now, req.params.id);

  db.prepare(`
    INSERT INTO audit_log (applicationId, action, actorPersona, actorName, notes, createdAt)
    VALUES (?, 'Service rated', 'citizen', 'Akello Sarah Namugenyi', ?, ?)
  `).run(req.params.id, `Rating: ${rating}/5 — ${comment || ''}`, now);

  res.json({ ok: true });
});

// ─── DASHBOARD ─────────────────────────────────────────────────────────────

app.get('/api/dashboard', (_req, res) => {
  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];
  const weekAgo = new Date(today.getTime() - 7 * 86400000).toISOString();

  const todayProcessed = (db.prepare(`
    SELECT COUNT(*) as c FROM applications
    WHERE resolvedAt >= ? AND status IN ('approved','rejected')
  `).get(`${todayStr}T00:00:00.000Z`) as { c: number }).c;

  const weekProcessed = (db.prepare(`
    SELECT COUNT(*) as c FROM applications
    WHERE resolvedAt >= ? AND status IN ('approved','rejected')
  `).get(weekAgo) as { c: number }).c;

  const avgRes = (db.prepare(`
    SELECT AVG((julianday(resolvedAt) - julianday(submittedAt)) * 24) as avg
    FROM applications
    WHERE resolvedAt IS NOT NULL
  `).get() as { avg: number | null }).avg;

  const totalResolved = (db.prepare(`
    SELECT COUNT(*) as c FROM applications WHERE resolvedAt IS NOT NULL
  `).get() as { c: number }).c;

  const onTime = (db.prepare(`
    SELECT COUNT(*) as c FROM applications
    WHERE resolvedAt IS NOT NULL
      AND (julianday(resolvedAt) - julianday(submittedAt)) * 24 <= slaResolveHours
  `).get() as { c: number }).c;

  const slaCompliancePercent = totalResolved > 0 ? Math.round((onTime / totalResolved) * 100) : 100;

  const activeApplications = (db.prepare(`
    SELECT COUNT(*) as c FROM applications WHERE status NOT IN ('approved','rejected')
  `).get() as { c: number }).c;

  const bottlenecks = [
    { stage: 'Awaiting Officer Review', count: 0, avgWaitHours: 0 },
    { stage: 'Pending Countersignature', count: 0, avgWaitHours: 0 },
    { stage: 'More Information Requested', count: 0, avgWaitHours: 0 },
  ];

  const stageCounts = db.prepare(`
    SELECT status, COUNT(*) as c,
      AVG((julianday('now') - julianday(submittedAt)) * 24) as avgWait
    FROM applications
    WHERE status IN ('submitted','pending_countersign','more_info_requested')
    GROUP BY status
  `).all() as { status: string; c: number; avgWait: number }[];

  stageCounts.forEach(row => {
    if (row.status === 'submitted') {
      bottlenecks[0].count = row.c;
      bottlenecks[0].avgWaitHours = Math.round(row.avgWait);
    } else if (row.status === 'pending_countersign') {
      bottlenecks[1].count = row.c;
      bottlenecks[1].avgWaitHours = Math.round(row.avgWait);
    } else if (row.status === 'more_info_requested') {
      bottlenecks[2].count = row.c;
      bottlenecks[2].avgWaitHours = Math.round(row.avgWait);
    }
  });

  const districtStats = db.prepare(`
    SELECT district,
      COUNT(*) as total,
      SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
      SUM(CASE WHEN resolvedAt IS NOT NULL
        AND (julianday(resolvedAt) - julianday(submittedAt)) * 24 > slaResolveHours
        THEN 1 ELSE 0 END) as slaBreached
    FROM applications
    GROUP BY district
    ORDER BY total DESC
  `).all();

  const weeklyTrend = [];
  for (let w = 4; w >= 0; w--) {
    const weekStart = new Date(today.getTime() - (w + 1) * 7 * 86400000).toISOString();
    const weekEnd = new Date(today.getTime() - w * 7 * 86400000).toISOString();
    const label = `Week -${w}`;
    const submitted = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE submittedAt >= ? AND submittedAt < ?`).get(weekStart, weekEnd) as { c: number }).c;
    const resolved = (db.prepare(`SELECT COUNT(*) as c FROM applications WHERE resolvedAt >= ? AND resolvedAt < ?`).get(weekStart, weekEnd) as { c: number }).c;
    const breached = (db.prepare(`
      SELECT COUNT(*) as c FROM applications
      WHERE resolvedAt >= ? AND resolvedAt < ?
        AND (julianday(resolvedAt) - julianday(submittedAt)) * 24 > slaResolveHours
    `).get(weekStart, weekEnd) as { c: number }).c;
    weeklyTrend.push({ week: label, submitted, resolved, slaBreached: breached });
  }

  const categoryStats = [{
    category: 'Cooperative Registration & Agribusiness Permit',
    total: totalResolved,
    slaBreached: totalResolved - onTime,
    avgResolutionHours: Math.round(avgRes || 0),
  }];

  res.json({
    todayProcessed,
    weekProcessed,
    avgResolutionHours: Math.round(avgRes || 0),
    slaCompliancePercent,
    activeApplications,
    bottlenecks,
    districtStats,
    weeklyTrend,
    categoryStats,
  });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`NileGov API running on http://localhost:${PORT}`);
});
