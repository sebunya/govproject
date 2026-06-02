# Module: Citizen Profile Foundation

## Purpose

The **Citizen Profile Foundation** module establishes a secure, structured, and compliant citizen data repository for NileGov Stack. It serves as the single source of truth for citizen identity records within the platform. By decoupling the citizen profile from actual National ID registry linkages, it allows public agencies to run local workflow prototyping safely, without exposing real personally identifiable information (PII) or referencing active government databases.

This module provides the database and logic framework supporting citizen request intake, case assignments, notification routing, future consent enforcement, and integration readiness.

---

## Government Use Case

The primary use case demonstrated is the **Lost National ID Replacement** service in Ntinda, Kampala.

### Citizen Profile Intake & Reference Path
1. A fictional citizen (e.g., *Robert Sebunya* living in Ntinda, Kampala) reports a lost National ID.
2. The platform retrieves or creates a **Citizen Profile** identified by a unique, secure, and non-deceptive profile code (e.g., `CP-001`).
3. This profile tracks essential contact information (phone, location, optional email) and preferred contact channels to coordinate officer updates and notifications.
4. The system links this Citizen Profile to the **Service Request** record via a foreign key relationship.

---

## Citizen Data Principles

1. **Optional National ID Number (NIN):** Real NIN validation and storage are not required. The NIN field is labeled optional in the schema and avoided in demo cases to maintain maximum data privacy.
2. **PII Classification:** The schema explicitly designates PII fields under standard Frappe classification guidelines.
3. **No Live Registries:** The module uses purely local, simulated sandbox verification layers. No live connections to NIRA, NITA-U, or UGHub exist.
4. **Fictional Seeding:** All seeded records use synthetic test data.

---

## Entity Schema & Fields

### NileGov Citizen Profile DocType

| Fieldname | Fieldtype | Label | Required? | Description / Valid Values |
| :--- | :--- | :--- | :--- | :--- |
| `citizen_profile_id` | Data | Citizen Profile ID | Yes | Unique profile reference (e.g., `CP-001`). Primary key. |
| `full_name` | Data | Full Name | Yes | The citizen's complete name. |
| `nin` | Data | NIN | No | Optional 14-character Ugandan National Identification Number. |
| `phone` | Data | Phone | Yes/No* | E.164 or Ugandan format. (*At least one contact channel required). |
| `email` | Data | Email | No | Contact email address. |
| `location` | Data | Location | Yes | Parish, Division, or Sub-county (e.g., `Ntinda`). |
| `division_or_area` | Data | District or Division | No | District or administrative area (e.g., `Kampala`). |
| `preferred_contact_channel` | Select | Preferred Contact Channel | Yes | `Phone`, `Email`, `Portal`, `SMS`, `WhatsApp`, `Officer Assisted`. |
| `status` | Select | Status | Yes | `Active`, `Inactive`, `Archived`, `Demo Only`. |
| `linked_user` | Link | Linked User | No | Links profile to standard Frappe User document. |
| `created_from_portal` | Check | Created From Portal | No | Indicates self-service portal request source. |

---

## Workflows & Use Cases Supported

* **Create Citizen Profile:** Application use case (`CreateCitizenProfile`) to instantiate and validate synthetic profiles, enforcing that synthetic emails use `.test` or `example.ug` formats.
* **Update Contact Details:** Application use case (`UpdateCitizenContact`) enabling modification of phone, email, and preferred contact channel.
* **Retrieve Profile:** Fetch profile by ID or NIN (`GetCitizenProfile`).
* **List Linked Service Requests:** Filters request aggregates by the parent profile code.
* **Verify Optional NIN Handling:** Proves that profiles function, link, and save without defining a National ID.

---

## Consent & Integration Readiness

### Consent Records Scaffolding
The Citizen Profile includes metadata and status fields that prepare NileGov Stack to support future **Consent Records** (e.g., storing date and channels where a citizen gave permission to process their data, verifying consent state before triggering simulated verifications).

### Interoperability Prep
The schema uses standard E.164 and E-Government-ready JSON fields that align with the Uganda National Data Integration Platform (UGHub) messaging formats.

---

## Testing Summary

The module is verified offline by 17 new pytest unit tests (bringing the suite to 135 passing tests):
* **Domain Entity Validation:** Ensures names, locations, and phone formats validate correctly.
* **Optional NIN Verification:** Confirms NIN-less profile instantiation works seamlessly.
* **Safety & Compliance Check:** Restricts production domains from demo profiles.
* **Mock Repository Operations:** Proves repository mapping works under synthetic database layers.

---

## Deployment & Validation Status

* **Status:** Implemented at code, schema, seed, and test level.
* **Runtime Desk Validation:** Pending deployment to Hetzner or another working Linux/Docker host.
* **Manual Setup Note:** Run `bench --site nilegov.local migrate` on the deployment host to update schema tables and execute the `seed_demo_records` patch.

---

## Claims Registry

### Safe Claims
* Fully implemented and tested Citizen Profile domain logic.
* Complete Gunicorn-ready database schema definitions.
* Safe, fictional demo records seeded.
* Tested mapping repository adapters.

### Claims to Avoid
* Live integration with NIRA database.
* Verification against real Ugandan citizen registries.
* Production-ready citizen authentication.
