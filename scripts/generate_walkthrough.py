#!/usr/bin/env python3
"""Render docs/WALKTHROUGH.template.md → docs/WALKTHROUGH.md with client config values.

Uses Jinja2 if available, else falls back to simple {{ var }} substitution.
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "client.config.yaml"
TEMPLATE = ROOT / "docs" / "WALKTHROUGH.template.md"
OUT = ROOT / "docs" / "WALKTHROUGH.md"


def render_with_jinja(text: str, ctx: dict) -> str:
    from jinja2 import Template
    return Template(text).render(**ctx)


def render_simple(text: str, ctx: dict) -> str:
    """Fallback: {{ key.subkey }} substitution only."""
    def sub(m):
        key = m.group(1).strip()
        cur = ctx
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            elif isinstance(cur, list):
                try:
                    cur = cur[int(part)]
                except (ValueError, IndexError):
                    return m.group(0)
            else:
                return m.group(0)
        return str(cur)
    return re.sub(r"\{\{\s*([\w.]+)\s*\}\}", sub, text)


def main():
    if not CONFIG.exists():
        raise SystemExit(f"Missing {CONFIG}")
    if not TEMPLATE.exists():
        raise SystemExit(f"Missing {TEMPLATE}")

    config = yaml.safe_load(CONFIG.read_text())
    text = TEMPLATE.read_text()

    try:
        rendered = render_with_jinja(text, config)
    except ImportError:
        print("(Jinja2 not installed — falling back to simple substitution)")
        rendered = render_simple(text, config)

    OUT.write_text(rendered)
    print(f"Wrote {OUT}")
    print(f"Brand: {config['brand']['name']}")
    print(f"Client: {config['client']['name']}")


if __name__ == "__main__":
    main()
