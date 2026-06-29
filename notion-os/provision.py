#!/usr/bin/env python3
"""Provision the Interior Designer OS into a Notion workspace.

Reads:
    db-spec.yaml                  — 9 sections + 19 DB schemas
    post_provision_relations.yaml — cross-DB relations (second pass)
    ../client.config.yaml         — per-client config (root page id, etc.)
    .env                          — NOTION_API_KEY

Writes:
    ids.json                      — created/found page + DB IDs (canonical reference)

Re-runnable. Idempotent. Existing pages and DBs are reused; missing properties added.
"""

import json
import os
import sys
from pathlib import Path

# Allow either pip-installed notion_os_toolkit or path-injected sibling repo
try:
    from notion_os_toolkit import auth, client as notion_client, provisioner
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "notion-os-toolkit"))
    from src import auth, client as notion_client, provisioner  # type: ignore

import yaml

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
DB_SPEC = ROOT / "db-spec.yaml"
RELATIONS = ROOT / "post_provision_relations.yaml"
CONFIG = REPO_ROOT / "client.config.yaml"
IDS_OUT = ROOT / "ids.json"


def load_config() -> dict:
    if not CONFIG.exists():
        raise SystemExit(
            f"Missing {CONFIG}. Copy client.config.example.yaml to client.config.yaml and edit."
        )
    return yaml.safe_load(CONFIG.read_text())


def expand_env(spec_text: str) -> str:
    """Substitute ${VAR} references with os.environ values."""
    import re
    return re.sub(r"\$\{(\w+)\}", lambda m: os.environ.get(m.group(1), ""), spec_text)


def first_pass_provision(nc, config) -> dict:
    spec_text = DB_SPEC.read_text()
    root_id = config["notion"]["root_page_id"]
    if root_id == "REPLACE_WITH_ROOT_PAGE_ID":
        raise SystemExit("Set notion.root_page_id in client.config.yaml")
    os.environ["NOTION_ROOT_PAGE_ID"] = root_id
    spec_text = expand_env(spec_text)
    spec = yaml.safe_load(spec_text)
    return provisioner.provision(nc, spec, out_path=IDS_OUT)


def second_pass_relations(nc, ids: dict) -> None:
    relations = yaml.safe_load(RELATIONS.read_text())["relations"]
    db_ids = ids["databases"]

    for source_db, props in relations.items():
        if source_db not in db_ids:
            print(f"  skip {source_db}: not in provisioned IDs")
            continue
        source_id = db_ids[source_db]
        update_props = {}
        for prop_name, cfg in props.items():
            target_db = cfg["database"]
            if target_db not in db_ids:
                print(f"  skip {source_db}.{prop_name}: target {target_db} missing")
                continue
            target_id = db_ids[target_db]
            relation_spec: dict = {"database_id": target_id}
            dual = cfg.get("dual")
            if dual:
                relation_spec["dual_property"] = {"synced_property_name": dual["property"]}
            else:
                relation_spec["single_property"] = {}
            update_props[prop_name] = {"relation": relation_spec}

        if update_props:
            print(f"  {source_db}: adding {list(update_props.keys())}")
            try:
                nc.update_database(source_id, properties=update_props)
            except Exception as e:
                print(f"    ERROR: {e}")


def main():
    config = load_config()
    nc = notion_client.NotionClient(auth.load_token())

    print("== First pass: pages + DBs ==")
    ids = first_pass_provision(nc, config)

    print("\n== Second pass: cross-DB relations ==")
    second_pass_relations(nc, ids)

    print(f"\nIDs written to {IDS_OUT}")
    print(f"Sections: {len(ids['sections'])}  DBs: {len(ids['databases'])}")


if __name__ == "__main__":
    main()
