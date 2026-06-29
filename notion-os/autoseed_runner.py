#!/usr/bin/env python3
"""Find projects with Tasks Status = Not Seeded AND Work Scope set, seed tasks.

Designed to run from GitHub Actions hourly. Also doubles as the engine the
local LaunchAgent used to run.
"""

import json
from pathlib import Path

from notion_os_toolkit import auth, client as notion_client, seeder

ROOT = Path(__file__).resolve().parent
IDS = ROOT / "ids.json"
TASK_TEMPLATES = ROOT / "seeds" / "task_templates.json"
CHECKLIST_TEMPLATES = ROOT / "seeds" / "relevant_checklist.json"


def find_projects_needing_seed(client, projects_db_id: str, status_prop: str):
    return client.query_all(projects_db_id, filter_payload={
        "property": status_prop,
        "select": {"equals": "Not Seeded"},
    })


def get_work_scope(project_row: dict) -> str | None:
    sel = project_row["properties"].get("Work Scope", {}).get("select")
    return sel["name"] if sel else None


def seed_tasks_for_project(client, tasks_db_id: str, project_id: str, work_scope: str):
    templates = json.loads(TASK_TEMPLATES.read_text())
    rows_to_create = []
    for t in templates:
        scopes = t["properties"]["Applicable Scopes"]["multi_select"]
        if work_scope not in scopes and "all" not in scopes:
            continue
        row = dict(t)
        row["properties"] = dict(t["properties"])
        row["properties"]["Is Template"] = {"checkbox": False}
        row["properties"]["Project"] = {"relation": [project_id]}
        rows_to_create.append(row)

    if not rows_to_create:
        print(f"  no matching templates for scope={work_scope}")
        return 0

    print(f"  seeding {len(rows_to_create)} tasks for scope={work_scope}")
    created = seeder.seed_rows(client, tasks_db_id, "Task Action", rows_to_create)
    seeder.rewire_relations_by_group(
        client, created,
        group_property="Template Group",
        depends_property="Depends On Groups",
        relation_property="Dependencies",
    )
    return len(created)


def main():
    ids = json.loads(IDS.read_text())
    db_ids = ids["databases"]
    projects_db = db_ids["Projects"]
    tasks_db = db_ids["Tasks"]

    nc = notion_client.NotionClient(auth.load_token())
    pending = find_projects_needing_seed(nc, projects_db, "Tasks Status")
    print(f"Found {len(pending)} project(s) with Tasks Status = Not Seeded")

    for project in pending:
        scope = get_work_scope(project)
        title = "".join(
            r["plain_text"] for r in project["properties"].get("Project Name", {}).get("title", [])
        ) or project["id"]
        print(f"\nProject: {title}")
        if not scope:
            print("  no Work Scope set — skip")
            continue
        seed_tasks_for_project(nc, tasks_db, project["id"], scope)
        nc.update_page(project["id"], properties={
            "Tasks Status": {"select": {"name": "Seeded"}},
        })
        print("  flipped Tasks Status → Seeded")


if __name__ == "__main__":
    main()
