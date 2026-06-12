#!/usr/bin/env python3
"""Validate Shadow & Mirror game manifests."""

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


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def text(value: object, context: str) -> str:
    require(isinstance(value, str) and value.strip(), f"{context}: missing text")
    return value


def load_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)}: invalid JSON at line {exc.lineno}: {exc.msg}")


def ids_unique(items: list[dict], context: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = text(item.get("id"), f"{context}.id")
        require(item_id not in seen, f"{context}: duplicate id {item_id}")
        seen.add(item_id)


def local_route_exists(href: str) -> bool:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        return True
    if not href.startswith("/"):
        return True
    if href == "/":
        return (PUBLIC / "index.html").is_file()
    target = PUBLIC / href.lstrip("/")
    candidates = [
        target,
        target.with_suffix(".html") if target.suffix == "" else target,
        target / "index.html",
    ]
    return any(candidate.is_file() for candidate in candidates)


def validate_route(href: object, context: str) -> None:
    href = text(href, context)
    parsed = urlparse(href)
    if parsed.scheme:
        require(parsed.scheme in {"http", "https"}, f"{context}: unsupported scheme {parsed.scheme}")
        require(bool(parsed.netloc), f"{context}: external URL missing host")
    else:
        require(local_route_exists(href), f"{context}: local route does not resolve: {href}")


def metric_specs(manifest: dict) -> dict[str, dict]:
    specs = manifest.get("metrics", [])
    require(isinstance(specs, list) and specs, "v2 metrics are required")
    ids_unique(specs, "v2 metrics")
    out = {item["id"]: item for item in specs}
    for item in specs:
        require(isinstance(item.get("min"), int), f"metric {item['id']}: min must be int")
        require(isinstance(item.get("max"), int), f"metric {item['id']}: max must be int")
        require(item["min"] < item["max"], f"metric {item['id']}: min must be lower than max")
        require(isinstance(item.get("higherIsBetter"), bool), f"metric {item['id']}: higherIsBetter must be bool")
    return out


def clamp(specs: dict[str, dict], metric: str, value: int) -> int:
    if metric == "seals":
        return max(0, min(3, value))
    spec = specs.get(metric)
    require(spec is not None, f"unknown score metric {metric}")
    return max(spec["min"], min(spec["max"], value))


def validate_v1(manifest: dict) -> None:
    require(manifest.get("schemaVersion") == 1, "v1 schemaVersion must be 1")
    text(manifest.get("gameId"), "v1 gameId")
    text(manifest.get("title"), "v1 title")
    rooms = manifest.get("rooms", [])
    require(isinstance(rooms, list) and len(rooms) >= 4, "v1 rooms must include four rooms")
    ids_unique(rooms, "v1 rooms")
    for route_id, href in manifest.get("routes", {}).items():
        validate_route(href, f"v1 routes.{route_id}")
    for room in rooms:
        text(room.get("name"), f"v1 room {room.get('id')}.name")
        for link in room.get("links", []):
            validate_route(link.get("href"), f"v1 room {room['id']} link {link.get('label')}")


def validate_stage_choices(room: dict, stage_id: str) -> dict[str, dict]:
    stage = room.get("stages", {}).get(stage_id)
    require(isinstance(stage, dict), f"room {room['id']} stage {stage_id}: missing")
    for key in ("label", "question", "prompt", "depthTitle", "depth"):
        text(stage.get(key), f"room {room['id']} stage {stage_id}.{key}")
    if stage_id == "inspect":
        text(stage.get("guide"), f"room {room['id']} stage inspect.guide")
        return {}
    choices = stage.get("choices", [])
    require(isinstance(choices, list) and choices, f"room {room['id']} stage {stage_id}: choices required")
    ids_unique(choices, f"room {room['id']} stage {stage_id} choices")
    require(any(item.get("correct") is True for item in choices), f"room {room['id']} stage {stage_id}: needs a correct choice")
    out = {item["id"]: item for item in choices}
    for item in choices:
        require(isinstance(item.get("correct"), bool), f"room {room['id']} {stage_id}.{item['id']}: correct must be bool")
        text(item.get("cost"), f"room {room['id']} {stage_id}.{item['id']}.cost")
        if stage_id == "test":
            text(item.get("label"), f"room {room['id']} {stage_id}.{item['id']}.label")
        else:
            text(item.get("title"), f"room {room['id']} {stage_id}.{item['id']}.title")
        require(isinstance(item.get("effect", {}), dict), f"room {room['id']} {stage_id}.{item['id']}: effect must be object")
        if item.get("correct"):
            text(item.get("nextStage"), f"room {room['id']} {stage_id}.{item['id']}.nextStage")
        else:
            text(item.get("recoveryPrompt"), f"room {room['id']} {stage_id}.{item['id']}.recoveryPrompt")
    return out


def validate_room(room: dict, room_ids: set[str], specs: dict[str, dict]) -> None:
    for key in ("name", "script", "kind", "state", "roomNumber", "headline", "lede", "artifactLabel", "firstAction", "method", "claimNote"):
        text(room.get(key), f"room {room.get('id')}.{key}")
    require(room["state"] == "playable", f"room {room['id']}: v2 homepage rooms must be playable once unlocked")
    require(room["kind"] in {"human", "final-boss"}, f"room {room['id']}: invalid kind")
    for dep in room.get("unlockAfter", []):
        require(dep in room_ids, f"room {room['id']}: unknown unlock dependency {dep}")
    for label, href in room.get("routes", {}).items():
        validate_route(href, f"room {room['id']}.routes.{label}")

    starting = room.get("startingScores", {})
    require(isinstance(starting, dict), f"room {room['id']}: startingScores required")
    for metric in (*specs.keys(), "seals"):
        require(isinstance(starting.get(metric), int), f"room {room['id']}: startingScores.{metric} must be int")

    evidence = room.get("evidence", [])
    require(isinstance(evidence, list) and len(evidence) >= room.get("evidenceGoal", 2), f"room {room['id']}: evidence cards required")
    ids_unique(evidence, f"room {room['id']} evidence")
    require(sum(1 for item in evidence if item.get("correct") is True) >= room.get("evidenceGoal", 2), f"room {room['id']}: not enough correct evidence")
    for item in evidence:
        for key in ("tag", "title", "code", "text"):
            text(item.get(key), f"room {room['id']} evidence {item.get('id')}.{key}")
        require(isinstance(item.get("correct"), bool), f"room {room['id']} evidence {item['id']}: correct must be bool")
        require(isinstance(item.get("effect", {}), dict), f"room {room['id']} evidence {item['id']}: effect must be object")
        for metric in item.get("effect", {}):
            require(metric == "seals" or metric in specs, f"room {room['id']} evidence {item['id']}: unknown metric {metric}")

    for stage_id in ("inspect", "method", "test", "counter"):
        choices = validate_stage_choices(room, stage_id)
        for item in choices.values():
            for metric in item.get("effect", {}):
                require(metric == "seals" or metric in specs, f"room {room['id']} {stage_id}.{item['id']}: unknown metric {metric}")

    trace = room.get("trace", {})
    initial = trace.get("initial", [])
    done = trace.get("done", [])
    require(len(initial) == 3 and len(done) == 3, f"room {room['id']}: trace must have three steps")
    for index, value in enumerate(initial):
        text(value, f"room {room['id']} trace.initial[{index}]")
    for index, value in enumerate(done):
        done_text = text(value, f"room {room['id']} trace.done[{index}]")
        require(done_text.startswith("This is what Logan did at full scale:"), f"room {room['id']} trace.done[{index}] must reveal Logan method")

    result = room.get("result", {})
    text(result.get("title"), f"room {room['id']} result.title")
    text(result.get("body"), f"room {room['id']} result.body")
    links = result.get("links", [])
    require(isinstance(links, list) and links, f"room {room['id']}: result links required")
    for link in links:
        route = text(link.get("route"), f"room {room['id']} result link.route")
        require(route in room.get("routes", {}) or route in {"catalogue", "vault", "matrix", "genesis", "thesis", "corpus"}, f"room {room['id']}: unknown result route {route}")


def choice_for(room: dict, stage_id: str, choice_id: str) -> dict:
    choices = room["stages"][stage_id]["choices"]
    found = next((item for item in choices if item["id"] == choice_id), None)
    require(found is not None, f"fixture: unknown {stage_id} choice {choice_id} in {room['id']}")
    return found


def simulate_fixture(manifest: dict, specs: dict[str, dict], rooms: dict[str, dict], fixture: dict) -> None:
    room = rooms.get(fixture.get("roomId"))
    require(room is not None, f"fixture {fixture.get('id')}: unknown room")
    state = {
        "stage": "inspect",
        "scores": dict(room["startingScores"]),
        "selected": set(),
        "trace": 0,
    }

    def apply(effect: dict) -> None:
        for metric, delta in effect.items():
            state["scores"][metric] = clamp(specs, metric, state["scores"].get(metric, 0) + int(delta))

    evidence = {item["id"]: item for item in room["evidence"]}
    goal = room.get("evidenceGoal", 2)
    for move in fixture.get("moves", []):
        move_type = move.get("type")
        move_id = move.get("id")
        if move_type == "evidence":
            require(state["stage"] == "inspect", f"fixture {fixture['id']}: evidence after inspect stage")
            card = evidence.get(move_id)
            require(card is not None, f"fixture {fixture['id']}: unknown evidence {move_id}")
            state["selected"].add(move_id)
            apply(card.get("effect", {}))
            correct = sum(1 for item in evidence.values() if item.get("correct") and item["id"] in state["selected"])
            if correct >= goal:
                state["stage"] = "method"
        elif move_type == "method":
            require(state["stage"] == "method", f"fixture {fixture['id']}: method outside method stage")
            choice = choice_for(room, "method", move_id)
            apply(choice.get("effect", {}))
            if choice.get("correct"):
                state["trace"] += 1
                state["stage"] = choice["nextStage"]
        elif move_type == "test":
            require(state["stage"] == "test", f"fixture {fixture['id']}: test outside test stage")
            choice = choice_for(room, "test", move_id)
            apply(choice.get("effect", {}))
            if choice.get("correct"):
                state["trace"] += 1
                state["stage"] = choice["nextStage"]
        elif move_type == "counter":
            require(state["stage"] == "counter", f"fixture {fixture['id']}: counter outside counter stage")
            choice = choice_for(room, "counter", move_id)
            apply(choice.get("effect", {}))
            if choice.get("correct"):
                state["trace"] += 1
                state["stage"] = choice["nextStage"]
        else:
            fail(f"fixture {fixture['id']}: unknown move type {move_type}")

    expected = fixture.get("expect", {})
    if "stage" in expected:
        require(state["stage"] == expected["stage"], f"fixture {fixture['id']}: stage={state['stage']}, expected {expected['stage']}")
    if "trace" in expected:
        require(state["trace"] == expected["trace"], f"fixture {fixture['id']}: trace={state['trace']}, expected {expected['trace']}")
    for metric in ("confidence", "parsimony", "overfit", "seals"):
        if metric in expected:
            require(state["scores"].get(metric) == expected[metric], f"fixture {fixture['id']}: {metric}={state['scores'].get(metric)}, expected {expected[metric]}")


def validate_v2(manifest: dict) -> None:
    require(manifest.get("schemaVersion") == 2, "v2 schemaVersion must be 2")
    serialized = json.dumps(manifest)
    for forbidden in ("PhD", "dissertation"):
        require(forbidden not in serialized, f"v2 manifest contains forbidden public framing: {forbidden}")

    text(manifest.get("gameId"), "v2 gameId")
    text(manifest.get("contentVersion"), "v2 contentVersion")
    text(manifest.get("title"), "v2 title")
    for key in ("player", "game", "essays", "zenodo"):
        text(manifest.get("doctrine", {}).get(key), f"v2 doctrine.{key}")
    claim = manifest.get("claimStatus", {})
    require(claim.get("tone") == "honest-not-apologetic", "v2 claimStatus.tone must be honest-not-apologetic")
    text(claim.get("note"), "v2 claimStatus.note")

    for route_id in ("catalogue", "vault", "matrix", "genesis", "thesis", "corpus"):
        validate_route(manifest.get("routes", {}).get(route_id), f"v2 routes.{route_id}")

    specs = metric_specs(manifest)
    rooms_list = manifest.get("rooms", [])
    require(isinstance(rooms_list, list) and len(rooms_list) == 4, "v2 must have exactly four homepage rooms")
    ids_unique(rooms_list, "v2 rooms")
    room_ids = {room["id"] for room in rooms_list}
    rooms = {room["id"]: room for room in rooms_list}
    progression = manifest.get("progression", {})
    require(progression.get("humanRooms") == ["rongorongo", "proto-elamite", "indus"], "v2 humanRooms must preserve the three human-language ladder")
    require(progression.get("tutorialRooms") == progression["humanRooms"], "v2 tutorialRooms must be exactly rooms I-III")
    require(progression.get("finalBoss") == "whale-cadence", "v2 finalBoss must be whale-cadence")
    require(progression["finalBoss"] not in progression["tutorialRooms"], "v2 finalBoss must not be tutorialized")
    require(rooms["whale-cadence"].get("unlockAfter") == progression["humanRooms"], "whale room must unlock after all human rooms")
    require(rooms["whale-cadence"].get("role") == "public-gate", "whale room must be the public gate")
    for room_id in progression["tutorialRooms"]:
        require(rooms[room_id].get("role") == "tutorial-room", f"{room_id} must remain a tutorial room")

    for room in rooms_list:
        validate_room(room, room_ids, specs)

    fixtures = manifest.get("fixtures", [])
    require(isinstance(fixtures, list) and fixtures, "v2 fixtures are required")
    ids_unique(fixtures, "v2 fixtures")
    for fixture in fixtures:
        simulate_fixture(manifest, specs, rooms, fixture)


def main() -> int:
    try:
        v1 = load_manifest(V1_MANIFEST)
        v2 = load_manifest(V2_MANIFEST)
        validate_v1(v1)
        validate_v2(v2)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Validated {V1_MANIFEST.relative_to(ROOT)}: {len(v1.get('rooms', []))} rooms and routes ok.")
    print(f"Validated {V2_MANIFEST.relative_to(ROOT)}: {len(v2.get('rooms', []))} rooms, {len(v2.get('fixtures', []))} fixtures, whale boss gated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
