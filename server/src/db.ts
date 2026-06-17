import { DatabaseSync } from 'node:sqlite';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data');
const DB_PATH = path.join(DATA_DIR, 'nilegov.db');

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(path.join(DATA_DIR, 'uploads'))) {
  fs.mkdirSync(path.join(DATA_DIR, 'uploads'), { recursive: true });
}

export const db = new DatabaseSync(DB_PATH);

export function initSchema() {
  db.exec(`
    PRAGMA journal_mode = WAL;
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS officers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      role TEXT NOT NULL,
      district TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS services (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      code TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      description TEXT NOT NULL,
      category TEXT NOT NULL,
      icon TEXT NOT NULL DEFAULT '📄',
      slaResponseHours INTEGER NOT NULL DEFAULT 48,
      slaResolveHours INTEGER NOT NULL DEFAULT 336,
      feeAmount INTEGER NOT NULL DEFAULT 0,
      feeCurrency TEXT NOT NULL DEFAULT 'UGX',
      requiredDocs TEXT NOT NULL DEFAULT 'Application Letter',
      active INTEGER NOT NULL DEFAULT 1,
      disclaimer TEXT NOT NULL DEFAULT 'Prototype service catalogue only. Not connected to a live government service registry.'
    );

    CREATE TABLE IF NOT EXISTS applications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      referenceNumber TEXT NOT NULL UNIQUE,
      serviceCode TEXT NOT NULL DEFAULT 'cooperative-permit',
      serviceType TEXT NOT NULL DEFAULT 'Cooperative Registration & Agribusiness Permit',
      nin TEXT NOT NULL,
      fullName TEXT NOT NULL,
      dateOfBirth TEXT NOT NULL,
      district TEXT NOT NULL,
      gender TEXT NOT NULL,
      phoneNumber TEXT,
      email TEXT,
      cooperativeName TEXT,
      businessName TEXT,
      proposedTin TEXT NOT NULL,
      taxStatus TEXT NOT NULL,
      taxClearanceValidUntil TEXT NOT NULL,
      consentTimestamp TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'submitted',
      escalationState TEXT NOT NULL DEFAULT 'not_escalated',
      slaResponseHours INTEGER NOT NULL DEFAULT 48,
      slaResolveHours INTEGER NOT NULL DEFAULT 336,
      submittedAt TEXT NOT NULL,
      respondedAt TEXT,
      resolvedAt TEXT,
      assignedOfficerId INTEGER REFERENCES officers(id),
      assignedOfficerName TEXT,
      officerNotes TEXT,
      officerDecision TEXT,
      supervisorNotes TEXT,
      supervisorDecision TEXT,
      rating INTEGER,
      ratingComment TEXT,
      ratedAt TEXT
    );

    CREATE TABLE IF NOT EXISTS documents (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      applicationId INTEGER NOT NULL REFERENCES applications(id),
      originalName TEXT NOT NULL,
      storedName TEXT NOT NULL,
      fileType TEXT NOT NULL,
      uploadedAt TEXT NOT NULL,
      verificationStatus TEXT NOT NULL DEFAULT 'pending',
      verificationNotes TEXT,
      verifiedBy TEXT,
      verifiedAt TEXT
    );

    CREATE TABLE IF NOT EXISTS notifications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      applicationId INTEGER REFERENCES applications(id),
      type TEXT NOT NULL,
      channel TEXT NOT NULL,
      recipient TEXT NOT NULL,
      message TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'simulated_sent',
      disclaimer TEXT NOT NULL DEFAULT 'Prototype simulation only. No live SMS, email or portal notification was sent.',
      createdAt TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS payments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      applicationId INTEGER REFERENCES applications(id),
      purpose TEXT NOT NULL,
      amount INTEGER NOT NULL,
      currency TEXT NOT NULL DEFAULT 'UGX',
      method TEXT,
      mobileNumber TEXT,
      transactionRef TEXT,
      receiptRef TEXT,
      status TEXT NOT NULL DEFAULT 'pending',
      disclaimer TEXT NOT NULL DEFAULT 'Prototype simulation only. No live payment was processed.',
      simulatedAt TEXT,
      verifiedAt TEXT,
      createdAt TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS audit_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      applicationId INTEGER REFERENCES applications(id),
      action TEXT NOT NULL,
      actorPersona TEXT NOT NULL,
      actorName TEXT NOT NULL,
      notes TEXT,
      createdAt TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);
}

export const uploadsDir = path.join(DATA_DIR, 'uploads');
