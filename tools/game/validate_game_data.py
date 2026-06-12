#!/usr/bin/env python3
"""Validate the Shadow & Mirror homepage game manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public"
V1_MANIFEST = PUBLIC / "game" / "shadow-mirror-game.v1.json"
V2_MANIFEST = PUBLIC / "game" / "homepage-game.v2.json"


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON at line {exc.lineno}: {exc.msg}")


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


def validate_manual(manifest: dict) -> None:
    manual = manifest.get("manual")
    require(isinstance(manual, dict), "manual is required")
    require(manual.get("label"), "manual.label is required")
    require(manual.get("subtitle"), "manual.subtitle is required")
    intro = manual.get("intro", {})
    require(intro.get("title") and intro.get("body"), "manual.intro title/body are required")

    path = manual.get("path", [])
    require(isinstance(path, list) and len(path) >= 2, "manual.path must contain at least two steps")
    for index, item in enumerate(path):
        require(isinstance(item, str) and item, f"manual.path[{index}] must be a non-empty string")

    axes = manual.get("axes", [])
    require(isinstance(axes, list) and len(axes) >= 2, "manual.axes must contain at least two axes")
    ids_unique(axes, "manual.axes")
    for axis in axes:
        require(axis.get("title"), f"manual axis {axis['id']}: missing title")
        cards = axis.get("cards", [])
        require(isinstance(cards, list) and cards, f"manual axis {axis['id']}: missing cards")
        ids_unique(cards, f"manual axis {axis['id']} cards")
        for card in cards:
            context = f"manual axis {axis['id']} card {card['id']}"
            require(card.get("tag"), f"{context}: missing tag")
            require(card.get("title"), f"{context}: missing title")
            require(card.get("body"), f"{context}: missing body")
            links = card.get("links", [])
            require(isinstance(links, list) and links, f"{context}: missing links")
            for link in links:
                require(link.get("label"), f"{context}: link missing label")
                validate_route(link.get("href"), f"{context} link {link.get('label')}")


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
    for route_id in ("thesis", "seal", "genesisJson", "sealSvg"):
        require(route_id in manifest.get("routes", {}), f"routes.{route_id} is required for Planisphere verification")
    validate_manual(manifest)

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


def require_text(value: object, context: str) -> str:
    require(isinstance(value, str) and value.strip(), f"{context}: missing text")
    return value


def validate_choices_v2(items: object, context: str) -> dict[str, dict]:
    require(isinstance(items, list) and items, f"{context}: choices are required")
    ids_unique(items, context)
    choices = {item["id"]: item for item in items}
    require(any(item.get("correct") is True for item in items), f"{context}: at least one correct choice is required")
    for item in items:
        require(isinstance(item.get("correct"), bool), f"{context}.{item['id']}: correct must be boolean")
        require_text(item.get("cost"), f"{context}.{item['id']}.cost")
        if item.get("correct"):
            require_text(item.get("nextStep"), f"{context}.{item['id']}.nextStep")
        else:
            require_text(item.get("recoveryPrompt"), f"{context}.{item['id']}.recoveryPrompt")
    return choices


def validate_homepage_manifest(manifest: dict) -> None:
    require(manifest.get("schemaVersion") == 2, "v2 schemaVersion must be 2")
    serialized = json.dumps(manifest)
    for forbidden in ("lcr.phd", "PhD", "dissertation"):
        require(forbidden not in serialized, f"v2 manifest contains forbidden public framing: {forbidden}")

    require_text(manifest.get("gameId"), "v2 gameId")
    require_text(manifest.get("contentVersion"), "v2 contentVersion")
    doctrine = manifest.get("doctrine", {})
    for key in ("player", "game", "essays", "zenodo"):
        require_text(doctrine.get(key), f"v2 doctrine.{key}")

    claim = manifest.get("claimStatus", {})
    require(claim.get("tone") == "honest-not-apologetic", "v2 claimStatus.tone must be honest-not-apologetic")
    require_text(claim.get("note"), "v2 claimStatus.note")

    routes = manifest.get("routes", {})
    for route_id in ("essay", "vault", "zenodo", "catalogue", "matrix", "genesis", "thesis"):
        require(route_id in routes, f"v2 routes.{route_id} is required")
    for route_id, href in routes.items():
        validate_route(href, f"v2 routes.{route_id}")

    rooms = manifest.get("rooms", [])
    require(isinstance(rooms, list) and len(rooms) >= 4, "v2 rooms must include the four locked rooms")
    ids_unique(rooms, "v2 rooms")
    playable = [room for room in rooms if room.get("state") == "playable"]
    require(len(playable) == 1 and playable[0].get("id") == "rongorongo", "v2 Rongorongo must be the only playable room")
    for room in rooms:
        require_text(room.get("name"), f"v2 room {room['id']}.name")
        require(room.get("state") in {"playable", "locked"}, f"v2 room {room['id']}: invalid state")
        require_text(room.get("method"), f"v2 room {room['id']}.method")
        for label, href in room.get("routes", {}).items():
            validate_route(href, f"v2 room {room['id']}.routes.{label}")

    runtime = manifest.get("runtime", {})
    require_text(runtime.get("mount"), "v2 runtime.mount")
    marks = runtime.get("acceptedMarks", {})
    require(marks.get("minUnique") == 2, "v2 acceptedMarks.minUnique must be 2")
    values = marks.get("values", [])
    require(isinstance(values, list) and len(values) >= 3, "v2 acceptedMarks.values must include all visible 730 marks")
    require(len(values) == len(set(values)), "v2 acceptedMarks.values must be unique")
    starting = runtime.get("startingScores", {})
    for metric in ("signal", "overfit"):
        require(isinstance(starting.get(metric), int), f"v2 runtime.startingScores.{metric} must be int")

    steps = manifest.get("steps", {})
    for step_id in ("notice", "twin", "test", "predict", "break", "open", "temptation"):
        step = steps.get(step_id, {})
        require(isinstance(step, dict), f"v2 steps.{step_id} is required")
        if step_id != "temptation":
            require_text(step.get("label"), f"v2 steps.{step_id}.label")
            require_text(step.get("question"), f"v2 steps.{step_id}.question")
            require_text(step.get("prompt"), f"v2 steps.{step_id}.prompt")
        require_text(step.get("depthTitle"), f"v2 steps.{step_id}.depthTitle")
        require_text(step.get("depth"), f"v2 steps.{step_id}.depth")
        require_text(step.get("announce"), f"v2 steps.{step_id}.announce")

    choices = manifest.get("choices", {})
    method_choices = validate_choices_v2(choices.get("method"), "v2 choices.method")
    prediction_choices = validate_choices_v2(choices.get("prediction"), "v2 choices.prediction")
    counter_choices = validate_choices_v2(choices.get("counter"), "v2 choices.counter")
    require(method_choices.get("calendar", {}).get("correct") is True, "v2 calendar method must be correct")
    require(prediction_choices.get("30", {}).get("correct") is True, "v2 30 prediction must be correct")
    require(counter_choices.get("keep", {}).get("correct") is True, "v2 keep counterexample must be correct")

    trace = manifest.get("trace", {})
    for key in ("count", "test", "counter"):
        require_text(trace.get("initial", {}).get(key), f"v2 trace.initial.{key}")
        done = require_text(trace.get("done", {}).get(key), f"v2 trace.done.{key}")
        require(done.startswith("This is what Logan did at full scale:"), f"v2 trace.done.{key} must reveal Logan's full-scale method")

    result = manifest.get("result", {})
    require_text(result.get("title"), "v2 result.title")
    require_text(result.get("body"), "v2 result.body")
    links = result.get("links", [])
    require(isinstance(links, list) and len(links) >= 4, "v2 result.links must route out of the game")
    for link in links:
        require_text(link.get("label"), "v2 result link label")
        route = require_text(link.get("route"), f"v2 result link {link.get('label')}.route")
        require(route in routes, f"v2 result link {link.get('label')}: unknown route {route}")

    fixtures = manifest.get("fixtures", [])
    ids_unique(fixtures, "v2 fixtures")
    for fixture in fixtures:
        simulate_homepage_fixture(manifest, fixture, method_choices, prediction_choices, counter_choices)


def phase_name(phase: int) -> str:
    return {0: "notice", 1: "test", 2: "predict", 3: "break", 4: "open"}[phase]


def simulate_homepage_fixture(
    manifest: dict,
    fixture: dict,
    method_choices: dict[str, dict],
    prediction_choices: dict[str, dict],
    counter_choices: dict[str, dict],
) -> None:
    runtime = manifest["runtime"]
    marks = set(runtime["acceptedMarks"]["values"])
    min_unique = runtime["acceptedMarks"]["minUnique"]
    state = {
        "phase": 0,
        "signal": runtime["startingScores"]["signal"],
        "overfit": runtime["startingScores"]["overfit"],
        "noise": 0,
        "tapped": set(),
        "trace": [],
    }

    def complete_count_if_ready() -> None:
        if state["phase"] == 0 and len(state["tapped"]) >= min_unique:
            state["phase"] = 1
            state["signal"] += 1
            state["trace"].append("count")

    for move in fixture.get("moves", []):
        move_type = move.get("type")
        if move_type == "noise":
            require(state["phase"] == 0, f"fixture {fixture['id']}: noise tap after notice phase")
            state["noise"] += 1
        elif move_type == "tap":
            mark = move.get("mark")
            require(mark in marks, f"fixture {fixture['id']}: unknown accepted mark {mark}")
            require(state["phase"] == 0, f"fixture {fixture['id']}: mark tap after notice phase")
            state["tapped"].add(mark)
            complete_count_if_ready()
        elif move_type == "choice":
            require(state["phase"] == 1, f"fixture {fixture['id']}: method choice outside test phase")
            choice = method_choices.get(move.get("id"))
            require(choice is not None, f"fixture {fixture['id']}: unknown method choice {move.get('id')}")
            if choice.get("correct"):
                state["phase"] = 2
            else:
                state["overfit"] += 1
        elif move_type == "prediction":
            require(state["phase"] == 2, f"fixture {fixture['id']}: prediction outside predict phase")
            choice = prediction_choices.get(move.get("id"))
            require(choice is not None, f"fixture {fixture['id']}: unknown prediction {move.get('id')}")
            if choice.get("correct"):
                state["phase"] = 3
                state["signal"] += 1
                state["trace"].append("test")
            else:
                state["overfit"] += 1
        elif move_type == "counter":
            require(state["phase"] == 3, f"fixture {fixture['id']}: counter choice outside break phase")
            choice = counter_choices.get(move.get("id"))
            require(choice is not None, f"fixture {fixture['id']}: unknown counter choice {move.get('id')}")
            if choice.get("correct"):
                state["phase"] = 4
                state["signal"] += 1
                state["overfit"] = max(0, state["overfit"] - 1)
                state["trace"].append("counter")
            else:
                state["overfit"] += 1
        else:
            fail(f"fixture {fixture['id']}: unknown move type {move_type}")

    expected = fixture.get("expect", {})
    if "step" in expected:
        require(phase_name(state["phase"]) == expected["step"], f"fixture {fixture['id']}: step={phase_name(state['phase'])}, expected {expected['step']}")
    for key in ("signal", "overfit", "noise"):
        if key in expected:
            require(state[key] == expected[key], f"fixture {fixture['id']}: {key}={state[key]}, expected {expected[key]}")
    if "trace" in expected:
        require(state["trace"] == expected["trace"], f"fixture {fixture['id']}: trace={state['trace']}, expected {expected['trace']}")


def main() -> int:
    try:
        v1_manifest = load_manifest(V1_MANIFEST)
        validate_manifest(v1_manifest)
        v2_manifest = load_manifest(V2_MANIFEST)
        validate_homepage_manifest(v2_manifest)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    v1_rooms = len(v1_manifest.get("rooms", []))
    v1_fixtures = len(v1_manifest.get("fixtures", []))
    v2_rooms = len(v2_manifest.get("rooms", []))
    v2_fixtures = len(v2_manifest.get("fixtures", []))
    print(f"Validated {V1_MANIFEST.relative_to(ROOT)}: {v1_rooms} rooms, {v1_fixtures} fixtures, routes and replay predicates ok.")
    print(f"Validated {V2_MANIFEST.relative_to(ROOT)}: {v2_rooms} rooms, {v2_fixtures} homepage fixtures and player contract ok.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
