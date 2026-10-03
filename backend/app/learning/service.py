from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from backend.app.engine.service import EngineService, SearchLimits
from backend.app.knowledge.service import load_opening
from backend.app.learning.schemas import (
    AttemptOutcome,
    AttemptReceipt,
    AttemptSubmit,
    ExerciseRecommendation,
    LearningProgress,
    RematchCandidate,
    RematchResponse,
    SavedGame,
    SkillProgress,
)
from backend.app.learning.store import LearningStore
from backend.app.rules import xiangqi


class LearningError(ValueError):
    def __init__(self, message: str, status_code: int = 422, code: str = "invalid_learning_request"):
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class LearningService:
    def __init__(self, store: LearningStore | None = None, *, app_env: str | None = None, now=None):
        self.store = store or LearningStore()
        self.app_env = (app_env or os.getenv("APP_ENV", "local")).casefold()
        self._now = now or (lambda: datetime.now(UTC))
        taxonomy_path = Path(__file__).with_name("taxonomy.json")
        self.taxonomy: dict[str, Any] = json.loads(taxonomy_path.read_text(encoding="utf-8"))
        self.skills = {item["id"]: item for item in self.taxonomy["skills"]}

    def _intervals(self) -> list[int]:
        try:
            values = [int(value.strip()) for value in os.getenv("LEARNING_REVIEW_INTERVALS_DAYS", "1,3,7").split(",")]
            if not values or any(value < 1 or value > 365 for value in values):
                raise ValueError
            return sorted(set(values))
        except ValueError:
            return [1, 3, 7]

    def _opening(self, *, include_experimental: bool):
        opening = load_opening()
        if self.app_env == "production" and opening.review_status not in {"reviewed", "published"}:
            raise LearningError("Học liệu chưa được duyệt để phục vụ trong production.", 404, "lesson_not_available")
        if opening.review_status == "experimental" and (not include_experimental or self.app_env == "production"):
            raise LearningError("Bài học chưa được xuất bản.", 404, "lesson_not_available")
        if opening.lesson.review_status not in {"reviewed", "published"} and not (include_experimental and self.app_env != "production"):
            raise LearningError("Bài học chưa được xuất bản.", 404, "lesson_not_available")
        return opening

    def _exercise(self, payload: AttemptSubmit, *, require_version: bool = True):
        opening = self._opening(include_experimental=payload.include_experimental)
        if opening.lesson.id != payload.lesson_id:
            raise LearningError("Lesson không khớp exercise.", 404, "exercise_not_found")
        exercise = next((item for item in opening.lesson.exercises if item.id == payload.exercise_id), None)
        if not exercise:
            raise LearningError("Không tìm thấy exercise.", 404, "exercise_not_found")
        if require_version and payload.exercise_version != opening.lesson.content_version:
            raise LearningError("Phiên bản bài tập đã thay đổi; hãy tải lại bài trước khi gửi.", 409, "exercise_version_conflict")
        try:
            position = xiangqi.Position.from_fen(exercise.fen)
        except xiangqi.PositionError as exc:
            raise LearningError("FEN bài tập không hợp lệ.", 422, "invalid_exercise_fen") from exc
        if payload.selected_move not in xiangqi.legal_moves(position):
            raise LearningError("Nước chọn không hợp lệ ở vị trí bài tập.", 422, "illegal_move")
        choice = next((choice for choice in exercise.choices if choice.move_iccs == payload.selected_move), None)
        if choice is None:
            raise LearningError("Nước chọn không thuộc các lựa chọn của bài.", 422, "unknown_choice")
        valid_checks = set(exercise.rubric)
        if not set(payload.rubric_self_checks) <= valid_checks:
            raise LearningError("Tự kiểm tra có tiêu chí không thuộc rubric.", 422, "unknown_rubric_item")
        return opening, exercise, choice

    def _skill_ids(self, exercise) -> list[str]:
        mapping = self.taxonomy["legacy_tag_map"]
        ids = {skill for tag in exercise.skill_tags for skill in mapping.get(tag, [tag] if tag in self.skills else [])}
        return sorted(ids)

    def submit_attempt(self, payload: AttemptSubmit) -> AttemptReceipt:
        # Idempotent retries return their recorded result even if content has since advanced.
        normalized = payload.model_dump(mode="json")
        digest = hashlib.sha256(json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        try:
            previous = self.store.find_attempt(learner_id=str(payload.learner_id), attempt_id=str(payload.attempt_id), idempotency_hash=digest)
            if previous:
                return AttemptReceipt(**previous, duplicate=True)
            attempts_before = self.store.attempts(str(payload.learner_id))
            opening, exercise, choice = self._exercise(payload)
            skill_ids = self._skill_ids(exercise)
            now = self._now().astimezone(UTC)
            prior_errors = self.store.error_counts(str(payload.learner_id)).get(exercise.id, 0)
            schedule = self.store.schedule(str(payload.learner_id))
            prior_schedule = {item["skill_id"]: item for item in schedule}
            aligned = bool(choice.correct)
            has_reason = bool(payload.learner_reason.strip())
            intervals = self._intervals()
            if aligned and has_reason:
                repetitions = min((prior_schedule[skill]["repetitions"] + 1 for skill in skill_ids if skill in prior_schedule), default=0)
                interval = intervals[min(repetitions, len(intervals) - 1)]
            else:
                repetitions = 0
                interval = intervals[0]
            due_at = now + timedelta(days=interval)
            repeated_errors = prior_errors + (0 if aligned else 1)
            outcome = {
                "status": "focus_aligned" if aligned else "needs_practice",
                "focus_aligned": aligned,
                "reason_submitted": has_reason,
                "points": int(aligned) + int(has_reason),
                "points_possible": 2,
                "rubric_self_checks": payload.rubric_self_checks,
                "review_due_at": due_at.isoformat(),
                "interval_days": interval,
                "repetitions": repetitions,
                "repeated_error_count": repeated_errors,
            }
            stored, duplicate = self.store.save_attempt(
                learner_id=str(payload.learner_id), attempt_id=str(payload.attempt_id), game_id=str(payload.game_id),
                idempotency_hash=digest, lesson_id=payload.lesson_id, exercise_id=exercise.id,
                exercise_version=opening.lesson.content_version, selected_move=payload.selected_move,
                learner_reason=payload.learner_reason, hint_level=payload.hint_level, skill_ids=skill_ids,
                outcome=outcome, created_at=now.isoformat(),
            )
        except PermissionError as exc:
            raise LearningError(str(exc), 404, "learning_record_not_found") from exc
        except ValueError as exc:
            if str(exc).startswith("Attempt ID"):
                raise LearningError(str(exc), 409, "idempotency_conflict") from exc
            raise
        return AttemptReceipt(**stored, duplicate=duplicate)

    def progress(self, learner_id: str) -> LearningProgress:
        attempts = self.store.attempts(learner_id)
        schedules = self.store.schedule(learner_id)
        schedule_by_skill: dict[str, list[datetime]] = {}
        for item in schedules:
            schedule_by_skill.setdefault(item["skill_id"], []).append(datetime.fromisoformat(item["due_at"]))
        output: list[SkillProgress] = []
        for skill_id, meta in self.skills.items():
            relevant = [attempt for attempt in attempts if skill_id in attempt["skill_ids"]]
            if not relevant:
                continue
            aligned = sum(bool(attempt["outcome"]["focus_aligned"]) for attempt in relevant)
            trailing_errors = 0
            for attempt in reversed(relevant):
                if attempt["outcome"]["focus_aligned"]:
                    break
                trailing_errors += 1
            due_dates = schedule_by_skill.get(skill_id, [])
            output.append(SkillProgress(
                skill_id=skill_id, name=meta["name"], attempts=len(relevant), focus_aligned=aligned,
                sample_size=len(relevant), focus_rate=aligned / len(relevant), repeated_errors=trailing_errors,
                next_review_at=min(due_dates) if due_dates else None,
            ))
        now = self._now().astimezone(UTC)
        return LearningProgress(
            learner_id=learner_id, total_attempts=len(attempts), skills=output,
            due_reviews=len({item["exercise_id"] for item in schedules if datetime.fromisoformat(item["due_at"]) <= now}),
            updated_at=max((datetime.fromisoformat(attempt["created_at"]) for attempt in attempts), default=None),
        )

    def recommend(self, learner_id: str, *, include_experimental: bool = False) -> ExerciseRecommendation:
        opening = self._opening(include_experimental=include_experimental)
        exercises = opening.lesson.exercises
        attempts = self.store.attempts(learner_id)
        counts = self.store.error_counts(learner_id)
        now = self._now().astimezone(UTC)
        due = [item for item in self.store.schedule(learner_id) if datetime.fromisoformat(item["due_at"]) <= now]
        due_ids = {item["exercise_id"] for item in due}
        due_exercises = [exercise for exercise in exercises if exercise.id in due_ids]
        if due_exercises:
            selected = max(due_exercises, key=lambda exercise: max(datetime.fromisoformat(item["due_at"]) for item in due if item["exercise_id"] == exercise.id))
            schedule_at = min(datetime.fromisoformat(item["due_at"]) for item in due if item["exercise_id"] == selected.id)
            reason = "Đến lịch ôn tập theo khoảng thời gian đã cấu hình."
        elif any(counts.values()):
            selected = max(exercises, key=lambda exercise: (counts.get(exercise.id, 0), exercise.id))
            schedule_at = None
            reason = f"Ưu tiên ý tưởng tương tự vì bạn đã lặp lại lỗi này {counts.get(selected.id, 0)} lần."
        else:
            attempted = {attempt["exercise_id"] for attempt in attempts}
            selected = next((exercise for exercise in exercises if exercise.id not in attempted), exercises[0])
            schedule_at = None
            reason = "Bài tiếp theo chưa có bằng chứng làm bài; bắt đầu để tạo mẫu học tập."
        return ExerciseRecommendation(
            lesson_id=opening.lesson.id, exercise_id=selected.id, exercise_version=opening.lesson.content_version,
            question=selected.question, skill_ids=self._skill_ids(selected), reason=reason,
            scheduled_for=schedule_at, include_experimental=opening.review_status == "experimental",
        )

    def due_reviews(self, learner_id: str) -> list[ExerciseRecommendation]:
        opening = self._opening(include_experimental=True)
        now = self._now().astimezone(UTC)
        exercises = {exercise.id: exercise for exercise in opening.lesson.exercises}
        output: dict[str, ExerciseRecommendation] = {}
        for row in self.store.schedule(learner_id):
            due_at = datetime.fromisoformat(row["due_at"])
            exercise = exercises.get(row["exercise_id"])
            if due_at <= now and exercise:
                output.setdefault(exercise.id, ExerciseRecommendation(
                    lesson_id=opening.lesson.id, exercise_id=exercise.id, exercise_version=opening.lesson.content_version,
                    question=exercise.question, skill_ids=self._skill_ids(exercise),
                    reason=f"Ôn kỹ năng {self.skills[row['skill_id']]['name']} sau {row['interval_days']} ngày.",
                    scheduled_for=due_at, include_experimental=opening.review_status == "experimental",
                ))
        return list(output.values())

    async def rematch(self, learner_id: str, game_id: str, engine: EngineService | None) -> RematchResponse:
        game = self.store.game(learner_id=learner_id, game_id=game_id)
        if not game:
            raise LearningError("Không tìm thấy ván local của người học này.", 404, "game_not_found")
        moves = json.loads(game["moves_json"])
        positions = json.loads(game["positions_json"])
        if not moves or not engine:
            return RematchResponse(game_id=game_id, candidates=[], engine_status="unavailable")
        # Sample up to three chronological checkpoints, then compare mover-relative evals.
        candidate_plies = sorted({1, (len(moves) + 1) // 2, len(moves)})
        candidate_plies = [ply for ply in candidate_plies if ply > 0 and ply <= len(moves)]
        scored: list[tuple[int, RematchCandidate]] = []
        for ply in candidate_plies:
            before_fen, after_fen = positions[ply - 1], positions[ply]
            try:
                before_result = await engine.analyze(before_fen, SearchLimits(time_ms=250, depth=6), 1, f"rematch-{game_id}-{ply}-before")
                after_result = await engine.analyze(after_fen, SearchLimits(time_ms=250, depth=6), 1, f"rematch-{game_id}-{ply}-after")
            except Exception:
                continue
            before_score = _score_red(before_result)
            after_score = _score_red(after_result)
            mover = "r" if before_fen.split()[1] == "r" else "b"
            centipawn_loss = before_score - after_score if mover == "r" else after_score - before_score
            if centipawn_loss >= 100:
                scored.append((centipawn_loss, RematchCandidate(
                    game_id=game_id, ply=ply, fen=before_fen, move_iccs=moves[ply - 1],
                    reason=f"Sau nước này, engine eval giảm khoảng {centipawn_loss} cp cho bên vừa đi.",
                    engine_marked=True, evidence=f"{before_result.engine_id} {before_result.engine_version}, depth {before_result.lines[0].depth}; ngưỡng 100 cp.",
                )))
        chosen = sorted(scored, key=lambda entry: (-entry[0], entry[1].ply))[:3]
        return RematchResponse(game_id=game_id, candidates=[entry[1] for entry in chosen], engine_status="available")

    def export(self, learner_id: str) -> dict[str, Any]:
        attempts = [AttemptReceipt(**row) for row in self.store.attempts(learner_id)]
        games = self.store.games(learner_id)
        return {"learner_id": learner_id, "exported_at": self._now().astimezone(UTC), "attempts": attempts, "games": games}

    def delete(self, learner_id: str) -> None:
        self.store.delete_learner(learner_id)

    def get_game(self, learner_id: str, game_id: str) -> SavedGame:
        row = self.store.game(learner_id=learner_id, game_id=game_id)
        if not row or not row["starting_fen"]:
            raise LearningError("Không tìm thấy ván local của người học này.", 404, "game_not_found")
        try:
            moves = json.loads(row["moves_json"])
            positions = json.loads(row["positions_json"])
            if len(positions) != len(moves) + 1:
                raise ValueError("Saved game history is inconsistent.")
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise LearningError("Lịch sử ván local bị lỗi; không thể khôi phục an toàn.", 500, "game_history_corrupt") from exc
        return SavedGame(
            learner_id=learner_id, game_id=game_id, starting_fen=row["starting_fen"],
            moves_iccs=moves, positions_fens=positions, ended=bool(row["ended"]), updated_at=row["updated_at"],
        )

    def save_game(self, payload):
        try:
            position = xiangqi.Position.from_fen(payload.starting_fen)
        except xiangqi.PositionError as exc:
            raise LearningError("FEN ván cờ không hợp lệ.", 422, "invalid_fen") from exc
        starting_fen = position.to_fen()
        positions = [starting_fen]
        first_unvalidated_ply = 0
        existing = self.store.game(learner_id=str(payload.learner_id), game_id=str(payload.game_id))
        if existing and existing["starting_fen"] == starting_fen:
            try:
                previous_moves = json.loads(existing["moves_json"])
                previous_positions = json.loads(existing["positions_json"])
                if len(previous_positions) == len(previous_moves) + 1 and previous_positions[0] == starting_fen:
                    while (
                        first_unvalidated_ply < len(payload.moves_iccs)
                        and first_unvalidated_ply < len(previous_moves)
                        and payload.moves_iccs[first_unvalidated_ply] == previous_moves[first_unvalidated_ply]
                    ):
                        first_unvalidated_ply += 1
                    positions = previous_positions[: first_unvalidated_ply + 1]
                    position = xiangqi.Position.from_fen(positions[-1])
            except (TypeError, ValueError, json.JSONDecodeError, xiangqi.PositionError):
                positions = [starting_fen]
                position = xiangqi.Position.from_fen(starting_fen)
                first_unvalidated_ply = 0
        for move in payload.moves_iccs[first_unvalidated_ply:]:
            try:
                position = xiangqi.apply_move(position, move)
            except xiangqi.IllegalMoveError as exc:
                raise LearningError(f"Lịch sử ván chứa nước không hợp lệ: {move}.", 422, "illegal_game_move") from exc
            positions.append(position.to_fen())
        now = self._now().astimezone(UTC).isoformat()
        try:
            self.store.save_game(
                learner_id=str(payload.learner_id), game_id=str(payload.game_id), starting_fen=positions[0],
                moves=payload.moves_iccs, positions=positions, ended=payload.ended, updated_at=now,
            )
        except PermissionError as exc:
            raise LearningError(str(exc), 404, "game_not_found") from exc
        except ValueError as exc:
            raise LearningError(str(exc), 409, "game_start_conflict") from exc
        from backend.app.learning.schemas import GameSaveResponse
        return GameSaveResponse(game_id=payload.game_id, ply_count=len(payload.moves_iccs))


def _score_red(result) -> int:
    line = result.lines[0]
    if line.mate_in_side_to_move is not None:
        side = result.position.split()[1]
        return (100000 if line.mate_in_side_to_move > 0 else -100000) * (1 if side == "r" else -1)
    cp = line.score_cp_side_to_move or 0
    return cp if result.position.split()[1] == "r" else -cp
