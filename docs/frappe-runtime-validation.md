# NileGov Stack — Pass 2B Runtime Validation Plan

This document details the step-by-step validation plan for **Pass 2B (Frappe Bench Validation)**. It establishes how to spin up a local or containerised bench site, install the app, execute database migrations, and verify runtime functionality.

---

## 1. Environment Initialization

To validate the custom app inside a running Frappe framework:
1. **Option A: Containerised Bench (Docker Compose):**
   * Deploy the configuration configurator and bench container defined under `deployment/`:
     ```bash
     docker compose -f deployment/docker-compose.yml up -d
     ```
2. **Option B: Host-level Bench Utility:**
   * If working on a server or workstation with `bench` installed:
     ```bash
     # Enter standard bench folder
     cd ~/frappe-bench
     # Link custom app
     bench get-app nilegov_stack /Users/robertsebunya/Documents/Nile_Gov/apps/nilegov_stack
     ```

---

## 2. App Installation & DB Migration

Run the following commands to install the app and migrate schema fields:
```bash
# Install the custom package onto our local test site
bench --site nilegov.local install-app nilegov_stack

# Run database migrations to compile the 13 custom NileGov table structures
bench --site nilegov.local migrate
```

---

## 3. Verify App Status

Confirm that the app is successfully installed:
```bash
# Check installed apps list
bench --site nilegov.local list-apps
```
*Expected Output:*
`nilegov_stack 0.0.1`

---

## 4. Verification Checkpoints

During Pass 2B, execution must satisfy these checks:

### Checkpoint A: Idempotent Patch Seeding
Verify that custom roles and default data are seeded into the database without duplication:
1. **Roles Seed:**
   Ensure `Citizen`, `Service Desk Officer`, `Supervisor`, `Registry Liaison Officer`, `MDA Leadership`, `MDA Administrator`, and `System Administrator` roles exist in the system database.
2. **Service Type Seed:**
   Ensure the `LOST_NATIONAL_ID` service type exists.
3. **SLA Rule Seed:**
   Ensure the default SLA Rule for `LOST_NATIONAL_ID` (response 24h, resolution 48h) exists.
4. **Idempotency verification:** Run the migration command again (`bench --site nilegov.local migrate`). Verify that duplicate roles or types are **not** created.

### Checkpoint B: DocType Loading & Schema Check
Verify that Frappe maps and exposes all 13 DocType fields correctly:
```bash
# Execute simple python verification script via bench CLI
bench --site nilegov.local execute nilegov_stack.tests.unit.test_runtime_schemas
```
This check should verify:
* Database inserts for `NileGov Citizen Profile` and `NileGov Service Request` resolve.
* Validation scripts are triggered (e.g. attempting to close a request without notes throws a validation error).
* Disclaimer validation throws an error if `disclaimer` or `response_message` fields omit the mock disclaimer wording.

### Checkpoint C: Row-Level Permission Queries
Verify that SQL conditions are dynamically appended to query filters:
* Log in as a `Citizen` user. Verify that running `frappe.get_list("NileGov Service Request")` returns only requests where `owner` matches the citizen's username.
* Log in as a `Service Desk Officer` user. Verify that querying returns only requests where `assigned_officer` matches the officer's username.
* Log in as a `Supervisor` user. Verify that querying returns escalated records or assigned cases.
* Verify that ordinary users are blocked from updating or editing `NileGov Audit Event` and `NileGov Integration Simulation Log` records.

### Checkpoint D: Frappe Test Suite
If the test runner is available, run the package integration tests:
```bash
bench --site nilegov.local run-tests --app nilegov_stack
```
