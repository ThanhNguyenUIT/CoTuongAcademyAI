from copy import deepcopy
import json
import sqlite3

import pytest

import backend.app.knowledge.service as knowledge_service
from backend.app.knowledge.service import (
    DATA_PATH,
    KnowledgeValidationError,
    build_graph,
    canonical_position_key,
    list_openings,
    load_document,
    load_opening,
    validate_knowledge,
)
from backend.app.rules import xiangqi
from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def raw_opening():
    return load_document(DATA_PATH.read_text(encoding="utf-8"), DATA_PATH.suffix)


def test_yaml_and_json_import_and_schema_validation(raw_opening):
    assert validate_knowledge(raw_opening).opening_id == "cannon-vs-screen-horse"
    assert load_document(json.dumps(raw_opening), ".json")["opening_id"] == "cannon-vs-screen-horse"
    with pytest.raises(KnowledgeValidationError, match="Invalid YAML"):
        load_document("opening_id: [", ".yaml")
    with pytest.raises(KnowledgeValidationError, match="schema validation"):
        validate_knowledge({"opening_id": "incomplete"})


def test_two_move_orders_transpose_to_same_canonical_position():
    opening = load_opening()
    graph = build_graph(opening)
    line_a = opening.lines[0]
    line_b = opening.lines[1]
    assert line_a.moves_iccs != line_b.moves_iccs
    final_position = xiangqi.Position.from_fen(xiangqi.STARTING_FEN)
    for move in line_a.moves_iccs:
        final_position = xiangqi.apply_move(final_position, move)
    final_key = canonical_position_key(final_position.to_fen())
    final_a = next(item for item in graph.positions if item.position_key == final_key)
    shared = [position for position in graph.positions if set(position.incoming_lines) >= {line_a.id, line_b.id}]
    assert final_a.position_key == shared[-1].position_key
    assert len(shared) >= 2


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda raw: raw["lines"][0].update(source_refs=["missing-source"]), "missing sources"),
        (lambda raw: raw["lines"][0].update(moves_iccs=["z9z0"]), "illegal move"),
        (lambda raw: raw["lines"][0].update(moves_iccs=["b0c2", "b9c7", "c2b0", "c7b9"]), "cycle"),
        (lambda raw: raw["annotations"][0].update(position_key="not-a-position"), "unknown position"),
        (lambda raw: raw["lesson"]["exercises"][0].update(fen="bad fen"), "invalid FEN"),
        (lambda raw: raw["lesson"]["exercises"][0]["choices"][0].update(move_iccs="h9h8"), "offers illegal move"),
        (lambda raw: raw["lesson"]["exercises"][0]["choices"][0].update(counterplay_moves_iccs=["a0a9"]), "illegal counterplay move"),
    ],
)
def test_importer_rejects_unsourced_illegal_cyclic_or_orphan_data(raw_opening, mutate, message):
    altered = deepcopy(raw_opening)
    mutate(altered)
    with pytest.raises(KnowledgeValidationError, match=message):
        validate_knowledge(altered)


def test_experimental_content_is_never_in_published_catalog(raw_opening):
    assert list_openings() == []
    assert list_openings(include_experimental=True)[0]["review_status"] == "experimental"
    altered = deepcopy(raw_opening)
    altered["review_status"] = "draft"
    draft = validate_knowledge(altered)
    assert draft.review_status == "draft"


def test_opening_and_lesson_api_expose_graph_sources_and_versioned_experimental_content():
    assert client.get("/v1/openings").json() == []
    assert client.get("/v1/openings/cannon-vs-screen-horse").status_code == 404
    assert client.get("/v1/lessons/lesson-cannon-screen-horse-01").status_code == 404
    detail = client.get("/v1/openings/cannon-vs-screen-horse?include_experimental=true")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["opening"]["review_status"] == "experimental"
    assert len(payload["opening"]["lines"]) == 3
    assert payload["graph"]["positions"]
    shared = [node for node in payload["graph"]["positions"] if len(node["incoming_lines"]) > 1]
    assert shared
    branches = client.get(
        "/v1/openings/cannon-vs-screen-horse/branches",
        params={"position_key": shared[-1]["position_key"], "include_experimental": "true"},
    )
    assert branches.status_code == 200
    assert client.get("/v1/lessons/lesson-cannon-screen-horse-01?include_experimental=true").json()["review_status"] == "experimental"
    assert client.get("/v1/lessons/missing").status_code == 404


def test_opening_schema_migration_creates_unique_canonical_positions():
    migration = (DATA_PATH.parent.parent / "migrations" / "001_opening_knowledge.sql").read_text(encoding="utf-8")
    connection = sqlite3.connect(":memory:")
    connection.executescript(migration)
    connection.execute(
        "INSERT INTO positions(position_key, fen_canonical, side_to_move) VALUES (?, ?, ?)",
        ("key r", "fen", "r"),
    )
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO positions(position_key, fen_canonical, side_to_move) VALUES (?, ?, ?)",
            ("key r", "other-fen", "r"),
        )
    assert {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")} >= {
        "positions", "position_edges", "openings", "opening_lines", "annotations", "lessons", "exercises"
    }


def test_validated_opening_cache_invalidates_when_source_changes(tmp_path, monkeypatch):
    source = tmp_path / "course.yaml"
    source.write_text(DATA_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(knowledge_service, "DATA_PATH", source)
    original_validate = knowledge_service.validate_knowledge
    calls = 0

    def counted_validate(raw):
        nonlocal calls
        calls += 1
        return original_validate(raw)

    monkeypatch.setattr(knowledge_service, "validate_knowledge", counted_validate)
    knowledge_service.clear_opening_cache()
    first = knowledge_service.load_opening()
    first.name_vi = "caller mutation"
    second = knowledge_service.load_opening()
    assert second.name_vi != "caller mutation"
    assert calls == 1

    changed = source.read_text(encoding="utf-8").replace("0.1.0-experimental", "0.20.0-experimental")
    source.write_text(changed, encoding="utf-8")
    updated = knowledge_service.load_opening()
    assert updated.version == "0.20.0-experimental"
    assert calls == 2
