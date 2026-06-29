#!/usr/bin/env python3
"""Add helper formulas + rollups to the provisioned DBs.

Run AFTER provision.py + after Tasks DB has its Dependencies self-relation.

Reads:
    helper_formulas.yaml — formula expressions + rollup specs
    ids.json             — DB IDs from provision.py
    ../client.config.yaml — for {{ invoice_due_days }} substitution
"""

import json
import sys
from pathlib import Path

import yaml

try:
    from notion_os_toolkit import auth, client as notion_client, helper_formulas
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "notion-os-toolkit"))
    from src import auth, client as notion_client, helper_formulas  # type: ignore

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
SPEC = ROOT / "helper_formulas.yaml"
IDS = ROOT / "ids.json"
CONFIG = REPO_ROOT / "client.config.yaml"


def render_template(text: str, ctx: dict) -> str:
    """Simple {{ var }} substitution. Avoids Jinja2 dependency for one-shot use."""
    import re
    def sub(m):
        key = m.group(1).strip()
        return str(ctx.get(key, m.group(0)))
    return re.sub(r"\{\{\s*([\w.]+)\s*\}\}", sub, text)


def main():
    config = yaml.safe_load(CONFIG.read_text())
    invoice_due_days = config["financials"]["invoice_due_days"]
    ctx = {"invoice_due_days": invoice_due_days}

    spec_text = render_template(SPEC.read_text(), ctx)
    spec = yaml.safe_load(spec_text)

    ids = json.loads(IDS.read_text())
    db_ids = ids["databases"]

    nc = notion_client.NotionClient(auth.load_token())

    # 1. Plain formulas
    print("\n== Plain formulas ==")
    formula_payload = {}
    for db_name, props in spec.get("formulas", {}).items():
        if db_name not in db_ids:
            print(f"  skip {db_name}: not in IDs")
            continue
        formula_payload[db_ids[db_name]] = props
    if formula_payload:
        helper_formulas.patch(nc, formula_payload)

    # 2. Rollups
    print("\n== Rollups ==")
    for db_name, rollup_props in spec.get("rollups", {}).items():
        if db_name not in db_ids:
            continue
        update = {}
        for prop_name, cfg in rollup_props.items():
            update[prop_name] = {
                "rollup": {
                    "relation_property_name": cfg["via"],
                    "rollup_property_name": cfg["target"],
                    "function": cfg["function"],
                }
            }
        print(f"  {db_name}: {list(update.keys())}")
        try:
            nc.update_database(db_ids[db_name], properties=update)
        except Exception as e:
            print(f"    ERROR: {e}")

    # 3. Post-rollup formulas (Completion %)
    print("\n== Post-rollup formulas ==")
    post_payload = {}
    for db_name, props in spec.get("post_rollup_formulas", {}).items():
        if db_name not in db_ids:
            continue
        post_payload[db_ids[db_name]] = props
    if post_payload:
        helper_formulas.patch(nc, post_payload)


if __name__ == "__main__":
    main()
