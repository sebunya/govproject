# NileGov Stack Production Readiness Guide

This guide details the operational, security, and infrastructure requirements necessary to transition NileGov Stack from a single-node prototype to a production-grade sovereign government system.

---

## 1. Hosting Infrastructure & Sizing

To support national deployment for a Ministry, Department, or Agency (MDA), NileGov Stack must run in a clustered, high-availability private cloud or approved sovereign Government hosting datacenter.

### Recommended Production Target Sizing (per 100,000 citizens/year)
* **Application Nodes (Gunicorn/WebSockets):** 
  * 3x Virtual Machines (each 4 vCPUs, 8GB RAM).
  * Load balancer (e.g. F5 or clustered HAProxy) handling HTTPS termination.
* **Database Nodes (MariaDB Clustered):**
  * 3x Virtual Machines (each 8 vCPUs, 16GB RAM, SSD in RAID 10 configuration).
  * Active-active replication (Galera Cluster) or Primary-Replica failover.
* **Redis Cluster Nodes:**
  * 3x isolated nodes (2 vCPUs, 4GB RAM) separating Cache and Task Queues.
* **Storage Cluster:**
  * Dedicated S3-compatible Object Storage cluster (e.g. MinIO or cloud storage) with replication across multiple nodes.

---

## 2. Security & Compliance Review

Before deploying NileGov Stack inside a production Government network, a formal review is required:

1. **Information Security Audit:**
   * Run full static application security testing (SAST) and dynamic analysis (DAST).
   * Perform professional penetration testing on all public endpoints.
2. **Data Privacy Impact Assessment (DPIA):**
   * Review compliance under Uganda's **Data Protection and Privacy Act, 2019**.
   * Audit personal identifiable information (PII) handling, ensuring database encryption at rest (using MariaDB encrypted tables) and Transport Layer Security (TLS 1.3 only).
3. **Formal Data Sharing Agreements (DSAs):**
   * Sign formal DSAs with NIRA and URA for active, non-simulated database lookups.
   * Secure credential tokens and store them inside secure Hardware Security Modules (HSMs) or vault managers.

---

## 3. High Availability & Backup Policies

Production operations demand a strict SLA with minimal RPO (Recovery Point Objective) and RTO (Recovery Time Objective):

### Backup Retention Requirements
* **Database Dumps:** Hourly incremental write-ahead log backups, daily full backups. Retained for 7 years to meet government compliance guidelines.
* **System Files & Attachments:** Real-time object storage mirroring across multiple sites.
* **Encrypted Archives:** All backups must be encrypted at rest using keys managed by a central Government Key Management Service (KMS).

### Disaster Recovery (DR) Active Failover
* Set up a mirror disaster recovery site in a secondary physical datacenter location.
* Database logs must synchronize asynchronously to the DR node.
* RTO: < 15 minutes (with automated DNS failover).
* RPO: < 1 minute.

---

## 4. Government Onboarding Criteria

To onboard an MDA onto NileGov Stack:
1. **Onboarding Questionnaire:** Capture specific service workflow requirements, roles, SLA configurations, and reporting indicators.
2. **Registry Mapping:** Set up API mappings to the agency's existing databases or UGHub endpoints.
3. **Security Access Setup:** Provision secure VPN connections linking agency local area networks (LANs) to the hosting cluster.
4. **Staff Training:** Conduct training workshops for Service Desk Officers, Supervisors, and MDA Administrators.
