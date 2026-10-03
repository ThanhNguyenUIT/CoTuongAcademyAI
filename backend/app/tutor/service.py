from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import time
from collections import defaultdict, deque
from uuid import uuid4

from backend.app.engine.service import EngineError, EngineService, SearchLimits, configured_engine_service
from backend.app.knowledge.schemas import LessonExercise, OpeningDetail
from backend.app.knowledge.service import canonical_position_key, get_opening_for_lesson
from backend.app.rules import xiangqi
from backend.app.tutor.providers import TutorProvider, TutorProviderError, configured_provider
from backend.app.tutor.schemas import (
    TutorAnswer,
    TutorClaim,
    TutorContext,
    TutorDraftClaim,
    TutorEvidence,
    TutorHintRequest,
    TutorAnnotationContext,
    TutorProviderDraft,
)

logger = logging.getLogger(__name__)
_MOVE_TOKEN = re.compile(r"(?<![a-z0-9])[a-i][0-9][a-i][0-9](?![a-z0-9])", re.IGNORECASE)
_UNPROVEN_CLAIM = re.compile(r"thắng bắt buộc|forced win|forced mate|chiếu hết bắt buộc|nước tốt nhất|best move", re.IGNORECASE)


class TutorRequestError(ValueError):
    def __init__(self, code: str, message: str, status_code: int = 422):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class TutorService:
    def __init__(self, *, provider: TutorProvider | None = None, engine_service: EngineService | None = None, app_env: str | None = None):
        self.provider = provider
        self._provider_loaded = provider is not None
        self.engine_service = engine_service
        self.app_env = (app_env if app_env is not None else os.getenv("APP_ENV", "development")).lower()
        self._provider_cache: dict[str, tuple[float, TutorProviderDraft]] = {}
        self._engine_cache: dict[str, tuple[float, object]] = {}
        self._provider_calls: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    def _get_provider(self) -> TutorProvider | None:
        if not self._provider_loaded:
            self.provider = configured_provider()
            self._provider_loaded = True
        return self.provider

    def _get_engine(self) -> EngineService | None:
        if self.engine_service is not None:
            return self.engine_service
        try:
            self.engine_service = configured_engine_service()
        except EngineError:
            return None
        return self.engine_service

    def _limit_provider(self, key: str) -> None:
        now = time.monotonic()
        recent = self._provider_calls[key]
        while recent and now - recent[0] > 60:
            recent.popleft()
        if len(recent) >= 20:
            raise TutorRequestError("tutor_rate_limited", "Đã đạt giới hạn gợi ý tạm thời; hãy chờ một phút.", 429)
        recent.append(now)

    @staticmethod
    def _cache_key(context: TutorContext) -> str:
        value = context.model_dump(mode="json", exclude={"trace_id"})
        return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    async def _analyze(self, fen: str):
        engine = self._get_engine()
        if engine is None:
            return None
        key = hashlib.sha256(f"{fen}|400|8|2".encode()).hexdigest()
        cached = self._engine_cache.get(key)
        if cached and time.monotonic() - cached[0] < 45:
            return cached[1]
        try:
            result = await engine.analyze(fen, SearchLimits(time_ms=400, depth=8), 2)
        except (EngineError, ValueError):
            return None
        if not any(line.pv for line in result.lines):
            return None
        self._engine_cache[key] = (time.monotonic(), result)
        return result

    def _evidence_and_exercise(self, request: TutorHintRequest) -> tuple[OpeningDetail, LessonExercise, bool]:
        production = self.app_env == "production"
        allow_experimental = request.include_experimental and not production
        detail = get_opening_for_lesson(
            request.lesson_id, include_experimental=allow_experimental, include_reviewed=True,
        )
        if detail is None or detail.opening.lesson.id != request.lesson_id:
            raise TutorRequestError("tutor_content_unavailable", "Bài học không được xuất bản hoặc không tồn tại.", 404)
        lesson = detail.opening.lesson
        exercise = next((item for item in lesson.exercises if item.id == request.exercise_id), None)
        if exercise is None:
            raise TutorRequestError("tutor_exercise_unavailable", "Bài tập không tồn tại trong bài học.", 404)
        if production and (detail.opening.review_status not in {"reviewed", "published"} or lesson.review_status not in {"reviewed", "published"} or exercise.review_status not in {"reviewed", "published"}):
            raise TutorRequestError("tutor_content_unavailable", "Nội dung chưa được duyệt để dùng trong production.", 404)
        try:
            actual_key = canonical_position_key(request.fen)
            expected_key = canonical_position_key(exercise.fen)
        except ValueError as exc:
            raise TutorRequestError("invalid_fen", "FEN không hợp lệ.") from exc
        return detail, exercise, actual_key != expected_key

    async def hint(self, request: TutorHintRequest, *, client_key: str = "local") -> TutorAnswer:
        try:
            position = xiangqi.Position.from_fen(request.fen)
        except xiangqi.PositionError as exc:
            raise TutorRequestError("invalid_fen", "FEN không hợp lệ.") from exc
        detail, exercise, off_theory = self._evidence_and_exercise(request)
        legal_moves = xiangqi.legal_moves(position)
        if request.learner_move and request.learner_move not in legal_moves:
            raise TutorRequestError("illegal_learner_move", "Nước người học gửi không hợp lệ trong vị trí này.")

        trace_id = uuid4().hex
        lesson = detail.opening.lesson
        base_ref = f"lesson:{lesson.id}:exercise:{exercise.id}"
        evidence: list[TutorEvidence] = [TutorEvidence(
            ref=base_ref, kind="lesson", review_status=exercise.review_status,
            version=lesson.content_version, source_refs=exercise.source_refs,
            moves_iccs=[choice.move_iccs for choice in exercise.choices],
        )]
        rules_hash = hashlib.sha256(request.fen.encode()).hexdigest()[:12]
        evidence.append(TutorEvidence(ref=f"rules:{rules_hash}", kind="rules", review_status="reviewed", moves_iccs=([request.learner_move] if request.learner_move else [])))
        reviewed_annotations = []
        for annotation in detail.opening.annotations:
            if annotation.review_status not in {"reviewed", "published"}:
                continue
            if annotation.position_key == canonical_position_key(request.fen):
                evidence.append(TutorEvidence(
                    ref=f"annotation:{annotation.id}", kind="source", review_status=annotation.review_status,
                    version=annotation.version, source_refs=annotation.source_refs,
                ))
                reviewed_annotations.append(TutorAnnotationContext(
                    annotation_id=annotation.id, claim=annotation.claim, source_refs=annotation.source_refs,
                    review_status=annotation.review_status, version=annotation.version,
                ))

        engine_result = await self._analyze(request.fen) if request.hint_level >= 2 else None
        engine_lines: list[list[str]] = []
        if engine_result:
            for index, line in enumerate(engine_result.lines):
                if not line.pv:
                    continue
                ref = f"engine:{engine_result.engine_id}:{engine_result.engine_version}:pv{index + 1}"
                evidence.append(TutorEvidence(
                    ref=ref, kind="engine", review_status="engine_validated",
                    engine_id=engine_result.engine_id, engine_version=engine_result.engine_version,
                    depth=line.depth, score_cp_side_to_move=line.score_cp_side_to_move,
                    mate_in_side_to_move=line.mate_in_side_to_move, moves_iccs=list(line.pv),
                ))
                engine_lines.append(list(line.pv))

        verified_moves = list(dict.fromkeys(
            [choice.move_iccs for choice in exercise.choices if not off_theory and choice.move_iccs in legal_moves]
            + [line[0] for line in engine_lines if line and line[0] in legal_moves]
        ))
        question = (
            exercise.question if not off_theory else
            "Vị trí đã rời bài mẫu. Bạn nhận ra mối đe dọa nào và muốn kiểm tra gì trước khi chọn kế hoạch?"
        )
        content_status = detail.opening.review_status
        context = TutorContext(
            trace_id=trace_id,
            lesson_id=lesson.id,
            exercise_id=exercise.id,
            position_fen=position.to_fen(),
            hint_level=request.hint_level,
            question=question,
            learning_outcomes=lesson.outcomes,
            exercise_rubric=exercise.rubric,
            choice_feedback=[choice.feedback for choice in exercise.choices] if not off_theory else [],
            reviewed_annotations=reviewed_annotations,
            learner_move=request.learner_move,
            learner_reason=request.learner_reason,
            off_theory=off_theory,
            evidence=evidence,
            verified_candidate_moves=verified_moves,
            engine_lines=engine_lines,
            content_review_status=content_status,
            content_version=lesson.content_version,
        )

        try:
            provider = self._get_provider()
        except TutorProviderError:
            provider = None
        draft: TutorProviderDraft | None = None
        fallback_reason = "LLM chưa được cấu hình hợp lệ; dùng gợi ý đã viết sẵn." if provider is None else ""
        if provider is not None:
            cache_key = self._cache_key(context)
            cached = self._provider_cache.get(cache_key)
            if cached and time.monotonic() - cached[0] < 1200:
                draft = cached[1]
            else:
                self._limit_provider(client_key)
                try:
                    draft = await provider.explain(context)
                    self._provider_cache[cache_key] = (time.monotonic(), draft)
                    if len(self._provider_cache) > 256:
                        oldest = min(self._provider_cache, key=lambda key: self._provider_cache[key][0])
                        self._provider_cache.pop(oldest, None)
                except TutorProviderError:
                    fallback_reason = "LLM hiện không khả dụng; dùng gợi ý đã viết sẵn."
                except Exception:
                    fallback_reason = "LLM hiện không khả dụng; dùng gợi ý đã viết sẵn."

        fallback = draft is None
        if fallback:
            if off_theory:
                fallback_text = [
                    "Hãy quét bàn cờ để tìm quân đang bị tấn công; chưa cần đoán nước đáp.",
                    "So sánh mối đe dọa với mục tiêu phát triển quân. Engine chưa cung cấp kết luận cho thế này.",
                    "Chọn một nước hợp lệ rồi tự giải thích mục tiêu. Hệ thống không có biến đã duyệt cho thế ngoài bài.",
                ][request.hint_level - 1]
                candidate_moves: list[str] = []
            else:
                fallback_text = exercise.hint_ladder[request.hint_level - 1]
                candidate_moves = []
                if request.hint_level == 3:
                    candidate_moves = [choice.move_iccs for choice in exercise.choices if choice.correct and choice.move_iccs in legal_moves][:1]
            evidence_ref = base_ref if not off_theory else f"rules:{rules_hash}"
            claims = [TutorClaim(text=fallback_text, evidence_refs=[evidence_ref])]
            provider_name = "fallback"
            uncertainty = fallback_reason
        else:
            evidence_map = {item.ref: item for item in evidence}
            claims = []
            for item in draft.claims:
                refs = [ref for ref in item.evidence_refs if ref in evidence_map]
                tokens = _MOVE_TOKEN.findall(item.text)
                if request.hint_level < 3 and tokens:
                    continue
                evidence_moves = {move for ref in refs for move in evidence_map[ref].moves_iccs}
                if tokens and any(token.lower() not in {move.lower() for move in evidence_moves} for token in tokens):
                    continue
                has_mate_proof = any(
                    evidence_map[ref].kind == "engine" and evidence_map[ref].mate_in_side_to_move is not None
                    and evidence_map[ref].mate_in_side_to_move > 0 for ref in refs
                )
                if _UNPROVEN_CLAIM.search(item.text) and not has_mate_proof:
                    continue
                if refs:
                    claims.append(TutorClaim(text=item.text, evidence_refs=refs))
            candidate_moves = []
            if request.hint_level == 3:
                candidate_moves = list(dict.fromkeys(
                    move for move in draft.candidate_moves
                    if move in verified_moves and move in legal_moves
                ))[:3]
            provider_name = provider.name
            uncertainty = draft.uncertainty
            if draft.candidate_moves and not candidate_moves:
                uncertainty = f"{uncertainty} Nước do provider đề xuất không khớp evidence hợp lệ nên đã bị loại."
            if not claims:
                fallback = True
                fallback_reason = "Provider không trả được lời giải có provenance hợp lệ."
                safe_text = exercise.hint_ladder[request.hint_level - 1] if not off_theory else "Hãy tự rà soát mối đe dọa và chọn một nước hợp lệ; chưa đủ chứng cứ cho lời giải cụ thể."
                claims = [TutorClaim(text=safe_text, evidence_refs=[base_ref if not off_theory else f"rules:{rules_hash}"])]
                candidate_moves = []
                provider_name = "fallback"
                uncertainty = fallback_reason

        # Lower levels are deliberately question-led and never expose answer moves.
        if request.hint_level < 3:
            candidate_moves = []
        if content_status == "experimental":
            uncertainty = f"{uncertainty} Học liệu đang ở trạng thái experimental, chưa được chuyên gia duyệt."
        if engine_result is None and request.hint_level >= 2:
            uncertainty = f"{uncertainty} Không có phân tích engine cho vị trí này."
        selected_evidence = {ref for claim in claims for ref in claim.evidence_refs}
        context_digest = self._cache_key(context)
        response = TutorAnswer(
            trace_id=trace_id,
            context_digest=context_digest,
            lesson_id=lesson.id,
            exercise_id=exercise.id,
            position_fen=position.to_fen(),
            hint_level=request.hint_level,
            question=question,
            claims=claims,
            candidate_moves=candidate_moves,
            evidence=[item for item in evidence if item.ref in selected_evidence or item.kind == "engine"],
            uncertainty=uncertainty[:500],
            provider=provider_name,
            fallback=fallback,
            engine_status="available" if engine_result is not None else "unavailable" if request.hint_level >= 2 else "not_requested",
        )
        if any(move not in legal_moves for move in response.candidate_moves):
            raise TutorRequestError("invalid_provider_move", "Tutor response included an unverified move.", 502)
        logger.info("Tutor response trace_id=%s context_digest=%s lesson_id=%s exercise_id=%s content_version=%s provider=%s fallback=%s level=%d evidence_count=%d", trace_id, context_digest, lesson.id, exercise.id, lesson.content_version, provider_name, fallback, request.hint_level, len(response.evidence))
        return response
