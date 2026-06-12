#!/usr/bin/env python3
"""Validate the Shadow & Mirror homepage game manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public"
MANIFEST = PUBLIC / "game" / "shadow-mirror-game.v1.json"


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load_manifest() -> dict:
    try:
        return json.loads(MANIFEST.read_text())
    except json.JSONDecodeError as exc:
        fail(f"{MANIFEST}: invalid JSON at line {exc.lineno}: {exc.msg}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def ids_unique(items: list[dict], label: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = item.get("id")
        require(isinstance(item_id, str) and item_id, f"{label}: missing id")
        require(item_id not in seen, f"{label}: duplicate id {item_id}")
        seen.add(item_id)


def local_route_exists(href: str) -> bool:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        return True
    if not parsed.path.startswith("/"):
        return True
    path = parsed.path
    if path == "/":
        return (PUBLIC / "index.html").is_file()
    target = PUBLIC / path.lstrip("/")
    candidates = [
        target,
        target.with_suffix(".html") if target.suffix == "" else target,
        target / "index.html",
    ]
    return any(candidate.is_file() for candidate in candidates)


def validate_route(href: str, context: str) -> None:
    require(isinstance(href, str) and href, f"{context}: empty href")
    parsed = urlparse(href)
    if parsed.scheme:
        require(parsed.scheme in {"http", "https"}, f"{context}: unsupported external scheme {parsed.scheme}")
        require(parsed.netloc, f"{context}: external URL missing host")
        return
    require(local_route_exists(href), f"{context}: local route does not resolve: {href}")


def score_specs(manifest: dict) -> dict[str, dict]:
    specs = manifest.get("scoreDimensions", [])
    ids_unique(specs, "scoreDimensions")
    return {item["id"]: item for item in specs}


def clamp(specs: dict[str, dict], metric: str, value: int) -> int:
    spec = specs[metric]
    return max(spec["min"], min(spec["max"], value))


def effect_for(manifest: dict, evidence: dict, method: dict) -> dict:
    direct = manifest.get("effects", {}).get(f"{evidence['id']}:{method['id']}")
    if direct:
        return direct
    for fallback in manifest.get("defaultEffects", []):
        when = fallback.get("when", {})
        if when.get("otherwise"):
            return fallback["effect"]
        if when.get("evidenceKind") and when["evidenceKind"] != evidence.get("kind"):
            continue
        if when.get("methodIds") and method["id"] not in when["methodIds"]:
            continue
        return fallback["effect"]
    return {"scores": {}}


def apply_move(manifest: dict, specs: dict[str, dict], state: dict, evidence: dict, method: dict) -> None:
    require(state["actionsLeft"] > 0, f"fixture {state['fixture']}: no actions left")
    require(method["id"] not in state["usedMethods"], f"fixture {state['fixture']}: method reused: {method['id']}")
    effect = effect_for(manifest, evidence, method)
    state["actionsLeft"] -= 1
    state["usedMethods"].add(method["id"])
    for metric, delta in effect.get("scores", {}).items():
        state["scores"][metric] = clamp(specs, metric, state["scores"].get(metric, 0) + delta)
    for flag in effect.get("flags", []):
        state["flags"][flag] = True
    state["traceLength"] += 1


def rule_passes(state: dict, rule: dict) -> bool:
    if "metric" in rule:
        value = state["scores"].get(rule["metric"], 0)
        if rule["op"] == "gte":
            return value >= rule["value"]
        if rule["op"] == "lte":
            return value <= rule["value"]
        if rule["op"] == "eq":
            return value == rule["value"]
        fail(f"unknown rule op: {rule['op']}")
    if "flag" in rule:
        value = bool(state["flags"].get(rule["flag"]))
        if rule["op"] == "true":
            return value
        if rule["op"] == "false":
            return not value
        if rule["op"] == "eq":
            return value == bool(rule["value"])
        fail(f"unknown flag op: {rule['op']}")
    fail(f"victory rule missing metric or flag: {rule}")


def simulate_fixture(manifest: dict, specs: dict[str, dict], rooms: dict[str, dict], methods: dict[str, dict], fixture: dict) -> None:
    room = rooms.get(fixture.get("roomId"))
    require(room is not None, f"fixture {fixture.get('id')}: unknown room")
    require(room.get("state") == "playable", f"fixture {fixture['id']}: room is not playable")
    case = next((item for item in room.get("cases", []) if item["id"] == fixture.get("caseId")), None)
    require(case is not None, f"fixture {fixture['id']}: unknown case {fixture.get('caseId')}")
    evidence = {item["id"]: item for item in case.get("evidence", [])}
    state = {
        "fixture": fixture["id"],
        "actionsLeft": room.get("actionsPerCase", 5),
        "scores": dict(room.get("startingScores", {})),
        "flags": {},
        "usedMethods": set(),
        "traceLength": 0,
    }
    for move in fixture.get("moves", []):
        evidence_id = move.get("evidenceId")
        method_id = move.get("methodId")
        require(evidence_id in evidence, f"fixture {fixture['id']}: unknown evidence {evidence_id}")
        require(method_id in methods, f"fixture {fixture['id']}: unknown method {method_id}")
        apply_move(manifest, specs, state, evidence[evidence_id], methods[method_id])

    rules = room.get("victory", {}).get("all", [])
    solved = all(rule_passes(state, rule) for rule in rules)
    expected = fixture.get("expect", {})
    if "solved" in expected:
        require(solved == expected["solved"], f"fixture {fixture['id']}: solved={solved}, expected {expected['solved']}")
    if "traceLength" in expected:
        require(state["traceLength"] == expected["traceLength"], f"fixture {fixture['id']}: traceLength={state['traceLength']}, expected {expected['traceLength']}")
    for metric, expected_value in expected.get("scores", {}).items():
        require(state["scores"].get(metric) == expected_value, f"fixture {fixture['id']}: {metric}={state['scores'].get(metric)}, expected {expected_value}")


def validate_manifest(manifest: dict) -> None:
    require(manifest.get("schemaVersion") == 1, "schemaVersion must be 1")
    require(manifest.get("runtime", {}).get("defaultRoom"), "runtime.defaultRoom is required")
    specs = score_specs(manifest)

    methods_list = manifest.get("methods", [])
    ids_unique(methods_list, "methods")
    methods = {item["id"]: item for item in methods_list}

    rooms_list = manifest.get("rooms", [])
    ids_unique(rooms_list, "rooms")
    rooms = {item["id"]: item for item in rooms_list}
    require(manifest["runtime"]["defaultRoom"] in rooms, "runtime.defaultRoom must name a room")

    claim_status = manifest.get("claimStatus", {})
    records = manifest.get("records", {})

    for route_id, href in manifest.get("routes", {}).items():
        validate_route(href, f"routes.{route_id}")

    for record_id, record in records.items():
        require(record.get("title"), f"record {record_id}: missing normalized title")
        require("zenodoTitle" in record, f"record {record_id}: missing zenodoTitle")
        require("essayTitle" in record, f"record {record_id}: missing essayTitle")
        require(record.get("roomId") in rooms, f"record {record_id}: unknown room {record.get('roomId')}")
        for label, href in record.get("local", {}).items():
            if href is not None:
                validate_route(href, f"record {record_id}.local.{label}")
        doi = record.get("doi", {})
        require(doi.get("concept") and doi.get("current"), f"record {record_id}: missing DOI normalization")
        for entry in doi.get("records", []):
            validate_route(entry["url"], f"record {record_id}.doi.records")

    all_evidence_ids: set[str] = set()
    for room in rooms_list:
        require(room.get("recordId") in records, f"room {room['id']}: unknown recordId {room.get('recordId')}")
        require(room.get("claimStatus") in claim_status, f"room {room['id']}: unknown claimStatus")
        for link in room.get("links", []):
            validate_route(link["href"], f"room {room['id']}.links.{link.get('label')}")
        if room.get("state") == "playable":
            require(room.get("cases"), f"playable room {room['id']}: missing cases")
            for metric in specs:
                require(metric in room.get("startingScores", {}), f"room {room['id']}: startingScores missing {metric}")
            for rule in room.get("victory", {}).get("all", []):
                if "metric" in rule:
                    require(rule["metric"] in specs, f"room {room['id']}: victory uses unknown metric {rule['metric']}")
                    require(rule["op"] in {"gte", "lte", "eq"}, f"room {room['id']}: bad metric op {rule['op']}")
                elif "flag" in rule:
                    require(rule["op"] in {"true", "false", "eq"}, f"room {room['id']}: bad flag op {rule['op']}")
                else:
                    fail(f"room {room['id']}: victory rule missing target")
            for case in room.get("cases", []):
                ids_unique(case.get("evidence", []), f"room {room['id']} case {case.get('id')} evidence")
                for evidence in case.get("evidence", []):
                    all_evidence_ids.add(evidence["id"])
                    require(evidence.get("kind"), f"room {room['id']} case {case['id']} evidence {evidence['id']}: missing kind")

    for key, effect in manifest.get("effects", {}).items():
        require(":" in key, f"effect key must be evidence:method: {key}")
        evidence_id, method_id = key.split(":", 1)
        require(evidence_id in all_evidence_ids, f"effect {key}: unknown evidence id")
        require(method_id in methods, f"effect {key}: unknown method id")
        for metric in effect.get("scores", {}):
            require(metric in specs, f"effect {key}: unknown metric {metric}")

    for fallback in manifest.get("defaultEffects", []):
        for method_id in fallback.get("when", {}).get("methodIds", []):
            require(method_id in methods, f"defaultEffect {fallback.get('id')}: unknown method {method_id}")
        for metric in fallback.get("effect", {}).get("scores", {}):
            require(metric in specs, f"defaultEffect {fallback.get('id')}: unknown metric {metric}")

    fixtures = manifest.get("fixtures", [])
    ids_unique(fixtures, "fixtures")
    for fixture in fixtures:
        simulate_fixture(manifest, specs, rooms, methods, fixture)


def main() -> int:
    try:
        manifest = load_manifest()
        validate_manifest(manifest)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    rooms = len(manifest.get("rooms", []))
    fixtures = len(manifest.get("fixtures", []))
    print(f"Validated {MANIFEST.relative_to(ROOT)}: {rooms} rooms, {fixtures} fixtures, routes and replay predicates ok.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
