# Interior Designer OS

> A Notion CRM + Operations OS opinionated for interior design studios.
> Provisioned in under 2 hours per client. Battle-tested by [Studio Nuvah](https://studionuvah.com).

[![Use this template](https://img.shields.io/badge/Use_this_template-blue?logo=github)](https://github.com/chiragg-ds/interior-design-os/generate)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What it ships

- **19 databases** wired with relations, rollups, and helper formulas
- **9 sections** with branded landing pages
- **Operations Cockpit** — single page with decision queue + KPI tiles + filtered views
- **Auto-seeded templates**: 44 handover items, ~25 task templates (dependency-wired), ~25 QC checklist items, ~29 drawing register entries
- **GitHub Actions** that replace the local LaunchAgent — auto-seed tasks hourly, post Weekly Status Log every Monday
- **Personalized walkthrough doc** (Jinja2 templated)
- **8 helper formulas** that collapse complex view filters into single-checkbox lookups

## Why

Studio Nuvah's full OS took 6 weeks to design + build the first time. With this template, the second client takes < 2 hours. Same opinionated structure, parameterized for the studio's brand, GST rate, fee stages, and client SLAs.

## Onboard a new client (90 minutes)

```bash
# 1. Clone from template
gh repo create chiragg-ds/<client-slug>-os --template chiragg-ds/interior-design-os --private
cd <client-slug>-os

# 2. Configure
cp client.config.example.yaml client.config.yaml
$EDITOR client.config.yaml      # Set brand, GST, fee stages, work scopes

cp .env.example .env
$EDITOR .env                    # Add NOTION_API_KEY + NOTION_ROOT_PAGE_ID

# 3. Install dependency
pip install pyyaml
git submodule add https://github.com/chiragg-ds/notion-os-toolkit external/notion-os-toolkit
pip install -e external/notion-os-toolkit

# 4. Provision
python3 notion-os/provision.py            # Sections + DBs + relations
python3 notion-os/add_helper_formulas.py  # Formulas + rollups
python3 notion-os/seed_all.py             # Templates loaded
python3 notion-os/build_cockpit.py        # Operations Dashboard rendered
python3 scripts/generate_walkthrough.py   # docs/WALKTHROUGH.md branded

# 5. Configure GitHub Actions
# Settings → Secrets → New repository secret → NOTION_API_KEY = <client token>
# Enable Actions for the repo. Workflows run automatically on schedule.

# 6. Manual UI steps (see docs/MANUAL-UI-STEPS.md)
# - Wire 9 linked DB views in Operations Cockpit
# - Add Seed Tasks / Seed Checklist buttons to Projects DB
# - Configure 10 native automations (Lead Won → Client+Project+Contract, etc.)
# - Set Finance permissions: Admin only
```

## Repo structure

```
interior-design-os/
├── client.config.example.yaml         # Per-client config (brand, fees, SLAs)
├── .env.example
├── notion-os/
│   ├── db-spec.yaml                   # 19-DB schema as data
│   ├── post_provision_relations.yaml  # Cross-DB relations (2nd pass)
│   ├── helper_formulas.yaml           # Checkbox formulas + rollups
│   ├── cockpit-spec.yaml              # Operations Dashboard layout
│   ├── provision.py                   # Driver: pages + DBs + relations
│   ├── add_helper_formulas.py         # Driver: formulas + rollups
│   ├── seed_all.py                    # Driver: load seed JSONs
│   ├── build_cockpit.py               # Driver: render Operations Dashboard
│   ├── dump_schema.py                 # Regenerate SCHEMA-REFERENCE.md
│   ├── autoseed_runner.py             # GH Actions worker — hourly task seeding
│   ├── weekly_status_runner.py        # GH Actions worker — Monday status posts
│   └── seeds/
│       ├── handover_items.json        # 44 items
│       ├── task_templates.json        # ~25 dependency-wired tasks
│       ├── relevant_checklist.json    # ~25 QC items
│       └── drawing_register.json      # ~29 drawings
├── docs/
│   ├── WALKTHROUGH.template.md        # Jinja2 — rendered per client
│   ├── MANUAL-UI-STEPS.md             # Manual UI steps the API can't do
│   ├── AUTOMATIONS-GUIDE.md
│   └── HANDOFF-CRITERIA.md
├── scripts/
│   └── generate_walkthrough.py        # Render walkthrough doc
└── .github/workflows/
    ├── tasks-autoseed.yml             # Hourly task auto-seed
    └── weekly-status.yml              # Monday 09:00 IST status post
```

## Customization

The template ships an opinionated default. Common per-client overrides:

| Override | Where to change |
|---|---|
| Brand name | `client.config.yaml` → `brand.name` |
| GST rate | `client.config.yaml` → `financials.gst_rate` |
| Fee stages | `client.config.yaml` → `financials.fee_stages` |
| Invoice due days | `client.config.yaml` → `financials.invoice_due_days` |
| Add new work scope | `notion-os/db-spec.yaml` → Projects.Work Scope.select.options |
| Extend task templates | `notion-os/seeds/task_templates.json` |
| Change Operations Dashboard | `notion-os/cockpit-spec.yaml` |

## Built by

[chiragg-ds](https://github.com/chiragg-ds) — operational systems for design studios.

Powered by [notion-os-toolkit](https://github.com/chiragg-ds/notion-os-toolkit) — a generic library you can use to build similar OSes for any vertical.

## License

MIT — see [LICENSE](LICENSE).
