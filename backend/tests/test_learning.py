from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from backend.app.engine.service import EngineLine, EngineResult, EngineService, SearchLimits
from backend.app.knowledge.service import load_opening
from backend.app.learning.schemas import AttemptSubmit, GameSaveRequest
from backend.app.learning.service import LearningError, LearningService
from backend.app.learning.store import LearningStore
from backend.app.main import app
from backend.app.rules import xiangqi

client = TestClient(app)
LEARNER_A = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
LEARNER_B = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
GAME_A = UUID("11111111-1111-4111-8111-111111111111")
GAME_B = UUID("22222222-2222-4222-8222-222222222222")
NOW = datetime(2026, 9, 27, 12, tzinfo=UTC)


def attempt(*, learner=LEARNER_A, attempt_id="33333333-3333-4333-8333-333333333333", game=GAME_A,
            exercise="predict-black-response", move="a9a8", version=None, hint=1, reason="Phát triển quân.", checks=None):
    opening = load_opening()
    return AttemptSubmit(
        learner_id=learner, attempt_id=UUID(attempt_id), game_id=game, lesson_id=opening.lesson.id,
        exercise_id=exercise, exercise_version=version or opening.lesson.content_version, selected_move=move,
        learner_reason=reason, hint_level=hint, rubric_self_checks=checks or [], include_experimental=True,
    )


def make_service(tmp_path, clock=None):
    return LearningService(LearningStore(tmp_path / "learning.sqlite3"), now=clock or (lambda: NOW))


def test_taxonomy_covers_all_skills_and_exercise_tags_have_explicit_mapping():
    service = LearningService(LearningStore(":memory:"), now=lambda: NOW)
    opening = load_opening()
    mapping = service.taxonomy["legacy_tag_map"]
    ids = set(service.skills)
    assert len(ids) == 6
    assert all(tag in mapping or tag in ids for exercise in opening.lesson.exercises for tag in exercise.skill_tags)
    assert service.taxonomy["rubric_policy"]["points_possible"] == 2


def test_attempt_scores_only_observable_dimensions_and_schedules_deterministically(tmp_path):
    service = make_service(tmp_path)
    payload = attempt()
    receipt = service.submit_attempt(payload)
    assert receipt.outcome.status == "needs_practice"
    assert receipt.outcome.points == 1  # Input was present; meaning is not auto-graded.
    assert receipt.outcome.reason_submitted is True
    assert receipt.outcome.repeated_error_count == 1
    assert receipt.outcome.review_due_at == NOW + timedelta(days=1)
    progress = service.progress(str(LEARNER_A))
    assert progress.total_attempts == 1
    assert progress.due_reviews == 0
    assert {skill.skill_id for skill in progress.skills} == {"read_threats", "calculate_variations", "develop_pieces"}


def test_idempotent_duplicate_returns_original_and_payload_conflict_is_rejected(tmp_path):
    service = make_service(tmp_path)
    payload = attempt()
    first = service.submit_attempt(payload)
    duplicate = service.submit_attempt(payload)
    assert duplicate.duplicate is True
    assert duplicate.outcome == first.outcome
    assert service.progress(str(LEARNER_A)).total_attempts == 1
    with pytest.raises(LearningError) as error:
        service.submit_attempt(attempt(reason="Different text with the same id."))
    assert error.value.status_code == 409
    assert error.value.code == "idempotency_conflict"


def test_due_review_and_repeated_error_heuristic_prioritize_similar_exercise(tmp_path):
    clock = [NOW]
    service = make_service(tmp_path, lambda: clock[0])
    service.submit_attempt(attempt())
    next_item = service.recommend(str(LEARNER_A), include_experimental=True)
    assert next_item.exercise_id == "predict-black-response"
    assert "lặp lại lỗi" in next_item.reason
    clock[0] = NOW + timedelta(days=1)
    assert service.progress(str(LEARNER_A)).due_reviews == 1
    assert len(service.due_reviews(str(LEARNER_A))) == 1
    due_item = service.recommend(str(LEARNER_A), include_experimental=True)
    assert due_item.exercise_id == "predict-black-response"
    assert "lịch ôn" in due_item.reason
    success = attempt(attempt_id="44444444-4444-4444-8444-444444444444", move="h9g7")
    receipt = service.submit_attempt(success)
    assert receipt.outcome.status == "focus_aligned"
    assert receipt.outcome.review_due_at == clock[0] + timedelta(days=3)
    assert service.progress(str(LEARNER_A)).due_reviews == 0


