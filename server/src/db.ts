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

    CREATE TABLE IF NOT EXISTS applications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      referenceNumber TEXT NOT NULL UNIQUE,
      serviceType TEXT NOT NULL DEFAULT 'Cooperative Registration & Agribusiness Permit',
      nin TEXT NOT NULL,
      fullName TEXT NOT NULL,
      dateOfBirth TEXT NOT NULL,
      district TEXT NOT NULL,
      gender TEXT NOT NULL,
      cooperativeName TEXT NOT NULL,
      proposedTin TEXT NOT NULL,
      taxStatus TEXT NOT NULL,
      taxClearanceValidUntil TEXT NOT NULL,
      consentTimestamp TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'submitted',
      slaResponseHours INTEGER NOT NULL DEFAULT 48,
      slaResolveHours INTEGER NOT NULL DEFAULT 336,
      submittedAt TEXT NOT NULL,
      respondedAt TEXT,
      resolvedAt TEXT,
      assignedOfficerId INTEGER REFERENCES officers(id),
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
      uploadedAt TEXT NOT NULL
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
