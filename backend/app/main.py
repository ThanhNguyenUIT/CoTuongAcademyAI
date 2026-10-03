from contextlib import asynccontextmanager
import json
import os
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from backend.app.rules import xiangqi
from backend.app.rules.schemas import ApplyMoveRequest, PositionRequest, RulesResponse
from backend.app.engine.schemas import EngineAnalysisResponse, EngineAnalyzeRequest, EngineLineResponse, EngineStopRequest, EngineStopResponse
from backend.app.engine.service import EngineError, EngineService, SearchLimits, configured_engine_service
from backend.app.knowledge.service import get_lesson, get_opening, list_openings, load_opening
from backend.app.tutor.schemas import TutorAnswer, TutorHintRequest
from backend.app.tutor.service import TutorRequestError, TutorService
from backend.app.learning.schemas import AttemptReceipt, AttemptSubmit, GameSaveRequest, GameSaveResponse, LearningProgress, RematchResponse, ExerciseRecommendation, SavedGame
from backend.app.learning.service import LearningError, LearningService


@asynccontextmanager
async def lifespan(application: FastAPI):
    try:
        yield
    finally:
        service = application.state.engine_service
        if service is not None:
            await service.close()


app = FastAPI(title="Xiangqi AI Academy API", version="0.1.0", lifespan=lifespan)
app.state.engine_service = None
app.state.tutor_service = None
app.state.learning_service = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/openings")
def get_opening_catalog(include_experimental: bool = False) -> list[dict[str, str]]:
    return list_openings(include_experimental=include_experimental)


@app.get("/v1/openings/{opening_id}")
def get_opening_detail(opening_id: str, include_experimental: bool = False):
    detail = get_opening(opening_id, include_experimental=include_experimental)
    if detail is None:
        raise HTTPException(status_code=404, detail={"code": "opening_not_found", "message": "Opening not found or not available."})
    return detail


@app.get("/v1/openings/{opening_id}/branches")
def get_opening_branches(opening_id: str, position_key: str, include_experimental: bool = False):
    detail = get_opening(opening_id, include_experimental=include_experimental)
    if detail is None:
        raise HTTPException(status_code=404, detail={"code": "opening_not_found", "message": "Opening not found or not available."})
    if not any(position.position_key == position_key for position in detail.graph.positions):
        raise HTTPException(status_code=404, detail={"code": "position_not_found", "message": "Position not found in this opening."})
    return {
        "position_key": position_key,
        "edges": [edge for edge in detail.graph.edges if edge.from_position_key == position_key],
        "annotations": [annotation for annotation in detail.opening.annotations if annotation.position_key == position_key],
    }


@app.get("/v1/lessons/{lesson_id}")
def get_lesson_detail(lesson_id: str, include_experimental: bool = False):
    lesson = get_lesson(lesson_id, include_experimental=include_experimental)
    if lesson is None:
        raise HTTPException(status_code=404, detail={"code": "lesson_not_found", "message": "Lesson not found or not available."})
    return lesson


@app.post("/v1/rules/legal-moves", response_model=RulesResponse)
def get_legal_moves(request: PositionRequest) -> RulesResponse:
    try:
        position = xiangqi.Position.from_fen(request.fen)
    except xiangqi.PositionError as exc:
        raise HTTPException(status_code=422, detail={"code": "invalid_fen", "message": str(exc)}) from exc
    analysis = xiangqi.analyze_position(position)
    return RulesResponse(
        fen=position.to_fen(),
        moves=list(analysis.legal_moves),
        status=analysis.status,
        in_check=analysis.in_check,
        checked_general=analysis.checked_general,
    )


@app.post("/v1/rules/apply-move", response_model=RulesResponse)
def post_apply_move(request: ApplyMoveRequest) -> RulesResponse:
    try:
        position = xiangqi.Position.from_fen(request.fen)
        result = xiangqi.apply_move(position, request.move)
        analysis = xiangqi.analyze_position(result)
        occurrences = xiangqi.repetition_count(request.history_fens, result.to_fen())
    except xiangqi.PositionError as exc:
        raise HTTPException(status_code=422, detail={"code": "invalid_fen", "message": str(exc)}) from exc
    except xiangqi.IllegalMoveError as exc:
        raise HTTPException(status_code=422, detail={"code": "illegal_move", "message": str(exc)}) from exc
    if occurrences >= 3:
        status = "repetition_review_required"
    else:
        status = analysis.status
    return RulesResponse(
        fen=result.to_fen(),
        moves=list(analysis.legal_moves),
        status=status,
        in_check=analysis.in_check,
        checked_general=analysis.checked_general,
        repetition_count=occurrences,
    )


def _engine_service() -> EngineService:
    service = app.state.engine_service
    if service is None:
        try:
            service = configured_engine_service()
        except EngineError as exc:
            raise HTTPException(status_code=503, detail={"code": "engine_unavailable", "message": str(exc)}) from exc
        app.state.engine_service = service
    return service


def _analysis_response(result) -> EngineAnalysisResponse:
    side_to_move = result.position.split()[1]
    red_sign = 1 if side_to_move == "r" else -1
    lines = [
        EngineLineResponse(
            multipv=line.multipv,
            depth=line.depth,
            score_cp_side_to_move=line.score_cp_side_to_move,
            mate_in_side_to_move=line.mate_in_side_to_move,
            score_cp_red=line.score_cp_side_to_move * red_sign if line.score_cp_side_to_move is not None else None,
            mate_in_red=line.mate_in_side_to_move * red_sign if line.mate_in_side_to_move is not None else None,
            pv=list(line.pv),
        )
        for line in result.lines
    ]
    return EngineAnalysisResponse(
        engine_id=result.engine_id,
        engine_version=result.engine_version,
        protocol=result.protocol,
        position_fen=result.position,
        limits={"time_ms": result.limits.time_ms, "depth": result.limits.depth},
        score_perspective=result.score_perspective,
        elapsed_ms=result.elapsed_ms,
        is_complete=result.is_complete,
        best_move=result.lines[0].pv[0],
        lines=lines,
    )