def test_two_local_learners_with_different_errors_receive_different_exercises(tmp_path):
    service = make_service(tmp_path)
    service.submit_attempt(attempt(learner=LEARNER_A, game=GAME_A))
    service.submit_attempt(attempt(learner=LEARNER_B, game=GAME_B, move="h9g7"))
    service.submit_attempt(attempt(learner=LEARNER_B, game=GAME_B, exercise="transfer-development-idea",
                                   move="a3a4", attempt_id="55555555-5555-4555-8555-555555555555"))
    rec_a = service.recommend(str(LEARNER_A), include_experimental=True)
    rec_b = service.recommend(str(LEARNER_B), include_experimental=True)
    assert rec_a.exercise_id == "predict-black-response"
    assert rec_b.exercise_id == "transfer-development-idea"
    assert service.progress(str(LEARNER_A)).total_attempts == 1
    assert service.progress(str(LEARNER_B)).total_attempts == 2


def test_content_version_change_keeps_old_attempt_and_rejects_stale_new_submission(tmp_path, monkeypatch):
    import backend.app.learning.service as learning_module

    service = make_service(tmp_path)
    old = attempt()
    service.submit_attempt(old)
    current = load_opening().model_copy(deep=True)
    current.lesson.content_version = "0.2.0-experimental"
    monkeypatch.setattr(learning_module, "load_opening", lambda: current)
    assert service.submit_attempt(old).duplicate is True
    with pytest.raises(LearningError) as error:
        service.submit_attempt(attempt(attempt_id="66666666-6666-4666-8666-666666666666"))
    assert error.value.status_code == 409
    assert service.progress(str(LEARNER_A)).total_attempts == 1


def test_invalid_rubric_check_and_move_are_rejected(tmp_path):
    service = make_service(tmp_path)
    with pytest.raises(LearningError, match="không hợp lệ"):
        service.submit_attempt(attempt(move="h9h8"))
    with pytest.raises(LearningError) as error:
        service.submit_attempt(attempt(checks=["Tôi đã giải hoàn hảo"] ))
    assert error.value.code == "unknown_rubric_item"


def test_production_does_not_accept_experimental_attempts(tmp_path):
    service = LearningService(LearningStore(tmp_path / "learning.sqlite3"), app_env="production", now=lambda: NOW)
    with pytest.raises(LearningError) as error:
        service.submit_attempt(attempt())
    assert error.value.code == "lesson_not_available"


def test_game_history_is_rules_validated_and_ownership_scoped(tmp_path):
    service = make_service(tmp_path)
    payload = GameSaveRequest(learner_id=LEARNER_A, game_id=GAME_A, starting_fen=xiangqi.STARTING_FEN,
                              moves_iccs=["b2e2", "h9g7", "b0c2"])
    result = service.save_game(payload)
    assert result.ply_count == 3
    stored = service.store.game(learner_id=str(LEARNER_A), game_id=str(GAME_A))
    assert len(__import__("json").loads(stored["positions_json"])) == 4
    with pytest.raises(LearningError) as error:
        service.save_game(payload.model_copy(update={"learner_id": LEARNER_B}))
    assert error.value.code == "game_not_found"
    with pytest.raises(LearningError) as error:
        service.save_game(payload.model_copy(update={"game_id": GAME_B, "moves_iccs":["b2b8"]}))
    assert error.value.code == "illegal_game_move"


def test_saved_game_resume_append_and_branch_only_validate_new_suffix(tmp_path, monkeypatch):
    service = make_service(tmp_path)
    moves = ["b2e2", "h9g7", "b0c2", "b9c7"]
    first = GameSaveRequest(learner_id=LEARNER_A, game_id=GAME_A, starting_fen=xiangqi.STARTING_FEN,
                           moves_iccs=moves[:3])
    service.save_game(first)
    restored = service.get_game(str(LEARNER_A), str(GAME_A))
    assert restored.moves_iccs == moves[:3]
    assert restored.positions_fens[0] == xiangqi.STARTING_FEN
    assert len(restored.positions_fens) == 4

    original_apply = xiangqi.apply_move
    validated: list[str] = []

    def counted_apply(position, move):
        validated.append(move)
        return original_apply(position, move)

    monkeypatch.setattr(xiangqi, "apply_move", counted_apply)
    service.save_game(first.model_copy(update={"moves_iccs": moves}))
    assert validated == [moves[3]]
    assert service.get_game(str(LEARNER_A), str(GAME_A)).moves_iccs == moves

    position = xiangqi.Position.from_fen(restored.positions_fens[2])
    branch_move = next(move for move in xiangqi.legal_moves(position) if move != moves[2])
    validated.clear()
    branch = first.model_copy(update={"moves_iccs": moves[:2] + [branch_move]})
    service.save_game(branch)
    assert validated == [branch_move]
    assert service.get_game(str(LEARNER_A), str(GAME_A)).moves_iccs == moves[:2] + [branch_move]

    with pytest.raises(LearningError) as error:
        service.save_game(first.model_copy(update={"starting_fen": xiangqi.STARTING_FEN.replace(" 0 1", " 1 1")}))
    assert error.value.code == "game_start_conflict"


