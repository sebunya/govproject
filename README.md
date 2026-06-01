# NileGov Stack — Citizen Service Operational Layer

**A Uganda-built operational layer for Government service delivery**

Submission to the Ministry of ICT and National Guidance Innovator Showcase · June 2026  
MDA: Mbarara District Local Government

---

## Quick Start (Demo Setup)

```bash
npm install            # install all dependencies
npm run seed           # wipe & re-seed DB to camera-ready state
npm run dev            # start API (port 3001) + UI (port 3000)
```

- **Citizen Portal:**   http://localhost:3000/portal?persona=citizen
- **Officer Desk:**     http://localhost:3000/desk?persona=officer
- **Supervisor Desk:**  http://localhost:3000/desk?persona=supervisor
- **Exec Dashboard:**   http://localhost:3000/dashboard?persona=leadership

---

## Demo Persona Switcher

A gold bar at the top of every screen switches personas without login screens.

| Persona | URL Parameter | Role |
|---------|--------------|------|
| Akello Sarah | `?persona=citizen` | Smallholder farmer / applicant |
| Tumusiime Robert | `?persona=officer` | District Agricultural Officer |
| Nakamya Grace | `?persona=supervisor` | Senior District Officer |
| Executive View | `?persona=leadership` | District Leadership dashboard |

---

## 13-Step Demo Workflow

1. Citizen portal landing page — "Apply for a Service"
2. Service catalogue — select Cooperative Registration & Agribusiness Permit
3. Enter NIN `CM93019100ABC1J` → Verify Identity (1.5s spinner + SIMULATED NIRA banner)
4. NIRA data auto-fills (read-only, lock icon)
5. Enter cooperative name + TIN → Verify Tax Status (1s spinner + SIMULATED URA banner)
6. Tick Data Protection & Privacy Act 2019 consent checkbox
7. Upload Cooperative Bylaws + Member Roster
8. Review & Submit → Confirmation with reference number + SLA commitment
9. Officer task queue shows new application with SLA countdown timers
10. Officer review interface: applicant details, SOP checklist, UGHub Integration Spine panel
11. Officer selects Approve → application routes to supervisor countersignature queue
12. Supervisor countersignature queue — Nakamya reviews Tumusiime's recommendation
13. Supervisor approves → citizen sees "Approved" status → rates service ★★★★★ → executive dashboard updates

---

## Technical Stack

- **Backend:** Node.js 22 + built-in `node:sqlite` + Express 4 + Multer
- **Frontend:** React 18 + Vite 5 + Tailwind CSS 3 + Recharts + React Query
- **Database:** SQLite — persists in `/server/data/nilegov.db`
- **Uploads:** stored in `/server/data/uploads/`
- No Docker. No authentication providers. No native compilation required.

---

## Simulated Integrations (all labelled on screen)

| Integration | Simulation |
|-------------|-----------|
| NIRA Identity API | Returns mock data for NIN `CM93019100ABC1J`. Production requires NITA-U Data Sharing Agreement. |
| URA Tax Clearance API | Returns "Compliant" status. Production requires URA system integration via NITA-U. |

