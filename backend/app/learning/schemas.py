from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AttemptSubmit(BaseModel):
    learner_id: UUID
    attempt_id: UUID
    game_id: UUID
    lesson_id: str = Field(min_length=1, max_length=120)
    exercise_id: str = Field(min_length=1, max_length=120)
    exercise_version: str = Field(min_length=1, max_length=80)
    selected_move: str = Field(pattern=r"^[a-i][0-9][a-i][0-9]$")
    learner_reason: str = Field(default="", max_length=500)
    hint_level: int = Field(default=0, ge=0, le=3)
    rubric_self_checks: list[str] = Field(default_factory=list, max_length=12)
    include_experimental: bool = False


class AttemptOutcome(BaseModel):
    status: Literal["focus_aligned", "needs_practice"]
    focus_aligned: bool
    reason_submitted: bool
    points: int = Field(ge=0, le=2)
    points_possible: int = 2
    rubric_self_checks: list[str]
    review_due_at: datetime
    repeated_error_count: int = Field(ge=0)


class AttemptReceipt(BaseModel):
    attempt_id: UUID
    game_id: UUID
    lesson_id: str
    exercise_id: str
    exercise_version: str
    skill_ids: list[str]
    outcome: AttemptOutcome
    created_at: datetime
    duplicate: bool = False


class GameSaveRequest(BaseModel):
    learner_id: UUID
    game_id: UUID
    starting_fen: str = Field(min_length=10, max_length=200)
    moves_iccs: list[str] = Field(max_length=300)
    ended: bool = False


class GameSaveResponse(BaseModel):
    game_id: UUID
    ply_count: int
    saved: bool = True


class SavedGame(BaseModel):
    learner_id: UUID
    game_id: UUID
    starting_fen: str
    moves_iccs: list[str]
    positions_fens: list[str]
    ended: bool
    updated_at: datetime


class SkillProgress(BaseModel):
    skill_id: str
    name: str
    attempts: int = Field(ge=0)
    focus_aligned: int = Field(ge=0)
    sample_size: int = Field(ge=0)
    focus_rate: float | None = Field(default=None, ge=0, le=1)
    repeated_errors: int = Field(ge=0)
    next_review_at: datetime | None = None


class LearningProgress(BaseModel):
    learner_id: UUID
    total_attempts: int = Field(ge=0)
    skills: list[SkillProgress]
    due_reviews: int = Field(ge=0)
    updated_at: datetime | None = None


class ExerciseRecommendation(BaseModel):
    lesson_id: str
    exercise_id: str
    exercise_version: str
    question: str
    skill_ids: list[str]
    reason: str
    scheduled_for: datetime | None = None
    include_experimental: bool


class RematchCandidate(BaseModel):
    game_id: UUID
    ply: int = Field(ge=1)
    fen: str
    move_iccs: str
    reason: str
    engine_marked: bool = False
    evidence: str


class RematchResponse(BaseModel):
    game_id: UUID
    candidates: list[RematchCandidate] = Field(max_length=3)
    engine_status: Literal["available", "unavailable"]


class ExportBundle(BaseModel):
    learner_id: UUID
    exported_at: datetime
    attempts: list[AttemptReceipt]
    games: list[GameSaveRequest]
