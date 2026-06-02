# Module 11: Roles, Permissions and User Profiles Foundation

## Purpose

The Roles, Permissions and User Profiles Foundation defines the access-control model for NileGov Stack.

The goal is to ensure that officers, supervisors, auditors, payments users, M&E users and administrators have clear responsibilities and controlled access to sensitive government-service records.

This module is Frappe-native in design and prepares NileGov for runtime role configuration through Frappe Role Permission Manager, Role Profiles and user assignments.

## Current status

**Pass 11B-2 aligned.** The following sources now consistently use the canonical NileGov-prefixed role names:

- `hooks.py` fixtures
- `patches/seed_roles.py`
- `interfaces/permissions.py`
- All 15 DocType JSON permission arrays
- `workspace.json` roles block
- `patches/seed_demo_records.py` demo user role assignments

This is a prototype permission foundation.

No live MDA users are configured.
No live government directory is connected.
No production identity provider is connected.
Runtime role assignment remains deferred to Hetzner/Frappe validation.

## Role model

### NileGov Citizen Officer

Responsible for frontline citizen service handling.

Allowed by design:

- create service requests;
- view assigned service requests;
- view limited citizen profile references;
- add case notes;
- see assigned queue status;
- initiate simulated service processing steps.

Restricted by design:

- cannot edit audit events;
- cannot edit integration simulation logs;
- cannot verify payments;
- cannot alter service catalogue settings;
- cannot change SLA rules;
- cannot view unnecessary sensitive evidence content.

### NileGov Records Officer

Responsible for evidence and document review.

Allowed by design:

- view service requests requiring document review;
- review evidence documents;
- approve evidence placeholders;
- reject evidence placeholders;
- request replacement documents;
- add records review notes.

Restricted by design:

- cannot verify payments;
- cannot edit audit logs;
- cannot edit integration logs;
- cannot change service catalogue settings;
- cannot change system configuration.

### NileGov Payments Officer

Responsible for simulated and sandbox payment review.

Allowed by design:

- view payment records;
- update simulated payment review status;
- refresh Pesapal sandbox status where configured;
- add payment review notes;
- view payment reconciliation status.

Restricted by design:

- cannot edit citizen identity records;
- cannot approve evidence;
- cannot edit audit logs;
- cannot edit integration logs;
- cannot activate live payments.

### NileGov SLA Supervisor

Responsible for service delivery timelines and escalations.

Allowed by design:

- view SLA rules;
- view SLA events;
- view escalated cases;
- reassign overdue cases;
- approve escalation outcomes;
- return cases to officers;
- monitor queue performance.

Restricted by design:

- cannot edit payment credentials;
- cannot edit audit logs;
- cannot alter integration logs;
- cannot change citizen identity details without admin authority.

### NileGov M&E Viewer

Responsible for executive and operational reporting visibility.

Allowed by design:

- view reporting snapshots;
- view service performance summaries;
- view workload summaries;
- view SLA compliance summaries;
- view payment summary metrics;
- view notification summary metrics.

Restricted by design:

- cannot edit service requests;
- cannot edit citizen profiles;
- cannot edit payments;
- cannot edit evidence;
- cannot edit audit or integration logs.

### NileGov MDA Admin

Responsible for service configuration and administrative oversight.

Allowed by design:

- manage service catalogue items;
- manage service configuration;
- manage queue and department settings;
- view operational reports;
- oversee service templates.

Restricted by design:

- cannot delete audit records;
- cannot delete integration simulation logs;
- cannot activate live third-party integrations without deployment approval.

### NileGov System Auditor

Responsible for independent review and traceability.

Allowed by design:

- view audit events;
- view integration simulation logs;
- view case history;
- view service request timeline;
- view evidence and payment status metadata.

Restricted by design:

- cannot edit audit events;
- cannot delete audit events;
- cannot edit integration simulation logs;
- cannot delete integration simulation logs;
- cannot alter operational records.

### NileGov System Manager

Responsible for controlled setup and runtime administration.

Allowed by design:

- configure roles;
- configure DocTypes;
- configure system settings;
- manage runtime deployment validation;
- run controlled migration/setup actions.

Restricted by policy:

- should not process ordinary citizen cases;
- should not be used as a daily operations role;
- should not bypass audit requirements.

## Sensitive DocType protection assumptions

The following records should be treated as sensitive:

- NileGov Citizen Profile
- NileGov Consent Record
- NileGov Evidence Document
- NileGov Payment Record
- NileGov Service Request
- NileGov SLA Event
- NileGov Escalation Record
- NileGov Audit Event
- NileGov Integration Simulation Log
- NileGov Reporting Snapshot
- NileGov Service Catalogue

## Immutable or protected records

The following should be read-only or highly restricted for ordinary users:

- NileGov Audit Event
- NileGov Integration Simulation Log
- submitted payment verification records
- submitted evidence review records
- closed service requests
- reporting snapshots after generation

## Permission principles

1. Least privilege by role.
2. No ordinary user can edit audit logs.
3. No ordinary user can edit integration simulation logs.
4. Payment officers cannot alter evidence decisions.
5. Records officers cannot verify payments.
6. M&E viewers cannot edit operational records.
7. System auditors can view but not modify sensitive logs.
8. Live integrations require explicit runtime approval.
9. `.env` secrets are never exposed through Desk roles.
10. Prototype disclaimers remain visible where needed.

## Runtime validation required

On Hetzner/Frappe runtime, validate:

- roles exist;
- role profiles can be created;
- users can be assigned role profiles;
- each role can access only intended DocTypes;
- ordinary users cannot modify audit logs;
- ordinary users cannot modify integration logs;
- payment users cannot modify evidence decisions;
- records users cannot modify payment verification;
- M&E viewers cannot edit operational records;
- System Auditor role is read-only for sensitive logs.

## Safe claims

It is safe to say:

- NileGov role and permission model is defined.
- Government-grade access-control assumptions are documented.
- Sensitive DocTypes are identified.
- Audit and integration logs are protected by design.
- Runtime Frappe permission validation remains pending.

## Claims to avoid

Do not claim:

- live MDA users are configured;
- production role assignment is complete;
- connected to a government identity provider;
- connected to NIRA, UGHub, NITA-U or URA;
- production permissions have been validated on a live host.

## Required disclaimer

“Prototype role and permission model only. Runtime Frappe permission validation remains pending.”
