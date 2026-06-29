#!/usr/bin/env python3
"""Render the Operations Cockpit onto the Operations Dashboard page.

Reads cockpit-spec.yaml, substitutes brand name from client.config.yaml,
calls cockpit_builder.render_cockpit on the Operations Dashboard section page.
"""

import json
import sys
from pathlib import Path

import yaml

try:
    from notion_os_toolkit import auth, client as notion_client, cockpit_builder
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "notion-os-toolkit"))
    from src import auth, client as notion_client, cockpit_builder  # type: ignore

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
SPEC = ROOT / "cockpit-spec.yaml"
IDS = ROOT / "ids.json"
CONFIG = REPO_ROOT / "client.config.yaml"


def render_template(text: str, ctx: dict) -> str:
    import re
    def sub(m):
        key = m.group(1).strip()
        cur = ctx
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return m.group(0)
        return str(cur)
    return re.sub(r"\{\{\s*([\w.]+)\s*\}\}", sub, text)


def main():
    config = yaml.safe_load(CONFIG.read_text())
    spec = yaml.safe_load(render_template(SPEC.read_text(), config))

    ids = json.loads(IDS.read_text())
    page_id = ids["sections"].get("Operations Dashboard")
    if not page_id:
        raise SystemExit("Operations Dashboard section not found in ids.json")

    nc = notion_client.NotionClient(auth.load_token())
    cockpit_builder.render_cockpit(nc, page_id, spec, wipe_existing=True)


if __name__ == "__main__":
    main()
