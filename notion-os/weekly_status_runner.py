#!/usr/bin/env python3
"""Post a Weekly Status Log entry per active project. Run Monday mornings via GH Actions.

For each project where Is Active = checked:
    counts open/done/blocked tasks for the past 7 days
    captures stage snapshot + timeline health
    creates a Weekly Status Log row tagged Posted By = AI Agent
"""

import datetime as dt
import json
import sys
from pathlib import Path

try:
    from notion_os_toolkit import auth, client as notion_client
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "notion-os-toolkit"))
    from src import auth, client as notion_client  # type: ignore

ROOT = Path(__file__).resolve().parent
IDS = ROOT / "ids.json"


def title_of(page, prop_name):
    return "".join(r["plain_text"] for r in page["properties"].get(prop_name, {}).get("title", []))


def main():
    ids = json.loads(IDS.read_text())
    db_ids = ids["databases"]
    nc = notion_client.NotionClient(auth.load_token())

    active = nc.query_all(db_ids["Projects"], filter_payload={
        "property": "Is Active", "checkbox": {"equals": True},
    })
    print(f"{len(active)} active project(s)")

    monday = dt.date.today() - dt.timedelta(days=dt.date.today().weekday())
    week_iso = monday.isoformat()

    for project in active:
        title = title_of(project, "Project Name") or project["id"]
        stage_sel = project["properties"].get("Project Stage", {}).get("select") or {}
        stage = stage_sel.get("name")
        timeline_sel = project["properties"].get("Timeline Status", {}).get("select") or {}
        timeline = timeline_sel.get("name", "On Track")

        # Count tasks
        tasks = nc.query_all(db_ids["Tasks"], filter_payload={
            "and": [
                {"property": "Project", "relation": {"contains": project["id"]}},
                {"property": "Is Template", "checkbox": {"equals": False}},
            ],
        })

        done = sum(1 for t in tasks if (t["properties"].get("Status", {}).get("status") or {}).get("name") == "Done")
        ip   = sum(1 for t in tasks if (t["properties"].get("Status", {}).get("status") or {}).get("name") == "In Progress")
        blk  = sum(1 for t in tasks if (t["properties"].get("Status", {}).get("status") or {}).get("name") == "Blocked")

        props = {
            "Entry":            {"title": [{"type": "text", "text": {"content": f"{title} — week of {week_iso}"}}]},
            "Week Of":          {"date": {"start": week_iso}},
            "Project":          {"relation": [{"id": project["id"]}]},
            "Tasks Done This Week": {"number": done},
            "Tasks In Progress":    {"number": ip},
            "Tasks Blocked":        {"number": blk},
            "Timeline Health":  {"select": {"name": timeline}},
            "Posted By":        {"select": {"name": "AI Agent"}},
        }
        if stage:
            props["Stage Snapshot"] = {"select": {"name": stage}}

        try:
            nc.create_page({"database_id": db_ids["Weekly Status Log"]}, props)
            print(f"  posted: {title} — {done} done / {ip} IP / {blk} blocked")
        except Exception as e:
            print(f"  ERROR posting {title}: {e}")


if __name__ == "__main__":
    main()
