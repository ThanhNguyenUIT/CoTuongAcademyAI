from pydantic import BaseModel, Field


class PositionRequest(BaseModel):
    fen: str = Field(min_length=1, max_length=256)


class ApplyMoveRequest(PositionRequest):
    move: str = Field(min_length=4, max_length=4)
    history_fens: list[str] = Field(default_factory=list, max_length=1024)


class RulesResponse(BaseModel):
    fen: str
    moves: list[str]
    status: str
    in_check: bool
    checked_general: str | None
    repetition_count: int | None = None

