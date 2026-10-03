from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class LearningStore:
    """Small local SQLite store for explicit, per-browser learner IDs."""

    def __init__(self, path: str | Path | None = None):
        configured = path or os.getenv("LEARNING_DB_PATH")
        self.path = Path(configured) if configured else Path(__file__).parents[3] / ".local-data" / "learning.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            with connection:
                yield connection
        finally:
            connection.close()

    def _migrate(self) -> None:
        migration = Path(__file__).with_name("migrations") / "001_learning.sql"
        with self._connect() as connection:
            connection.executescript(migration.read_text(encoding="utf-8"))

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def save_game(self, *, learner_id: str, game_id: str, starting_fen: str, moves: list[str], positions: list[str], ended: bool, updated_at: str) -> None:
        with self._connect() as connection:
            owner = connection.execute("SELECT learner_id, starting_fen FROM games WHERE game_id = ?", (game_id,)).fetchone()
            if owner and owner["learner_id"] != learner_id:
                raise PermissionError("Game belongs to a different local learner.")
            if owner and owner["starting_fen"] and owner["starting_fen"] != starting_fen:
                raise ValueError("A saved game's starting position cannot be changed.")
            connection.execute("INSERT OR IGNORE INTO learners(learner_id, created_at) VALUES (?, ?)", (learner_id, updated_at))
            connection.execute(
                """INSERT INTO games(game_id, learner_id, starting_fen, moves_json, positions_json, ended, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(game_id) DO UPDATE SET starting_fen=excluded.starting_fen, moves_json=excluded.moves_json,
                   positions_json=excluded.positions_json, ended=excluded.ended, updated_at=excluded.updated_at""",
                (game_id, learner_id, starting_fen, self._json(moves), self._json(positions), int(ended), updated_at),
            )

    def game(self, *, learner_id: str, game_id: str) -> sqlite3.Row | None:
        with self._connect() as connection:
            return connection.execute("SELECT * FROM games WHERE game_id=? AND learner_id=?", (game_id, learner_id)).fetchone()

    def find_attempt(self, *, learner_id: str, attempt_id: str, idempotency_hash: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM attempts WHERE learner_id=? AND attempt_id=?", (learner_id, attempt_id)).fetchone()
        if not row:
            return None
        if row["idempotency_hash"] != idempotency_hash:
            raise ValueError("Attempt ID was already used with different submission data.")
        return self._attempt_row(row)

    def save_attempt(self, *, learner_id: str, attempt_id: str, game_id: str, idempotency_hash: str, lesson_id: str,
                     exercise_id: str, exercise_version: str, selected_move: str, learner_reason: str, hint_level: int,
                     skill_ids: list[str], outcome: dict[str, Any], created_at: str) -> tuple[dict[str, Any], bool]:
        with self._connect() as connection:
            previous = connection.execute(
                "SELECT * FROM attempts WHERE learner_id=? AND attempt_id=?", (learner_id, attempt_id)
            ).fetchone()
            if previous:
                if previous["idempotency_hash"] != idempotency_hash:
                    raise ValueError("Attempt ID was already used with different submission data.")
                return self._attempt_row(previous), True
            connection.execute("INSERT OR IGNORE INTO learners(learner_id, created_at) VALUES (?, ?)", (learner_id, created_at))
            game = connection.execute("SELECT learner_id FROM games WHERE game_id=?", (game_id,)).fetchone()
            if game and game["learner_id"] != learner_id:
                raise PermissionError("Game belongs to a different local learner.")
            if not game:
                connection.execute(
                    "INSERT INTO games(game_id, learner_id, starting_fen, moves_json, positions_json, ended, updated_at) VALUES (?, ?, '', '[]', '[]', 0, ?)",
                    (game_id, learner_id, created_at),
                )
            connection.execute(
                """INSERT INTO attempts(attempt_id, learner_id, game_id, idempotency_hash, lesson_id, exercise_id,
                   exercise_version, selected_move, learner_reason, hint_level, skill_ids_json, outcome_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (attempt_id, learner_id, game_id, idempotency_hash, lesson_id, exercise_id, exercise_version,
                 selected_move, learner_reason, hint_level, self._json(skill_ids), self._json(outcome), created_at),
            )
            connection.executemany(
                """INSERT INTO review_schedule(learner_id, exercise_id, skill_id, interval_days, repetitions, due_at, last_attempt_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(learner_id, exercise_id, skill_id) DO UPDATE SET interval_days=excluded.interval_days,
                   repetitions=excluded.repetitions, due_at=excluded.due_at, last_attempt_id=excluded.last_attempt_id""",
                [(learner_id, exercise_id, skill, outcome["interval_days"], outcome["repetitions"], outcome["review_due_at"], attempt_id) for skill in skill_ids],
            )
            row = connection.execute("SELECT * FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
            return self._attempt_row(row), False

    @staticmethod
    def _attempt_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "attempt_id": row["attempt_id"], "game_id": row["game_id"], "lesson_id": row["lesson_id"],
            "exercise_id": row["exercise_id"], "exercise_version": row["exercise_version"],
            "skill_ids": json.loads(row["skill_ids_json"]), "outcome": json.loads(row["outcome_json"]), "created_at": row["created_at"],
        }

    def attempts(self, learner_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM attempts WHERE learner_id=? ORDER BY created_at, attempt_id", (learner_id,)).fetchall()
            return [self._attempt_row(row) for row in rows]

    def schedule(self, learner_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM review_schedule WHERE learner_id=? ORDER BY due_at", (learner_id,)).fetchall()
            return [dict(row) for row in rows]

    def error_counts(self, learner_id: str) -> dict[str, int]:
        with self._connect() as connection:
            rows = connection.execute("SELECT exercise_id, outcome_json FROM attempts WHERE learner_id=? ORDER BY created_at", (learner_id,)).fetchall()
        counts: dict[str, int] = {}
        for row in rows:
            outcome = json.loads(row["outcome_json"])
            exercise_id = row["exercise_id"]
            if outcome["focus_aligned"]:
                counts[exercise_id] = 0
            else:
                counts[exercise_id] = counts.get(exercise_id, 0) + 1
        return counts

    def games(self, learner_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM games WHERE learner_id=? AND starting_fen != '' ORDER BY updated_at", (learner_id,)).fetchall()
            return [{**dict(row), "moves": json.loads(row["moves_json"]), "positions": json.loads(row["positions_json"])} for row in rows]

    def delete_learner(self, learner_id: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM learners WHERE learner_id=?", (learner_id,))
