# {{ brand.name }} — Notion OS Walkthrough

> A page-by-page guide to how the system works, what each page is for, what to do on it, and how everything fits together.
> Audience: {{ brand.name }} team. Written in plain English.

---

## 1. What this system does

{{ brand.name }} OS is one connected workspace inside Notion that runs the studio end-to-end. It replaces scattered WhatsApp messages, spreadsheets, Drive folders, and mental notes with a single source of truth where:

- Every **lead** is tracked from first contact to "Won" or "Lost".
- Every **project** has its own page with team, scope, stage, tasks, deliverables, materials, site logs, and handover checklist in one place.
- Every **contract**, **invoice**, **deliverable**, and **vendor interaction** is linked back to the project it belongs to.
- The system **tells you what needs attention today** — overdue invoices, deliverables waiting on client feedback, blocked tasks, leads to follow up on.
- Routine work (creating tasks for a new project, seeding QC checklists, computing invoice due dates, flagging SLA breaches) happens automatically.

You always start at the **Operations Dashboard**. Everything else hangs off it.

---

## 2. Studio defaults locked in by your contract

| Item | Value | Source |
|---|---|---|
| GST rate | {{ financials.gst_rate }}% | India tax law |
| Fee stages | {{ financials.fee_stages[0] }}% / {{ financials.fee_stages[1] }}% / {{ financials.fee_stages[2] }}% / {{ financials.fee_stages[3] }}% | Your client contract |
| Invoice payment due | {{ financials.invoice_due_days }} days | Your contract SLA |
| Client feedback SLA | {{ financials.client_feedback_sla_hours }} hours | Your contract SLA |
| Max design iterations | {{ financials.max_design_iterations }} per project | Contractual cap |
| Currency | {{ client.currency_symbol }} | Locale |

These values drive the auto-flag logic on the Operations Dashboard. Changing them later means changing the helper formulas — see "Schema updates" at the end of this doc.

---

## 3. The big picture — a project from start to finish

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  1. LEAD comes in (Instagram DM, referral, etc.)                        │
│      → Create row in CRM › Leads                                        │
│      → Stage = "Initial Contact"                                        │
│                                                                         │
│  2. MEETING booked → Stage = "Meeting Booked"                           │
│  3. PROPOSAL sent → Stage = "Proposal Sent"                             │
│  4. WON  → Stage = "Won"                                                │
│      → Automation creates: Client row, Project row, Contract row        │
│                                                                         │
│  5. ONBOARDING                                                          │
│      → Send Client Questionnaire                                        │
│      → Site visit logged in Activities                                  │
│      → Drawings start in Deliverables (drawing register)                │
│                                                                         │
│  6. PROJECT EXECUTION                                                   │
│      → Set Work Scope on Project                                        │
│      → System auto-seeds Tasks (scoped, dependency-wired)               │
│      → System auto-seeds Relevant Checklist (scoped QC items)           │
│      → Team works through tasks; Site Log daily; Materials tracked      │
│      → Stages: Consultation → Design → Flooring → Ceiling → Carpentry   │
│        → Furniture → Final Touches → Handover                           │
│                                                                         │
│  7. INVOICING ({{ financials.fee_stages[0] }}/{{ financials.fee_stages[1] }}/{{ financials.fee_stages[2] }}/{{ financials.fee_stages[3] }} % per stage)                                  │
│      → Each invoice auto-flagged Overdue if past Date + {{ financials.invoice_due_days }} days        │
│                                                                         │
│  8. HANDOVER                                                            │
│      → 44-item Handover Checklist                                       │
│      → Client signs off each section                                    │
│      → Project marked complete                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Workspace structure

```
{{ brand.name }} Space
│
├── 🧭 Operations Dashboard       ← Start here every morning
│
├── 👥 CRM
│   ├── Team Members
│   ├── Leads
│   ├── Clients
│   ├── Activities
│   ├── Meeting Notes
│   └── Client Questionnaire Responses
│
├── 🏗️ Projects
│   ├── Projects
│   ├── Site Log
│   ├── Materials
│   ├── Tasks
│   └── Weekly Status Log
│
├── 📑 Contracts
│   ├── Contracts
│   └── BOQ
│
├── 🎨 Deliverables
│   └── Deliverables
│
├── 💰 Finance  (Admin only)
│   └── Finance
│
├── ⚙️ Operations
│   ├── Vendors
│   ├── Contractors
│   └── Relevant Checklist
│
├── ✅ Handover
│   └── Handover Items
│
└── 📚 Templates
    └── Templates
```

---

## 5. Operations Dashboard

Open this first every morning. It shows:

**Decision Queue (4 cards):**
- Approvals waiting — deliverables in "Client Review" needing a client response
- Overdue invoices — past Date + {{ financials.invoice_due_days }} days, still Pending
- SLA breaches — deliverables past the {{ financials.client_feedback_sla_hours }}-hour feedback window
- Blocked tasks — any task marked Status = Blocked

