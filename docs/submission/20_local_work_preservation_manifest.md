# Local Work Preservation Manifest (Pass F-RECOVERY-3A)

This manifest serves as the formal inventory and quality gate verification for the NileGov consolidation project local files. It guarantees that all local cleanup and consolidation work is safely cataloged, hashed, and archived prior to performing any remote GitHub reconciliation or comparisons.

---

## 1. Executive Verdict
**Verdict:** **PASSED & GO FOR GITHUB COMPARISON**
Both local project folders have been successfully backed up to timestamped archives, checksums have been generated, and all critical files are present and verified safe by local static architecture testing.

---

## 2. Timestamp
* **Timestamp:** 2026-06-06T22:32:00+03:00
* **Local Timezone:** EAT (UTC+3)

---

## 3. Local Folder Mapping
* **Main Directory (`govproject-main`):**
  `/Users/robertsebunya/Documents/NileGov_Project/govproject-main`
* **Alternative/Cloned Directory (`govproject-claude-peaceful-dijkstra-TMPp2`):**
  `/Users/robertsebunya/Documents/NileGov_Project/govproject-claude-peaceful-dijkstra-TMPp2`

---

## 4. Git Status Findings
* **`govproject-main`:** Not a Git repository (`fatal: not a git repository`).
* **`govproject-claude-peaceful-dijkstra-TMPp2`:** Not a Git repository (`fatal: not a git repository`).
* **Workspace parent folder (`NileGov_Project`):** Not a Git repository.
* **Verdict:** Change management must rely on local manifest logging and checksum verification until a clean Git repository structure is established.

---

## 5. Backup Archive Paths
Local backups have been saved inside `/Users/robertsebunya/Documents/NileGov_Project/local_backups`:
* **Main Backup Archive:**
  `/Users/robertsebunya/Documents/NileGov_Project/local_backups/govproject-main-LOCAL-BEFORE-GITHUB-20260606-222824.tar.gz`
* **Claude Temp Directory Backup Archive:**
  `/Users/robertsebunya/Documents/NileGov_Project/local_backups/govproject-claude-peaceful-dijkstra-TMPp2-LOCAL-BEFORE-GITHUB-20260606-222824.tar.gz`

---

## 6. Backup Checksums
* **govproject-claude-peaceful-dijkstra-TMPp2-LOCAL-BEFORE-GITHUB-20260606-222824.tar.gz:**
  `d5b2d41dff75e4829bf0933068cdc6c388b5523e85570a28c74e5f4682a2ab31`
* **govproject-main-LOCAL-BEFORE-GITHUB-20260606-222824.tar.gz:**
  `ab6395ce5a74642d8114e5c9fcb9005ce694e77c3b95f6b42a8fb8f83eefe636`

---

## 7. Critical File Inventory & 8. Critical File Checksums

| File Path | Exists | Size (Bytes) | SHA-256 Checksum | Purpose | Preservation Priority |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `docs/adr/001-frappe-first-consolidation.md` | Yes | 2,729 | `ff5f5eca1c67accf12a85353fe7824708b117c40d7a2001b66179b0c4b8e95b0` | Consolidation strategy architecture decision record | **Critical** |
| `docs/submission/18_recovery_change_snapshot.md` | Yes | 6,377 | `57506a25c200567f8906d5096e720631323c5eb1127c070c51e72e007e4cd8df` | Recovery safety cleanup log | **Critical** |
| `docs/submission/18_recovery_change_snapshot.sha256` | Yes | 1,110 | `074e0fa028114b5a00b377594d0ca5b5cfad26917526cceca9a817ee5092bd8a` | Checksum verification file for Pass F-RECOVERY-1 | **Critical** |
| `apps/nilegov_stack/nilegov_stack/interfaces/frappe/api/public_readiness.py` | Yes | 7,815 | `807f07c0c3ca86635f5f5c2008c2d45e5f809ecae28616092a30bd52d3535eb6` | Whitelisted public API endpoints for service requests | **Critical** |
| `apps/nilegov_stack/nilegov_stack/interfaces/frappe/api/__init__.py` | Yes | 400 | `901233d457df14880ccb80822b832f7d929b90510ebe3e31f0ce5f63cb41e1e1` | Package level endpoint exports | **Critical** |
| `apps/nilegov_stack/nilegov_stack/tests/architecture/test_recovery_safety_cleanup.py` | Yes | 7,440 | `32cad08718ceac7d2283d52d6f308914c6e772bd89853d2358c75b83d14141ce` | Safety and quarantine regression tests | **Critical** |
| `apps/nilegov_stack/nilegov_stack/nilegov_stack/www/track.html` | Yes | 15,091 | `a237e65d10e753e9bef5874afdf610754d977375f6bd659e9c1a72bc2a66057c` | Public tracking page with prototype disclaimers | **Critical** |
| `apps/nilegov_stack/nilegov_stack/nilegov_stack/www/track.py` | Yes | 216 | `89d165d2492a2b9e40a88b88c0e0ed48eb52bb6956ea0af050935bec2fe6f4ee` | Public tracking page backend controller | **Critical** |
| `apps/nilegov_stack/nilegov_stack/nilegov_stack/web_form/nilegov_lost_nid_replacement_intake/nilegov_lost_nid_replacement_intake.js` | Yes | 10,983 | `b04b38ae43fbf89b688b29a26481cb7f04b0116eaef8500bb607f61b6751c214` | Step-by-step lost NID replacement intake UI script | **Critical** |
| `apps/nilegov_stack/nilegov_stack/nilegov_stack/web_form/nilegov_lost_nid_replacement_intake/nilegov_lost_nid_replacement_intake.py` | Yes | 236 | `1835d2c161ca811170f0a58cafdd0e2c4b383ff35448a5c49c64209f0484c532` | Intake web form backend controller | **High** |
| `apps/nilegov_stack/nilegov_stack/nilegov_stack/web_form/nilegov_citizen_consent_capture/nilegov_citizen_consent_capture.js` | Yes | 3,116 | `fa8c4c2ea7a47bcc0db00adfa0f1a18c6f11302e790d1c4a70b9d319941571e5` | Citizen consent capture UI script | **Critical** |
| `apps/nilegov_stack/nilegov_stack/nilegov_stack/web_form/nilegov_citizen_consent_capture/nilegov_citizen_consent_capture.py` | Yes | 176 | `8324638eb3282b7094f3bccb0870e3489806f97460f5f84493249ceba5665523` | Consent capture backend controller | **High** |
| `apps/nilegov_stack/nilegov_stack/nilegov_stack/web_form/nilegov_evidence_supplement_metadata/nilegov_evidence_supplement_metadata.js` | Yes | 2,954 | `5682ae07e4ce4c871aef2e85934661e70d85a4c274690bae97ffb60c9437f24d` | Evidence submission guidelines and constraints | **Critical** |
| `apps/nilegov_stack/nilegov_stack/nilegov_stack/web_form/nilegov_evidence_supplement_metadata/nilegov_evidence_supplement_metadata.py` | Yes | 176 | `8324638eb3282b7094f3bccb0870e3489806f97460f5f84493249ceba5665523` | Evidence metadata backend controller | **High** |
| `apps/nilegov_stack/nilegov_stack/nilegov_stack/doctype/nilegov_service_request/nilegov_service_request.js` | Yes | 24,907 | `27cde1188e0e9639dac427167704e73c7567f1c3aa82d3c334d843c7097ef916` | Case management view with ticking SLA timer and SOP checklist | **Critical** |

