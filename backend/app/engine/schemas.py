from pydantic import BaseModel, Field


class EngineAnalyzeRequest(BaseModel):
    fen: str = Field(min_length=1, max_length=256)
    time_ms: int = Field(default=1000, ge=100, le=5000)
    depth: int = Field(default=12, ge=1, le=20)
    multipv: int = Field(default=3, ge=1, le=3)
    job_id: str | None = Field(default=None, min_length=1, max_length=80)


class EngineLineResponse(BaseModel):
    multipv: int
    depth: int
    score_cp_side_to_move: int | None
    mate_in_side_to_move: int | None
    score_cp_red: int | None
    mate_in_red: int | None
    pv: list[str]


class EngineAnalysisResponse(BaseModel):
    engine_id: str
    engine_version: str
    protocol: str
    position_fen: str
    limits: dict[str, int]
    score_perspective: str
    elapsed_ms: int
    is_complete: bool
    best_move: str
    lines: list[EngineLineResponse]


class EngineStopRequest(BaseModel):
    job_id: str = Field(min_length=1, max_length=80)


class EngineStopResponse(BaseModel):
    stopped: bool
    job_id: str