@app.post("/v1/engine/analyze", response_model=EngineAnalysisResponse)
async def analyze_position(request: EngineAnalyzeRequest) -> EngineAnalysisResponse:
    service = _engine_service()
    try:
        result = await service.analyze(
            request.fen,
            SearchLimits(time_ms=request.time_ms, depth=request.depth),
            request.multipv,
            request.job_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "invalid_fen_or_job", "message": str(exc)}) from exc
    except EngineError as exc:
        message = str(exc)
        status = 429 if "busy" in message.lower() else 504 if "time" in message.lower() or "timed out" in message.lower() else 502
        code = "engine_busy" if status == 429 else "engine_timeout" if status == 504 else "engine_error"
        raise HTTPException(status_code=status, detail={"code": code, "message": message}) from exc
    return _analysis_response(result)


@app.post("/v1/engine/best-move", response_model=EngineAnalysisResponse)
async def get_engine_move(request: EngineAnalyzeRequest) -> EngineAnalysisResponse:
    # Uses the same bounded analysis path so the returned move carries its evidence.
    return await analyze_position(request)


@app.post("/v1/engine/stop", response_model=EngineStopResponse)
async def stop_analysis(request: EngineStopRequest) -> EngineStopResponse:
    return EngineStopResponse(stopped=await _engine_service().stop(request.job_id), job_id=request.job_id)


@app.post("/v1/tutor/hint", response_model=TutorAnswer)
async def tutor_hint(payload: TutorHintRequest, http_request: Request) -> TutorAnswer:
    service = app.state.tutor_service
    if service is None:
        service = TutorService()
        app.state.tutor_service = service
    if payload.hint_level >= 2 and service.engine_service is None:
        try:
            service.engine_service = _engine_service()
        except HTTPException:
            # Engine is optional for guided fallback; answer must state this limitation.
            service.engine_service = None
    try:
        return await service.hint(payload, client_key=http_request.client.host if http_request.client else "local")
    except TutorRequestError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc


def _learning_service() -> LearningService:
    if os.getenv("APP_ENV", "local").casefold() == "production":
        raise HTTPException(status_code=503, detail={"code": "learning_auth_required", "message": "Learning progress is local-only until authenticated multi-user access is implemented."})
    service = app.state.learning_service
    if service is None:
        service = LearningService()
        app.state.learning_service = service
    return service


def _learning_error(exc: LearningError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)})


@app.post("/v1/learning/games", response_model=GameSaveResponse)
def save_learning_game(payload: GameSaveRequest) -> GameSaveResponse:
    try:
        return _learning_service().save_game(payload)
    except LearningError as exc:
        raise _learning_error(exc) from exc


@app.get("/v1/learning/games/{game_id}", response_model=SavedGame)
def get_learning_game(game_id: UUID, learner_id: UUID) -> SavedGame:
    try:
        return _learning_service().get_game(str(learner_id), str(game_id))
    except LearningError as exc:
        raise _learning_error(exc) from exc


@app.post("/v1/learning/attempts", response_model=AttemptReceipt)
def submit_learning_attempt(payload: AttemptSubmit) -> AttemptReceipt:
    try:
        return _learning_service().submit_attempt(payload)
    except LearningError as exc:
        raise _learning_error(exc) from exc


@app.get("/v1/learning/progress/{learner_id}", response_model=LearningProgress)
def get_learning_progress(learner_id: UUID) -> LearningProgress:
    try:
        return _learning_service().progress(str(learner_id))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "invalid_learner_id", "message": "Learner ID không hợp lệ."}) from exc


@app.get("/v1/learning/next/{learner_id}", response_model=ExerciseRecommendation)
def get_next_exercise(learner_id: UUID, include_experimental: bool = False) -> ExerciseRecommendation:
    try:
        return _learning_service().recommend(str(learner_id), include_experimental=include_experimental)
    except LearningError as exc:
        raise _learning_error(exc) from exc


@app.get("/v1/learning/reviews/{learner_id}", response_model=list[ExerciseRecommendation])
def get_due_reviews(learner_id: UUID) -> list[ExerciseRecommendation]:
    try:
        return _learning_service().due_reviews(str(learner_id))
    except LearningError as exc:
        raise _learning_error(exc) from exc


@app.get("/v1/learning/games/{game_id}/rematch", response_model=RematchResponse)
async def get_rematch_candidates(game_id: UUID, learner_id: UUID) -> RematchResponse:
    try:
        try:
            engine = _engine_service()
        except HTTPException:
            engine = None
        return await _learning_service().rematch(str(learner_id), str(game_id), engine)
    except LearningError as exc:
        raise _learning_error(exc) from exc


@app.get("/v1/learning/export/{learner_id}")
def export_learning_data(learner_id: UUID) -> Response:
    try:
        data = _learning_service().export(str(learner_id))
        return Response(content=json.dumps(data, ensure_ascii=False, default=str), media_type="application/json", headers={"Content-Disposition": "attachment; filename=xiangqi-learning-progress.json"})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "invalid_learner_id", "message": "Learner ID không hợp lệ."}) from exc


@app.delete("/v1/learning/progress/{learner_id}")
def delete_learning_progress(learner_id: UUID) -> dict[str, bool]:
    try:
        _learning_service().delete(str(learner_id))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "invalid_learner_id", "message": "Learner ID không hợp lệ."}) from exc
    return {"deleted": True}
