from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from backend.app.knowledge.schemas import ReviewStatus


class TutorHintRequest(BaseModel):
    lesson_id: str = Field(min_length=1, max_length=100)
    exercise_id: str = Field(min_length=1, max_length=100)
    fen: str = Field(min_length=1, max_length=256)
    hint_level: int = Field(ge=1, le=3)
    previous_hint_level: int = Field(default=0, ge=0, le=2)
    learner_move: str | None = Field(default=None, pattern=r"^[a-i][0-9][a-i][0-9]$", max_length=4)
    learner_reason: str = Field(default="", max_length=1000)
    include_experimental: bool = False

    @model_validator(mode="after")
    def validate_progression(self):
        if self.hint_level != self.previous_hint_level + 1:
            raise ValueError("Hints must be requested one level at a time.")
        if self.hint_level == 3 and not self.learner_move:
            raise ValueError("Submit a candidate move before requesting hint level 3.")
        if self.hint_level == 3 and not self.learner_reason.strip():
            raise ValueError("Explain your candidate before requesting hint level 3.")
        return self


class TutorEvidence(BaseModel):
    ref: str
    kind: Literal["lesson", "source", "rules", "engine"]
    review_status: ReviewStatus | None = None
    version: str | None = None
    source_refs: list[str] = Field(default_factory=list)
    engine_id: str | None = None
    engine_version: str | None = None
    depth: int | None = None
    score_cp_side_to_move: int | None = None
    mate_in_side_to_move: int | None = None
    moves_iccs: list[str] = Field(default_factory=list)


class TutorClaim(BaseModel):
    text: str = Field(min_length=1, max_length=700)
    evidence_refs: list[str] = Field(min_length=1)


class TutorAnswer(BaseModel):
    contract_version: Literal["1"] = "1"
    trace_id: str
    context_digest: str
    lesson_id: str
    exercise_id: str
    position_fen: str
    hint_level: int = Field(ge=1, le=3)
    question: str
    claims: list[TutorClaim] = Field(min_length=1, max_length=5)
    candidate_moves: list[str] = Field(default_factory=list, max_length=3)
    evidence: list[TutorEvidence] = Field(default_factory=list)
    uncertainty: str = Field(min_length=1, max_length=500)
    provider: str
    fallback: bool
    engine_status: Literal["available", "unavailable", "not_requested"]

    @field_validator("position_fen")
    @classmethod
    def nonempty_fen(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def claims_have_resolvable_evidence(self):
        refs = {item.ref for item in self.evidence}
        if any(not set(claim.evidence_refs) <= refs for claim in self.claims):
            raise ValueError("Every tutor claim must point to evidence in the response.")
        return self


class TutorDraftClaim(BaseModel):
    text: str = Field(min_length=1, max_length=700)
    evidence_refs: list[str] = Field(default_factory=list)


class TutorProviderDraft(BaseModel):
    claims: list[TutorDraftClaim] = Field(min_length=1, max_length=5)
    candidate_moves: list[str] = Field(default_factory=list, max_length=8)
    uncertainty: str = Field(default="Chưa đủ chứng cứ để kết luận.", max_length=500)


class TutorAnnotationContext(BaseModel):
    annotation_id: str
    claim: str
    source_refs: list[str]
    review_status: ReviewStatus
    version: str


class TutorContext(BaseModel):
    trace_id: str
    lesson_id: str
    exercise_id: str
    position_fen: str
    hint_level: int
    question: str
    learning_outcomes: list[str]
    exercise_rubric: list[str]
    choice_feedback: list[str]
    reviewed_annotations: list[TutorAnnotationContext]
    learner_move: str | None
    learner_reason: str
    off_theory: bool
    evidence: list[TutorEvidence]
    verified_candidate_moves: list[str]
    engine_lines: list[list[str]]
    content_review_status: ReviewStatus
    content_version: str


class TutorProviderError(RuntimeError):
    """A provider failure with no credential or upstream response details."""
