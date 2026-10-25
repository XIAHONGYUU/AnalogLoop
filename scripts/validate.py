#!/usr/bin/env python3
"""Validate the AnalogLoop repository before publishing.

Checks:
  - YAML / JSON syntax
  - JSON Schema correctness and sample validation
  - relative Markdown links and image targets
  - forbidden references to the original attachment or local absolute paths
  - presence and non-trivial size of generated diagrams
  - license and citation files
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
checks = 0


def ok(msg: str) -> None:
    global checks
    checks += 1
    print(f"  ok   {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"  FAIL {msg}")


def load_yaml(rel: str):
    path = ROOT / rel
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        ok(f"{rel} parses as YAML")
        return data
    except Exception as exc:  # noqa: BLE001
        fail(f"{rel}: {exc}")
        return None


def load_json(rel: str):
    path = ROOT / rel
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        ok(f"{rel} parses as JSON")
        return data
    except Exception as exc:  # noqa: BLE001
        fail(f"{rel}: {exc}")
        return None


def check_yaml_files() -> None:
    for rel in ["spec/tool-contract.yaml", "examples/two-stage-opamp/spec.yaml", "CITATION.cff"]:
        data = load_yaml(rel)
        if rel == "spec/tool-contract.yaml" and isinstance(data, dict):
            for key in ["contract", "version", "tools", "stop_conditions"]:
                if key not in data:
                    fail(f"spec/tool-contract.yaml missing key: {key}")
                else:
                    ok(f"tool contract has {key}")
            tools = data.get("tools") or []
            names = [t.get("name") for t in tools if isinstance(t, dict)]
            if len(names) != len(set(names)):
                fail("tool contract has duplicate tool names")
            else:
                ok(f"tool contract lists {len(names)} unique tools")


def check_schema() -> None:
    schema = load_json("spec/case-record.schema.json")
    if not schema:
        return
    try:
        Draft202012Validator.check_schema(schema)
        ok("case-record schema is a valid 2020-12 schema")
    except Exception as exc:  # noqa: BLE001
        fail(f"case-record schema invalid: {exc}")
        return
    sample = load_json("examples/sample-case.json")
    if sample:
        validator = Draft202012Validator(schema)
        errs = sorted(validator.iter_errors(sample), key=lambda e: e.path)
        if errs:
            for err in errs:
                fail(f"sample-case.json: {list(err.path)}: {err.message}")
        else:
            ok("sample-case.json validates")


LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def check_links() -> None:
    md_files = [ROOT / "README.md"]
    md_files += sorted((ROOT / "docs").glob("*.md"))
    for name in ["CONTRIBUTING.md", "DISCLAIMER.md", "THIRD_PARTY_NOTICES.md", "PUBLICATION_GATE.md"]:
        p = ROOT / name
        if p.exists():
            md_files.append(p)

    for md in md_files:
        text = md.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            raw = match.group(1).strip()
            if raw.startswith("<") and raw.endswith(">"):
                raw = raw[1:-1]
            target = raw.split("#", 1)[0].strip()
            if not target:
                continue
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                fail(f"{md.relative_to(ROOT)}: missing link target {target}")


FORBIDDEN = [
    "484388f2e6533ce8583fc25ec26fa9d82b5ab038b17804984685d72366571444",
    ".dsh/attachments",
    "attachments/v1/objects",
    "/home/zuoky",
]


def check_forbidden() -> None:
    extensions = {".md", ".yaml", ".yml", ".json", ".py", ".cff", ".txt", ".svg"}
    skip_dirs = {".git", ".venv", "__pycache__", "node_modules"}
    hits = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in extensions:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for needle in FORBIDDEN:
            if needle in text:
                fail(f"forbidden reference {needle!r} in {path.relative_to(ROOT)}")
                hits += 1
    if hits == 0:
        ok("no forbidden attachment or absolute-path references")


def check_assets() -> None:
    for name in ["architecture", "fast-verification", "mcu-mapping", "pdk-fastpath"]:
        for rel in [f"diagrams/{name}.svg", f"diagrams/png/{name}.png"]:
            path = ROOT / rel
            if not path.exists():
                fail(f"missing asset: {rel}")
            elif path.stat().st_size < 1000:
                fail(f"asset too small: {rel}")
            else:
                ok(f"asset {rel} ({path.stat().st_size} bytes)")


def check_licenses() -> None:
    lic = ROOT / "LICENSE"
    if not lic.exists():
        fail("missing LICENSE")
    else:
        head = lic.read_text(encoding="utf-8", errors="ignore")[:120]
        if "Attribution 4.0 International" not in head:
            fail("LICENSE does not look like CC BY 4.0")
        else:
            ok("LICENSE is CC BY 4.0")
    code = ROOT / "LICENSE-CODE"
    if not code.exists():
        fail("missing LICENSE-CODE")
    elif "MIT License" not in code.read_text(encoding="utf-8", errors="ignore"):
        fail("LICENSE-CODE does not look like MIT")
    else:
        ok("LICENSE-CODE is MIT")


def main() -> int:
    print("AnalogLoop validation")
    print("=" * 60)
    check_yaml_files()
    check_schema()
    check_links()
    check_forbidden()
    check_assets()
    check_licenses()

    print("=" * 60)
    if errors:
        print(f"{len(errors)} error(s), {checks} check(s) passed")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"all checks passed ({checks})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
