# Module: Evidence & Document Foundation

## Purpose

The **Evidence & Document Foundation** module manages document metadata, attachments, and officer review notes within the NileGov Stack. It connects proof-of-loss police letters, statutory declaration affidavits, supporting ID placeholders, and payment receipt placeholders to **Citizen Profiles**, **Consent Records**, and **Service Requests**. By focusing on a metadata layer and verification statuses, it allows officials to review attachments and update verification state using simulated placeholders without requiring live external registry validation.

---

## Government Use Case

The primary use case demonstrated is the **Lost National ID Replacement** service in Ntinda, Kampala.

### Evidence Submission & Officer Verification Flow
1. A fictional citizen (e.g. *Demo Citizen A*) submits a Lost National ID Replacement request.
2. During submission, placeholder files representing necessary supporting documents are attached:
   * **Police Letter Placeholder:** A report detailing the theft or loss of the ID.
   * **Affidavit Placeholder:** A statutory declaration signed by a Commissioner of Oaths.
   * **Supporting ID Placeholder:** Secondary identification such as a driving permit or employee ID.
   * **Payment Receipt Placeholder:** Proof of mock replacement fee payment.
3. Officers retrieve evidence items linked to the service request (`req_pass3_001`) or citizen profile (`CP-001`).
4. Officers review document contents, add verification notes, and record status updates (`Submitted` to `Under Review` to `Accepted`, `Rejected`, or `Requires Replacement`).

---

## Document & Evidence Principles

1. **Simulated Attachment References:** Attachments use safe fictional string references (e.g. `demo-police-letter-placeholder.pdf`). The system does not store or process real personal files.
2. **Internal Officer Verification:** The module enforces manual workflow-based verification states. It does not automate validity checks or authenticate documents.
3. **Audit Trail Integrity:** Officer notes and status changes update the document's verification metadata, logging who verified it and when.
4. **Consent-Backed Isolation:** If applicable, evidence documents can be optionally linked to a **Consent Record** (e.g., matching the data-sharing authorization code), ensuring metadata is only kept under active privacy consents.

---

## Allowed Vocabularies

### Document Types
* **Police Letter Placeholder:** Formal police abstract or loss report.
* **Affidavit Placeholder:** Commissioner of Oaths sworn statement.
* **Supporting ID Placeholder:** Secondary identification placeholder.
* **Payment Receipt Placeholder:** Fee payment receipt confirmation.
* **Application Form Placeholder:** Signed application printout or scan.
* **Other Supporting Document:** Miscellanous evidence attachments.

### Upload/Source Channels
* `Web Form`
* `Officer Assisted`
* `Portal`
* `Email`
* `WhatsApp`
* `Other`

### Verification Statuses
* `Submitted`: Initial state after citizen or officer upload.
* `Under Review`: Officer is currently inspecting the document.
* `Accepted`: Document is verified and accepted as valid.
* `Rejected`: Document is invalid (e.g. wrong citizen details).
* `Requires Replacement`: Document needs to be re-uploaded (e.g. blurry scan).
* `Not Required`: Document is skipped for this service type.
* `Demo Placeholder`: Seeding fallback for static simulation.

---

## Entity Schema & Fields

### NileGov Evidence Document DocType

| Fieldname | Fieldtype | Label | Required? | Description / Valid Values |
| :--- | :--- | :--- | :--- | :--- |
| `evidence_document_id` | Data | Evidence Document ID | Yes | Unique reference (e.g. `EVI-CP001-POL`). |
| `citizen_profile` | Link | Citizen Profile | Yes | Links to parent `NileGov Citizen Profile`. |
| `service_request` | Link | Service Request | Yes | Links to parent `NileGov Service Request`. |
| `consent_record` | Link | Consent Record | No | Optional link to privacy `NileGov Consent Record`. |
| `document_type` | Select | Document Type | Yes | Approved types list (see above). |
| `document_title` | Data | Document Title | Yes | Short title (e.g. `Ntinda Police Post Loss Letter`). |
| `file` | Attach | File | Yes | File placeholder name (e.g. `demo-police-letter-placeholder.pdf`). |
| `upload_channel` | Select | Upload/Source Channel | Yes | Approved channels list (see above). |
| `uploaded_by` | Link | Uploaded By | Yes | Link to `User` who uploaded (e.g. `officer_demo`). |
| `uploaded_at` | Datetime | Uploaded At | Yes | Timestamp of upload. |
| `verification_status` | Select | Verification Status | Yes | Approved verification statuses list (see above). |
| `verified_by` | Data | Verified By | No | Username of officer performing verification. |
| `verified_timestamp` | Datetime | Verified Timestamp | No | Timestamp of verification. |
| `visibility` | Select | Visibility | Yes | `Citizen and Officer`, `Officer Only`, `Supervisor Only`. |
| `officer_notes` | Small Text | Officer Notes | No | Detailed comments logged by reviewing officers. |
| `disclaimer` | Small Text | Disclaimer | Yes | Default: "Prototype simulation only. No live Government registry access." |

*Note: The legacy field `notes` is kept in the JSON schema to ensure full backward compatibility with static quality checks.*

---

## Workflows & Use Cases Supported

* **Create Evidence Document:** Application service (`CreateEvidenceDocument`) registering a uploaded document.
* **Verify Evidence Document:** Officers update the verification status and log verification metadata (`VerifyEvidenceDocument`).
* **List Service Request Evidence:** Retrieve all evidence items linked to a case (`ListServiceRequestEvidence`).
* **List Citizen Profile Evidence:** Retrieve all evidence items linked to a citizen's profile history (`ListCitizenProfileEvidence`).
* **Add Officer Notes:** Update review comments on specific document objects.

---

## Testing Summary

Verified by 13 new pytest integration and unit tests (suite total: 163 passing tests):
* **Domain aggregate checks:** Validates creation, status transitions, and empty note rejection.
* **Use Cases:** Verifies creating, listing by citizen or request, and verifying documents via repository adapters.
* **Patches Seeding:** Verifies that the idempotent seeding script correctly maps evidence records under mocks.

---

## Deployment & Validation Status

* **Status:** Implemented at code, schema, seed, and test level.
* **Runtime Desk Validation:** Pending deployment to Hetzner or another working Linux/Docker host.
* **Manual Setup Note:** Run `bench --site nilegov.local migrate` on the deployment host to update schema tables and execute the `seed_demo_records` patch.

---

## Claims Registry

### Safe Claims
* Fully implemented domain models, use cases, and validations.
* Complete database schema definitions with custom autoname.
* Idempotent seeding patch written and registered in `patches.txt`.
* Clean separation of concerns allowing pluggable repository adapters.

### Claims to Avoid
* Live verification of Police Loss Letters or Affidavit authenticity.
* Integration with the Uganda Police Force or judicial registry databases.
* Automated OCR document parsing or AI-based classification.
* Integration with payment providers for receipt authentication.
