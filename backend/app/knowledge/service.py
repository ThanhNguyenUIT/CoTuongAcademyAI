from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from backend.app.knowledge.schemas import (
    GraphEdge,
    GraphPosition,
    Lesson,
    OpeningDetail,
    OpeningGraph,
    OpeningKnowledge,
)
from backend.app.rules import xiangqi

DATA_PATH = Path(__file__).with_name("data") / "cannon-vs-screen-horse.yaml"
PUBLISHED = {"published"}
VISIBLE_WITH_EXPERIMENTAL = PUBLISHED | {"experimental"}


class KnowledgeValidationError(ValueError):
    pass


def load_document(raw: str, suffix: str) -> dict[str, Any]:
    try:
        data = json.loads(raw) if suffix.lower() == ".json" else yaml.safe_load(raw)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise KnowledgeValidationError(f"Invalid {suffix.lstrip('.').upper()} document: {exc}") from exc
    if not isinstance(data, dict):
        raise KnowledgeValidationError("Knowledge document must be an object.")
    return data


def canonical_position_key(fen: str) -> str:
    """Position identity excludes move counters, but retains board and side to move."""
    try:
        position = xiangqi.Position.from_fen(fen)
    except xiangqi.PositionError as exc:
        raise KnowledgeValidationError(f"Invalid FEN: {exc}") from exc
    fields = position.to_fen().split()
    return f"{fields[0]} {fields[1]}"


def validate_knowledge(raw: dict[str, Any]) -> OpeningKnowledge:
    try:
        opening = OpeningKnowledge.model_validate(raw)
    except Exception as exc:
        raise KnowledgeValidationError(f"Knowledge schema validation failed: {exc}") from exc

    source_ids = {source.id for source in opening.source_refs}
    if len(source_ids) != len(opening.source_refs):
        raise KnowledgeValidationError("Source IDs must be unique.")
    if len({line.id for line in opening.lines}) != len(opening.lines):
        raise KnowledgeValidationError("Opening line IDs must be unique.")
    if opening.review_status == "published" and any(line.review_status != "published" for line in opening.lines):
        raise KnowledgeValidationError("A published opening cannot contain an unpublished line.")
    if opening.review_status == "published" and (
        any(annotation.review_status != "published" for annotation in opening.annotations)
        or opening.lesson.review_status != "published"
        or any(exercise.review_status != "published" for exercise in opening.lesson.exercises)
    ):
        raise KnowledgeValidationError("A published opening cannot expose unpublished lesson content.")

    root = xiangqi.Position.from_fen(xiangqi.STARTING_FEN)
    canonical_owners: dict[str, set[str]] = defaultdict(set)
    edge_claims: dict[tuple[str, str], str] = {}
    for line in opening.lines:
        missing = set(line.source_refs) - source_ids
        if missing:
            raise KnowledgeValidationError(f"Line {line.id} references missing sources: {sorted(missing)}")
        if not line.moves_iccs:
            raise KnowledgeValidationError(f"Line {line.id} must contain at least one move.")
        position = root.copy()
        key = canonical_position_key(position.to_fen())
        seen = {key}
        canonical_owners[key].add(line.id)
        for move in line.moves_iccs:
            from_key = canonical_position_key(position.to_fen())
            try:
                following = xiangqi.apply_move(position, move)
            except (xiangqi.PositionError, xiangqi.IllegalMoveError) as exc:
                raise KnowledgeValidationError(f"Line {line.id} contains illegal move {move}: {exc}") from exc
            to_key = canonical_position_key(following.to_fen())
            if to_key in seen:
                raise KnowledgeValidationError(f"Line {line.id} contains a cycle at {to_key}.")
            claimed = edge_claims.get((from_key, move))
            if claimed is not None and claimed != to_key:
                raise KnowledgeValidationError(f"Line {line.id} has an inconsistent path for {move}.")
            edge_claims[(from_key, move)] = to_key
            seen.add(to_key)
            canonical_owners[to_key].add(line.id)
            position = following

    for annotation in opening.annotations:
        if annotation.position_key not in canonical_owners:
            raise KnowledgeValidationError(f"Annotation {annotation.id} points to an unknown position.")
        if set(annotation.source_refs) - source_ids:
            raise KnowledgeValidationError(f"Annotation {annotation.id} references missing sources.")
        if annotation.review_status == "published" and opening.review_status != "published":
            raise KnowledgeValidationError("Published annotations require a published opening.")
    annotation_ids = {annotation.id for annotation in opening.annotations}
    for step in opening.lesson.steps:
        if set(step.annotation_ids) - annotation_ids:
            raise KnowledgeValidationError(f"Lesson step {step.id} references missing annotations.")
        if step.moves_iccs:
            position = root.copy()
            for move in step.moves_iccs:
                try:
                    position = xiangqi.apply_move(position, move)
                except (xiangqi.PositionError, xiangqi.IllegalMoveError) as exc:
                    raise KnowledgeValidationError(f"Lesson step {step.id} has illegal move {move}.") from exc
    for exercise in opening.lesson.exercises:
        if set(exercise.source_refs) - source_ids:
            raise KnowledgeValidationError(f"Exercise {exercise.id} references missing sources.")
        try:
            exercise_position = xiangqi.Position.from_fen(exercise.fen)
        except xiangqi.PositionError as exc:
            raise KnowledgeValidationError(f"Exercise {exercise.id} has invalid FEN: {exc}") from exc
        for choice in exercise.choices:
            if choice.move_iccs not in xiangqi.legal_moves(exercise_position):
                raise KnowledgeValidationError(
                    f"Exercise {exercise.id} offers illegal move {choice.move_iccs}."
                )
            reply_position = xiangqi.apply_move(exercise_position, choice.move_iccs)
            for reply in choice.counterplay_moves_iccs:
                if reply not in xiangqi.legal_moves(reply_position):
                    raise KnowledgeValidationError(
                        f"Exercise {exercise.id} has illegal counterplay move {reply} after {choice.move_iccs}."
                    )
                reply_position = xiangqi.apply_move(reply_position, reply)

    return opening


