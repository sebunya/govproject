# NileGov Stack Runtime Handover Pack

This document is for the systems engineer or developer who will deploy and run the NileGov Stack on a working container host or native server.

---

## 1. Technical Requirements

* **Preferred Runtime Environment:** Linux VM (Ubuntu 22.04 LTS or Rocky Linux 9) with Docker and Docker Compose installed.
* **Alternative Runtime Environment:** macOS or Windows machine running **Docker Desktop** (which starts the virtual machine daemon automatically).
* **Native Host Caution:** A native setup is possible but discouraged unless the host has `redis-server`, MariaDB (`mysql`), `yarn`, and the `bench` CLI already installed. Running native setups on Python 3.14+ is untested; Python 3.10 to 3.12 is recommended for Frappe v15.

---

## 2. Docker Deployment Steps

Navigate to the repository root directory and execute:

```bash
# 1. Start the Gunicorn, Redis, and Database services in detached mode
docker compose -f deployment/docker-compose.yml up -d

# 2. Verify all containers are running and healthy
docker compose -f deployment/docker-compose.yml ps

# 3. Create the bench site nilegov.local
docker compose -f deployment/docker-compose.yml exec backend bench new-site nilegov.local --mariadb-root-password admin --admin-password admin --no-mariadb-socket

# 4. Install the custom app on nilegov.local
docker compose -f deployment/docker-compose.yml exec backend bench --site nilegov.local install-app nilegov_stack

# 5. Run migrations (this executes patches, including seed_demo_records)
docker compose -f deployment/docker-compose.yml exec backend bench --site nilegov.local migrate
```

---

## 3. Database Seed & Lifecycle Validation

Verify that 9 requests are seeded in the database.
```bash
# Execute sql command within container
docker compose -f deployment/docker-compose.yml exec backend bench --site nilegov.local mariadb -e "SELECT name, status, nin, reference_no FROM \`tabNileGov Service Request\`"
```
Ensure you see records `req_pass3_001` through `req_pass3_009` corresponding to the 9 lifecycle statuses.

---

## 4. Expected Browser Desk Paths

When the containers are active, access the Desk at `http://nilegov.local:8000/app` using:
* **Username:** `Administrator`
* **Password:** `admin` (or using the seeded user `officer_sebunya`).

* **Workspace Dashboard:** `http://nilegov.local:8000/app/nilegov-case-operations`
* **Request List View:** `http://nilegov.local:8000/app/nilegov-service-request`
* **Case Record Detail:** `http://nilegov.local:8000/app/nilegov-service-request/req_pass3_001`

---

## 5. Troubleshooting Notes

* **Permission issues:** If Gunicorn workers fail to boot, check file permissions on `apps/nilegov_stack`. The folder must be readable and writable by the docker user (mount mapped in `docker-compose.yml`).
* **Port Conflict:** If port `8000` or `3306` is already in use by host services, modify host port mapping configurations in `deployment/docker-compose.yml`.
* **Host Resolution:** Add `127.0.0.1 nilegov.local` to `/etc/hosts` to access the site via browser.

---

## 6. Screenshot Specifications & Target Directory

After verifying UI actions, capture screenshots and save them to:
`docs/submission_screenshots/pass6b_runtime/`

Filename registry:
1. `01_workspace.png` — Dash workspace.
2. `02_service_request_list.png` — Active queues.
3. `03_case_detail_submitted.png` — Fictional intake.
4. `04_simulated_nira_action.png` — NIRA dropdown.
5. `05_simulated_nira_result.png` — NIRA Matched success toast.
6. `06_simulated_payment_action.png` — Payment button.
7. `07_simulated_payment_result.png` — Verified success toast.
8. `08_sla_overdue.png` — Overdue badge.
9. `09_audit_timeline.png` — Timeline history log.
10. `10_management_metrics.png` — Operations report update.
