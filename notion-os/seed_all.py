#!/usr/bin/env python3
"""Load all template seeds into the provisioned DBs.

Run AFTER provision.py + add_helper_formulas.py.

Idempotent guard: checks if templates already exist (Is Template = true count > 0)
and skips if so. Pass --force to re-seed.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from notion_os_toolkit import auth, client as notion_client, seeder
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "notion-os-toolkit"))
    from src import auth, client as notion_client, seeder  # type: ignore

ROOT = Path(__file__).resolve().parent
SEEDS = ROOT / "seeds"
IDS = ROOT / "ids.json"

SEED_PLAN = [
    # (seed_file, target_db_name, title_property)
    ("handover_items.json",      "Handover Items",      "Item Title"),
    ("drawing_register.json",    "Deliverables",        "Deliverable Name"),
    ("task_templates.json",      "Tasks",               "Task Action"),
    ("relevant_checklist.json",  "Relevant Checklist",  "Item Name"),
]


def has_templates(client, db_id) -> bool:
    res = client.query_all(db_id, filter_payload={
        "property": "Is Template",
        "checkbox": {"equals": True},
    })
    return len(res) > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="Re-seed even if templates exist")
    args = ap.parse_args()

    ids = json.loads(IDS.read_text())
    db_ids = ids["databases"]
    nc = notion_client.NotionClient(auth.load_token())

    for seed_file, db_name, title_prop in SEED_PLAN:
        if db_name not in db_ids:
            print(f"SKIP {seed_file}: {db_name} not in IDs")
            continue
        db_id = db_ids[db_name]
        path = SEEDS / seed_file
        if not path.exists():
            print(f"SKIP {seed_file}: file missing")
            continue

        print(f"\n== {db_name} from {seed_file} ==")

        # Only seed templates check for Tasks + Relevant Checklist
        if db_name in ("Tasks", "Relevant Checklist") and not args.force:
            if has_templates(nc, db_id):
                print(f"  templates already exist — skip (use --force to override)")
                continue

        created = seeder.seed_from_json(nc, db_id, title_prop, path)

        # Rewire Task Dependencies after seeding
        if db_name == "Tasks":
            print(f"\n== Rewire Task Dependencies ==")
            seeder.rewire_relations_by_group(
                nc, created,
                group_property="Template Group",
                depends_property="Depends On Groups",
                relation_property="Dependencies",
            )


if __name__ == "__main__":
    main()
