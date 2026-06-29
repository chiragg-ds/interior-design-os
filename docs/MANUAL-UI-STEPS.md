# Manual Notion UI Steps

Stuff the Notion API cannot do — must be configured by an Admin in the Notion UI.

---

## 1. Operations Cockpit linked views (~10 min)

The `notion-os/build_cockpit.py` script wrote WIRE HERE callouts onto the Operations Dashboard page. Each callout names the DB, filter, sort, and group-by spec. Replace each callout with an actual linked DB view:

1. Click in the callout → delete the callout block.
2. Type `/linked` → choose "Linked view of database".
3. Pick the named DB.
4. Apply the filter / group / sort spec from the callout.
5. Save.

Repeat for all 4 Decision Queue slots, 4 KPI tiles, and 3 sections.

---

## 2. Tasks DB activation buttons (~5 min)

In Projects DB, add two **Button** properties:

**Seed Tasks button:**
- Click + → Button property
- Name: `Seed Tasks`
- Action: Edit pages → `Tasks Status` = `Not Seeded`

**Seed Checklist button:**
- Same flow
- Name: `Seed Checklist`
- Action: Edit pages → `Checklist Status` = `Not Seeded`

Clicking either button on a project row flips the flag; GitHub Actions (hourly) picks it up and seeds.

---

## 3. Native automations (~30 min)

Open each DB → top-right ⚡ Automations → + New automation.

| Trigger | Action |
|---|---|
| Lead › Lead Stage = Won | Create row in Clients (link via Won Client); Create row in Projects (link via Client); Create row in Contracts (link via Client + Project) |
| Projects › Work Scope is set | Set Tasks Status = Not Seeded; Set Checklist Status = Not Seeded |
| Contracts › Contract Status = Signed | Create Activity row (Type = Approval, Title = "Contract signed") |
| Deliverables › Status = Client Review | If Issued Date empty, set Issued Date = today |
| Finance › Status = Received | Move project to next stage (if applicable) |
| Tasks › Status = Done | (optional) Check rollups to advance Project Stage |
| Handover Items › Client Sign-off checked | Update Activity log |
| Materials › Status contains "Installed" | Auto-flag for Site Log entry |
| Projects › Project Stage = Handover | (optional) Trigger handover checklist setup notification |

---

## 4. My Tasks linked views on role dashboards

Each role dashboard has a `## My Tasks` heading + placeholder callout. Replace each with a linked DB view of Tasks DB filtered:

| Dashboard | Filter |
|---|---|
| Admin / Owner | `Assignee = me AND Status != Done` |
| Design | `Assignee = me AND Task Category in (Design Iteration, Client Approval) AND Status != Done` |
| Site Ops | `Assignee = me AND Task Category in (Civil Works, MEP, Carpentry, Snagging) AND Status != Done` |

---

## 5. Permissions — Finance restricted to Admin

- Open Finance section page → Share menu
- Remove non-Admin users / groups
- Confirm: an Admin sees Finance, a Manager does not

Test by impersonation: log in as a Manager-level account, verify Finance section is hidden.

---

## 6. Per-project default page template

- Open Projects DB → ▾ next to New → Edit template (default)
- Inside the template: type `/linked` → Tasks → filter `Project contains current page`, group by Task Category, sort by Deadline
- Repeat for Deliverables, Handover Items
- Save template

Every new project page now shows its own tasks / deliverables / handover.

---

## 7. Verification

After completing all of the above:

- [ ] Create test project with Work Scope = Modular Kitchen
- [ ] Wait ~1 hour (or trigger workflow manually); confirm Tasks Status flipped to Seeded
- [ ] Open the test project → Tasks linked view shows ~15-20 tasks
- [ ] Pick a Carpentry task → confirm Dependencies populated with Civil Works tasks
- [ ] Mark a dependency Done → confirm Ready formula updates
- [ ] Each role dashboard shows My Tasks linked view
- [ ] Operations Dashboard shows all 9 wired views
- [ ] Finance section hidden from non-Admin accounts

When all checks pass — handoff complete.
