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

import hashlib
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



UNIT = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "meg": 1e6, "": 1.0}


def parse_quantity(token: str):
    match = re.fullmatch(r"([0-9]*\.?[0-9]+)([a-zA-Z]*)", str(token).strip())
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2).lower()
    return value * UNIT.get(unit, 1.0)


def parse_netlist(rel: str):
    path = ROOT / rel
    devices = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("*") or stripped.startswith("."):
            continue
        parts = stripped.split()
        if not parts:
            continue
        head = parts[0][0].upper()
        if head == "M" and len(parts) >= 6:
            params = {}
            for token in parts[6:]:
                if "=" in token:
                    key, value = token.split("=", 1)
                    params[key.upper()] = value
            devices[parts[0]] = {"kind": "mos", "nodes": parts[1:5], "model": parts[5], "params": params}
        elif head in {"C", "R"} and len(parts) >= 4:
            devices[parts[0]] = {"kind": "passive", "nodes": parts[1:3], "model": head, "params": {"VALUE": parts[3]}}
    return devices


def check_semantics() -> None:
    roles_doc = load_yaml("spec/device-roles.yaml")
    manifest = load_yaml("examples/two-stage-opamp/roles.yaml")
    schema = load_json("spec/netlist-manifest.schema.json")
    if not roles_doc or not manifest or not schema:
        return
    role_ids = {item["id"] for item in roles_doc.get("roles", []) if isinstance(item, dict) and "id" in item}
    if not role_ids:
        fail("device-roles.yaml lists no roles")
        return
    ok(f"device role vocabulary has {len(role_ids)} roles")

    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        problems = sorted(validator.iter_errors(manifest), key=lambda e: e.path)
        if problems:
            for problem in problems:
                fail(f"roles.yaml: {list(problem.path)}: {problem.message}")
            return
        ok("roles.yaml validates against the manifest schema")
    except Exception as exc:
        fail(f"manifest schema invalid: {exc}")
        return

    netlist_file = ROOT / "examples/two-stage-opamp/netlist.cir"
    if not netlist_file.exists():
        fail("missing examples/two-stage-opamp/netlist.cir")
        return
    netlist = parse_netlist("examples/two-stage-opamp/netlist.cir")
    ok(f"netlist has {len(netlist)} M/C/R devices")

    digest = hashlib.sha256(netlist_file.read_bytes()).hexdigest()
    declared = manifest["netlist_sha256"].removeprefix("sha256:")
    if declared != digest:
        fail("roles.yaml netlist_sha256 does not match netlist.cir")
    else:
        ok("manifest hash matches netlist.cir")

    manifest_devices = set(manifest["devices"])
    if manifest_devices != set(netlist):
        missing = sorted(set(netlist) - manifest_devices)
        extra = sorted(manifest_devices - set(netlist))
        fail(f"device coverage mismatch: missing={missing}, extra={extra}")
    else:
        ok(f"all {len(netlist)} netlist devices are annotated")

    seen = {}
    block_ids = set()
    for block in manifest["blocks"]:
        bid = block["id"]
        role = block["role"]
        if bid in block_ids:
            fail(f"duplicate block id: {bid}")
        block_ids.add(bid)
        if role not in role_ids:
            fail(f"block {bid}: unknown role {role}")
        for dev in block["devices"]:
            if dev in seen:
                fail(f"device {dev} belongs to both {seen[dev]} and {bid}")
            seen[dev] = bid
            if dev not in netlist:
                fail(f"block {bid}: device {dev} not in netlist")
                continue
            entry = manifest["devices"].get(dev)
            if not entry:
                fail(f"block {bid}: device {dev} has no device entry")
                continue
            if entry["role"] != role:
                fail(f"device {dev}: role {entry['role']} != block role {role}")
            if entry["block"] != bid:
                fail(f"device {dev}: block {entry['block']} != {bid}")

        match = block.get("match", {})
        if match.get("same_wl"):
            values = []
            for dev in block["devices"]:
                params = netlist.get(dev, {}).get("params", {})
                w = parse_quantity(params.get("W", ""))
                l = parse_quantity(params.get("L", ""))
                if w is None or l is None:
                    fail(f"block {bid}: cannot check same_wl for {dev}")
                    continue
                values.append((round(w, 18), round(l, 18)))
            if len(set(values)) > 1:
                fail(f"block {bid}: same_wl violated ({values})")

        if role == "current_mirror" and "ratio" in block:
            ratios = []
            for dev in block["devices"]:
                params = netlist.get(dev, {}).get("params", {})
                w = parse_quantity(params.get("W", ""))
                l = parse_quantity(params.get("L", ""))
                if w and l:
                    ratios.append(w / l)
            if len(ratios) >= 2:
                actual = ratios[1] / ratios[0]
                target = block["ratio"]
                if abs(actual - target) > 0.01 * target:
                    fail(f"block {bid}: mirror ratio {actual:.3f} != declared {target}")

        if role in {"enable_switch", "adj_switch", "dummy"}:
            for dev in block["devices"]:
                entry = manifest["devices"].get(dev, {})
                if entry.get("tunable", True):
                    fail(f"device {dev}: {role} must be tunable: false")
                if role in {"enable_switch", "adj_switch"}:
                    if not entry.get("constraints", {}).get("digital"):
                        fail(f"device {dev}: {role} must declare digital: true")

    unannotated = set(manifest.get("unannotated", []))
    missing_entries = set(manifest["devices"]) - set(seen)
    if missing_entries:
        fail(f"devices not assigned to a block: {sorted(missing_entries)}")
    extra_netlist = set(netlist) - set(seen) - unannotated
    if extra_netlist:
        fail(f"netlist devices without role: {sorted(extra_netlist)}")
    if not missing_entries and not extra_netlist:
        ok("every netlist device has exactly one role block")


def check_assets() -> None:
    for name in ["architecture", "fast-verification", "mcu-mapping", "pdk-fastpath", "netlist-semantics", "area-aware-loop", "asst-execution"]:
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
    check_semantics()
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