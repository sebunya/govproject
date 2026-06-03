# NileGov Stack QA Checklist

This document details the quality assurance tests, code checks, and pre-release gates executed before NileGov Stack versions are tagged or deployed.

---

## Pre-Release Quality Gates

All checks must pass `100%` before release tagging:

```text
┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│  Tier 1: Pure Unit     │ ──> │  Tier 2: Use Case      │ ──> │  Tier 3: Integrations  │
│  (pytest domain)       │     │  (pytest application)  │     │  (bench test db)       │
└────────────────────────┘     └────────────────────────┘     └────────────────────────┘
                                                                          │
┌────────────────────────┐     ┌────────────────────────┐                 │
│  Tier 5: Architecture  │ <── │  Tier 4: Permissions   │ <───────────────┘
│  (ast scans & regex)   │     │  (RBAC verification)   │
└────────────────────────┘     └────────────────────────┘
```

---

## 1. Automated Verification Checks

### Domain Logic (Pytest Unit)
* **Goal:** Core state rules validation.
* **Commands:** `pytest apps/nilegov_stack/nilegov_stack/tests/unit/`
* **Success Metric:** 100% pass, zero exceptions.

### Architecture Decoupling (AST Scan)
* **Goal:** Verifies that no imports of `frappe`, `requests`, `mariadb`, `redis` appear in the `domain/` directory.
* **Commands:** `pytest apps/nilegov_stack/nilegov_stack/tests/unit/test_domain_import_boundaries.py`
* **Success Metric:** 100% pass.

### Quality Scan (Branding & Secrets)
* **Goal:** Scans files to verify no prohibited prompt artifacts or hardcoded credential keys exist in the repository.
* **Commands:** `pytest apps/nilegov_stack/nilegov_stack/tests/architecture/test_no_forbidden_public_strings.py`
* **Success Metric:** 100% pass, zero occurrences of forbidden strings.

### Python Syntax Analysis
* **Goal:** Static code compilation validity check.
* **Commands:** `python -m py_compile $(find apps/nilegov_stack/ -name "*.py")`
* **Success Metric:** Zero syntax errors.

---

## 2. Manual Verification Checklist

### Repository hygiene
* Check that planning files (`implementation_plan.md`, `task.md`, `walkthrough.md`) exist at the **repository root**.
* Confirm that no local `.env` files are tracked in Git.
* Check that `.gitignore` correctly ignores IDE caches and Python caches.

### Security Disclaimers
* Confirm that simulated integration logs and screens are labeled:
  * `“Prototype simulation only. No live Government registry access.”`
* Check that documentation contains the basic Hetzner deployment disclaimers.

### Terminology Checklist
* Check that roles match the approved branding definitions.
* Ensure terms like "Registry Liaison Officer" are used in place of "NIRA Officer".