**KPI tiles:** Active Projects, Tasks Open, Revenue MTD (Admin only), SLA Breaches

**Sections:**
- Active Projects board (grouped by Project Stage)
- This Week's Tasks
- Lead Follow-ups Due

Every filter on this page = single-checkbox lookup against a helper formula. Filters auto-recompute.

---

## 6. The 8 helper formulas

These checkboxes auto-compute on every row. You never check them manually — they're the system thinking for you.

| DB | Formula | Means |
|---|---|---|
| Deliverables | `Needs Client Approval` | Status = Client Review AND Requires Client Approval checked |
| Deliverables | `SLA Breach` | Issued > 4 days ago AND not yet Approved/Issued |
| Finance | `Invoice Due Date` | Date + {{ financials.invoice_due_days }} days |
| Finance | `Is Overdue` | Invoice past Date+{{ financials.invoice_due_days }} days, still Pending |
| Finance | `Is Revenue MTD` | Payment Received this calendar month |
| Projects | `Is Active` | Stage ≠ Handover AND Client Sign-off unchecked |
| Tasks | `Is Open` | Status ≠ Done AND not a template |
| Tasks | `Due This Week` | Open AND Deadline within next 7 days |
| Leads | `Needs Follow-up` | Next Action Date past AND Stage ∉ {Won, Lost} |

---

## 7. Daily / Weekly / Monthly rituals

**Every morning (5 min):** Open Operations Dashboard → clear Decision Queue → check "This Week's Tasks".

**Every evening (5 min):** Site Supervisor logs Site Log entry. Update task Status changes.

**Every Monday (15 min):** Weekly review. AI Agent posts Weekly Status Log per active project. Review Active Projects board.

**Every handover (2-4h):** Walk site with team → verify 44 Handover Items → walk with client → sign-off → final invoice → mark Project Client Sign-off = checked.

**Every month:** Reconcile Finance. Review Vendor / Contractor ratings. Update template versions.

---

## 8. Permissions

| Section | Admin | Manager | Contributor |
|---|---|---|---|
| CRM | ✅ | ✅ | View linked only |
| Projects | ✅ | ✅ | ✅ |
| Contracts | ✅ | ✅ | ❌ |
| Deliverables | ✅ | ✅ | ✅ |
| Finance | ✅ | ❌ | ❌ |
| Operations | ✅ | ✅ | ✅ |
| Handover | ✅ | ✅ | ✅ |
| Templates | ✅ | ✅ | View only |

---

## 9. Auto-seeding (how new project tasks appear automatically)

1. The Tasks DB + Relevant Checklist DB contain template rows (`Is Template = checked`), tagged with `Applicable Scopes`.
2. When you set a new project's **Work Scope** and **Tasks Status = Not Seeded**:
   - A background script (GitHub Actions, hourly) sees the flag
   - Filters templates by `Applicable Scopes contains <project's Work Scope> OR "all"`
   - Creates task rows on that project, copying Action / Category / Stage
   - Re-wires Dependencies via the Template Group lookup
   - Flips `Tasks Status = Seeded`
3. Same pattern runs for Relevant Checklist.

Set scope → walk away 1 hour → tasks appear ready to assign.

---

## 10. Schema updates

If you ever need to change a select option, add a property, or modify a formula:

1. Make the change in Notion UI.
2. Regenerate the schema reference:
   ```bash
   python3 notion-os/dump_schema.py
   ```
3. The updated `SCHEMA-REFERENCE.md` is the source of truth for any future filter, view, or formula authoring.

---

## 11. When something doesn't work

| Problem | Likely cause | Fix |
|---|---|---|
| Set Work Scope but no tasks appeared | GitHub Actions not running | Check repo Actions tab; run "Tasks Autoseed" workflow manually |
| Dashboard view shows wrong rows | Filter using stale property name | Regenerate SCHEMA-REFERENCE.md; recheck filter |
| Invoice never marked Overdue | Status field blank | Set Status = Pending; Invoice Due Date will compute |
| Task says "🔒 Blocked — 0/0" but should be ready | Dependencies relation empty | Open task; if empty, Ready should say ✅ |

---

## 12. Glossary

- **DB** — Database. A Notion structured table.
- **Relation** — A field linking one row to another row in a different DB.
- **Rollup** — A field aggregating values from related rows.
- **Formula** — A computed field (like a spreadsheet formula).
- **Helper formula** — Pattern: push complex view filters into a single checkbox formula on the DB.
- **Template row** — A row with `Is Template = checked`. Blueprint, never appears in live views.
- **Auto-seed** — The script that copies templates to a project based on Work Scope.
- **SLA** — Service Level Agreement. {{ brand.name }} has a {{ financials.client_feedback_sla_hours }}h client feedback SLA and a {{ financials.invoice_due_days }}-day invoice payment SLA.

---

For technical issues, regenerate `SCHEMA-REFERENCE.md` and check current state against this doc.

— Built for {{ brand.name }} by [Chirag Studio](https://github.com/chiragg-ds).