def test_saved_game_http_read_is_owner_scoped(tmp_path):
    service = make_service(tmp_path)
    service.save_game(GameSaveRequest(learner_id=LEARNER_A, game_id=GAME_A, starting_fen=xiangqi.STARTING_FEN,
                                      moves_iccs=["b2e2", "h9g7"]))
    app.state.learning_service = service
    response = client.get(f"/v1/learning/games/{GAME_A}?learner_id={LEARNER_A}")
    assert response.status_code == 200
    assert response.json()["moves_iccs"] == ["b2e2", "h9g7"]
    hidden = client.get(f"/v1/learning/games/{GAME_A}?learner_id={LEARNER_B}")
    assert hidden.status_code == 404


class ScoredAdapter:
    def __init__(self, red_scores):
        self.red_scores = red_scores

    async def analyze(self, fen, limits, multipv):
        position = xiangqi.Position.from_fen(fen)
        red_score = self.red_scores.get(fen, 0)
        score_side = red_score if position.turn == "r" else -red_score
        pv = (xiangqi.legal_moves(position)[0],)
        return EngineResult("mock", "1", "mock", fen, limits, (EngineLine(1, 6, score_side, None, pv),), "side_to_move", 1, True)

    async def close(self):
        return None


def test_rematch_engine_marks_up_to_three_score_drops_for_user_to_choose(tmp_path):
    service = make_service(tmp_path)
    fen0 = xiangqi.STARTING_FEN
    positions = [fen0]
    position = xiangqi.Position.from_fen(fen0)
    for move in ["b2e2", "h9g7", "b0c2"]:
        position = xiangqi.apply_move(position, move)
        positions.append(position.to_fen())
    service.save_game(GameSaveRequest(learner_id=LEARNER_A, game_id=GAME_A, starting_fen=fen0,
                                      moves_iccs=["b2e2", "h9g7", "b0c2"]))
    scores = {positions[0]: 220, positions[1]: 40, positions[2]: 40, positions[3]: -140}
    result = asyncio.run(service.rematch(str(LEARNER_A), str(GAME_A), EngineService(ScoredAdapter(scores))))
    assert [candidate.ply for candidate in result.candidates] == [1, 3]
    assert all(candidate.engine_marked for candidate in result.candidates)
    assert all("100 cp" in candidate.evidence for candidate in result.candidates)


def test_export_and_delete_remove_all_local_learner_data(tmp_path):
    service = make_service(tmp_path)
    service.submit_attempt(attempt())
    exported = service.export(str(LEARNER_A))
    assert len(exported["attempts"]) == 1
    assert exported["attempts"][0].exercise_version == load_opening().lesson.content_version
    service.delete(str(LEARNER_A))
    assert service.progress(str(LEARNER_A)).total_attempts == 0
    assert service.store.games(str(LEARNER_A)) == []


def test_learning_http_api_attempt_dashboard_export_delete_and_isolation(tmp_path, monkeypatch):
    app.state.learning_service = make_service(tmp_path)
    payload = attempt().model_dump(mode="json")
    response = client.post("/v1/learning/attempts", json=payload)
    assert response.status_code == 200
    assert response.json()["outcome"]["status"] == "needs_practice"
    duplicate = client.post("/v1/learning/attempts", json=payload)
    assert duplicate.status_code == 200 and duplicate.json()["duplicate"] is True
    progress = client.get(f"/v1/learning/progress/{LEARNER_A}")
    assert progress.status_code == 200 and progress.json()["total_attempts"] == 1
    assert client.get(f"/v1/learning/progress/{LEARNER_B}").json()["total_attempts"] == 0
    assert client.get(f"/v1/learning/next/{LEARNER_A}?include_experimental=true").json()["exercise_id"] == "predict-black-response"
    exported = client.get(f"/v1/learning/export/{LEARNER_A}")
    assert exported.status_code == 200 and "attachment" in exported.headers["content-disposition"]
    assert client.delete(f"/v1/learning/progress/{LEARNER_A}").json() == {"deleted": True}
    assert client.get(f"/v1/learning/progress/{LEARNER_A}").json()["total_attempts"] == 0
