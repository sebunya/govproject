# NileGov Stack Scope & Known Limitations

This document lists the architectural, operational, and integration boundaries of the **NileGov Stack** prototype environment.

---

## Bounded Integration Scope

> [!WARNING]
> **Integration Safeguard Notice:**
> “Prototype simulation only. No live Government registry access.”
> Production integrations with official government systems require formal regulatory approval, information security audits, sizing metrics, network whitelistings, and signed Data Sharing Agreements with the relevant ministries.

NileGov Stack acts as a tracking, request validation, and workflow audit layer. It does **not** replace or connect live to:
1. **National Identification & Registration Authority (NIRA):** Identity checks are simulated locally. No real NIN registries are queried.
2. **Uganda Revenue Authority (URA):** Tax verification checkpoints are mocked. No financial tax accounts are validated.
3. **Uganda Registration Services Bureau (URSB):** Business profile verifications are mocked.
4. **UGHub (Uganda Government Integration Service Bus):** Connection interfaces are structured, but data flows are simulated inside mock handlers.
5. **National Payment Switches:** No real transaction processing takes place. Payment milestones are logged as simulated integration responses.

---

## Hosting & High-Availability Limitations

For initial testing and evaluation, the prototype is configured to run on a single-node VPS (Hetzner). This environment has the following architectural limitations:

1. **No High Availability (HA):**
   * If the host server crashes, all services go offline.
   * There are no active-active server configurations, autoscaling clusters, or automated node failovers configured.
2. **Resource Constraints:**
   * Run-time processes share CPU, RAM, and Disk space. High loads (e.g., intensive CSV/PDF file processing) can degrade web server responsiveness.
   * Background workers are restricted to save RAM. Bulk tasks queue sequentially.
3. **Log Eviction Risk:**
   * Cache and queue services share a Redis service block. LRU eviction must be monitored closely to ensure background jobs are not dropped.
4. **Manual Recovery Steps:**
   * Although backups are automated, restore operations are manually executed by running script instructions. The recovery window (RTO) is dependent on administrative manual setup.
5. **No sovereign cloud isolation:**
   * Demonstration is run on standard shared cloud hardware, not inside isolated sovereign government datacenters.