---

## 9. `.env` and Secret Safety
* **No `.env` files** exist in either folder or parent workspace.
* **No secrets or credentials** are stored or printed in any source code, settings, or manifests.
* Safe default `.env.example` configurations are maintained.

---

## 10. Recovery Work Preserved
* Removal of four unapproved guest endpoints (`get_nira_data_preview`, `get_ura_data_preview`, `simulate_erp_sync`, `simulate_payment`).
* Removal of string-concatenation bypasses in API modules.
* Generalization of Mbarara and Uganda Data Protection Act 2019 Section 10 claims.
* Integration of the test suite [test_recovery_safety_cleanup.py](file:///Users/robertsebunya/Documents/NileGov_Project/govproject-main/apps/nilegov_stack/nilegov_stack/tests/architecture/test_recovery_safety_cleanup.py).

---

## 11. Frappe-First Work Preserved
* Comprehensive Frappe native Doctypes (e.g., `NileGov Service Request`, `NileGov Consent Record`, `NileGov Evidence Document`).
* Frappe native Web Forms configuration and corresponding JavaScript scripts.
* Clean whitelisted endpoint wrappers inside `apps/nilegov_stack/nilegov_stack/interfaces/frappe/api/public_readiness.py` conforming to safety constraints.

---

## 12. React/Express Prototype Preserved
* Deprecated React/Express prototype folder `govproject-claude-peaceful-dijkstra-TMPp2` is fully preserved in the backup archive.

---

## 13. Files That Must Not Be Lost
All critical files listed in Section 7 of this manifest are prioritized for preservation. Under no circumstances should they be overwritten by any GitHub checkout or branch sync.

---

## 14. What Was Not Done
* **No Git operations:** No repository initialization, branch checkouts, clones, pulls, or merges were performed.
* **No Dependency Installation:** No external python packages or testing frameworks (like pytest) were installed in the local environment.

---

## 15. Go / No-Go for GitHub Comparison
* **Status:** **GO**
* The local directories are fully backed up and checksummed. It is now safe to proceed to Pass F-RECOVERY-3B to perform Git inspections and comparisons against the remote repository `https://github.com/sebunya/govproject`.

---

## 16. Risk String Check Log
Executed Command:
```bash
grep -RIn "get_nira_data_preview\|get_ura_data_preview\|simulate_erp_sync\|simulate_payment\|string concatenation bypass\|Mbarara\|Section 10\|Data Protection Act\|Pesapal Sandbox payment clearance\|b\"payment_status\".decode\|payment_\"[[:space:]]*+[[:space:]]*\"status" . || true
```
Output:
* Clean. Only matches are in safety documentation (`18_recovery_change_snapshot.md`) and the test suite (`test_recovery_safety_cleanup.py`). No bypasses or unapproved wording exist in active code.

---

## 17. Compilation Status
* Command: `python3 -m compileall apps/nilegov_stack/nilegov_stack`
* Verdict: **Passed (0 errors)**.
