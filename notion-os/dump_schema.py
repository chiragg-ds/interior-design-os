#!/usr/bin/env python3
"""Regenerate SCHEMA-REFERENCE.md + schema-reference.json from live workspace."""

import json
from pathlib import Path

import yaml

from notion_os_toolkit import auth, client as notion_client, schema_dump

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
IDS = ROOT / "ids.json"
CONFIG = REPO_ROOT / "client.config.yaml"


def main():
    config = yaml.safe_load(CONFIG.read_text())
    brand = config.get("brand", {}).get("name", "Workspace")

    ids = json.loads(IDS.read_text())
    nc = notion_client.NotionClient(auth.load_token())
    schema_dump.dump(nc, ids["databases"], out_dir=ROOT, brand_name=brand)


if __name__ == "__main__":
    main()