def build_graph(opening: OpeningKnowledge) -> OpeningGraph:
    root = xiangqi.Position.from_fen(xiangqi.STARTING_FEN)
    root_key = canonical_position_key(root.to_fen())
    positions: dict[str, tuple[xiangqi.Position, set[str]]] = {root_key: (root, set())}
    edges: dict[tuple[str, str], tuple[str, set[str]]] = {}
    for line in opening.lines:
        position = root.copy()
        parent_key = root_key
        for move in line.moves_iccs:
            following = xiangqi.apply_move(position, move)
            target_key = canonical_position_key(following.to_fen())
            if (parent_key, move) not in edges:
                edges[(parent_key, move)] = (target_key, set())
            edges[(parent_key, move)][1].add(line.id)
            if target_key not in positions:
                positions[target_key] = (following.copy(), set())
            positions[target_key][1].add(line.id)
            position = following
            parent_key = target_key
    return OpeningGraph(
        opening_id=opening.opening_id,
        root_position_key=root_key,
        positions=[
            GraphPosition(position_key=key, fen=position.to_fen(), side_to_move=position.turn, incoming_lines=sorted(lines))
            for key, (position, lines) in positions.items()
        ],
        edges=[
            GraphEdge(from_position_key=source, move_iccs=move, to_position_key=target, line_ids=sorted(line_ids))
            for (source, move), (target, line_ids) in edges.items()
        ],
    )


def _source_fingerprint() -> tuple[str, int, int]:
    resolved = DATA_PATH.resolve()
    stat = resolved.stat()
    return str(resolved), stat.st_mtime_ns, stat.st_size


@lru_cache(maxsize=4)
def _load_snapshot(path: str, modified_ns: int, size: int) -> tuple[OpeningKnowledge, OpeningGraph]:
    del modified_ns, size  # These values are part of the cache key for edit invalidation.
    source = Path(path)
    opening = validate_knowledge(load_document(source.read_text(encoding="utf-8"), source.suffix))
    return opening, build_graph(opening)


def clear_opening_cache() -> None:
    _load_snapshot.cache_clear()


def _cached_snapshot() -> tuple[OpeningKnowledge, OpeningGraph]:
    return _load_snapshot(*_source_fingerprint())


def load_opening() -> OpeningKnowledge:
    opening, _ = _cached_snapshot()
    return opening.model_copy(deep=True)


def get_opening(opening_id: str, *, include_experimental: bool = False) -> OpeningDetail | None:
    opening, graph = _cached_snapshot()
    allowed = VISIBLE_WITH_EXPERIMENTAL if include_experimental else PUBLISHED
    if opening.opening_id != opening_id or opening.review_status not in allowed:
        return None
    return OpeningDetail(opening=opening.model_copy(deep=True), graph=graph.model_copy(deep=True))


def get_opening_for_lesson(
    lesson_id: str, *, include_experimental: bool = False, include_reviewed: bool = False,
) -> OpeningDetail | None:
    opening, graph = _cached_snapshot()
    allowed = {"published"}
    if include_experimental:
        allowed.add("experimental")
    if include_reviewed:
        allowed.add("reviewed")
    if opening.lesson.id != lesson_id or opening.review_status not in allowed:
        return None
    return OpeningDetail(opening=opening.model_copy(deep=True), graph=graph.model_copy(deep=True))


def list_openings(*, include_experimental: bool = False) -> list[dict[str, str]]:
    opening, _ = _cached_snapshot()
    allowed = VISIBLE_WITH_EXPERIMENTAL if include_experimental else PUBLISHED
    if opening.review_status not in allowed:
        return []
    return [{"id": opening.opening_id, "name_vi": opening.name_vi, "review_status": opening.review_status, "version": opening.version}]


def get_lesson(lesson_id: str, *, include_experimental: bool = False) -> Lesson | None:
    opening, _ = _cached_snapshot()
    allowed = VISIBLE_WITH_EXPERIMENTAL if include_experimental else PUBLISHED
    if opening.lesson.id != lesson_id or opening.lesson.review_status not in allowed:
        return None
    return opening.lesson.model_copy(deep=True)
