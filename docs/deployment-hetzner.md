# NileGov Stack Hetzner Single-Node Deployment Guide

This document details the deployment posture, configuration strategies, and security precautions for running the NileGov Stack on a basic single-node Hetzner VPS.

---

## Deployment Posture & Wording

> [!IMPORTANT]
> **Production & Deployment Wording Directive:**
> “The prototype is deployed on a basic Hetzner server for demonstration and technical evaluation. Production deployment for an MDA would require approved hosting, security review, sizing, monitoring, backup policy, disaster recovery planning and formal Government onboarding.”
>
> **Deployment Package Draft Warning:**
> “The Hetzner deployment package is a prototype deployment draft. It must be verified after the NileGov application exists, including site creation, migrations, worker queues, websocket behaviour, email notifications, backups and restore drill.”

---

## Single-Node Resource Decisions

Deploying on a basic, resource-constrained VPS (e.g. 2GB RAM, 1-2 vCPUs) requires strict resource allocations to prevent system out-of-memory (OOM) crashes.

### 1. Redis Cache vs. Queue Isolation Decision
Running Cache, Queue, and SocketIO under a single Redis instance with an LRU (Least Recently Used) eviction policy risks evicting critical task queues or active web sessions when cache requirements spikes. 

To solve this, we choose **Option A (Separate Lightweight Containers)**:
* **`redis-cache` Container:**
  * **Memory Limit:** 96MB.
  * **Eviction Policy:** `allkeys-lru` (safely drops cache data if the memory limit is hit).
* **`redis-queue` Container:**
  * **Memory Limit:** 64MB.
  * **Eviction Policy:** `noeviction` (guarantees that scheduled background jobs, emails, and notifications are never lost). If the limit is reached, writes block rather than losing data, signaling issues cleanly.
* **`redis-socketio` Container:** Shared with cache or queue depending on load, or isolated. In our compose configuration, we will split this into two separate Docker Redis containers: one for Cache/SocketIO and one for Queue.

*This separation will be applied to the docker-compose file during the deployment pass (Pass 14).*

### 2. Consolidated Background Workers
Running separate queue workers (short, default, long) in multiple Python containers consumes ~300-500MB of RAM. NileGov consolidates queue workers into a single process:
```bash
bench worker --queue short,default,long
```
* **Risk:** A long-running job (like report generation or heavy integration mock) can block the execution of short jobs (like SMS confirmation codes).
* **Mitigation:** Job runtimes must be audited. Any task taking >5 seconds must run asynchronously in background tasks, keeping the worker loop highly responsive.

---

## Security & Operations Safeguards

### 1. SSH Hardening & Lock-out Prevention
Automated host-setup scripts that disable password authentication and root login can permanently lock administrators out of their servers if SSH key configuration is incomplete.

**Mandatory Precautions implemented in `setup-host.sh`:**
* **Preflight SSH Key Verification:** The script checks for the existence of `/home/nilegov/.ssh/authorized_keys` and prints a warning.
* **Confirmation Prompt:** Administrators must explicitly approve disabling password authentication via a CLI confirmation.
* **Option to Skip:** SSH hardening steps can be skipped completely during initial script execution to allow the administrator to log in via the new deploy user first and test their key connection.

### 2. Backup & Restore Validation Drill
A backup script is not verified until a successful restore operation has been executed on a clean environment.

**Annual/Monthly Restore Drill Checklist:**
1. Execute `./scripts/backup.sh` to generate the encrypted GPG archive.
2. Transfer the archive to a clean, secondary test node or local docker staging container.
3. Run `./scripts/restore.sh` with the target file.
4. Verify:
   * The Frappe site loads without database errors.
   * Sample citizen profiles and service requests exist.
   * Attachment storage paths (evidence documents) are accessible.
   * Audit log timelines show consistent history.
