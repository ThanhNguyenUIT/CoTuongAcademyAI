from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ReviewStatus = Literal["draft", "experimental", "engine_validated", "reviewed", "published", "needs_review"]


class SourceRef(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    note: str = ""


class Annotation(BaseModel):
    id: str
    position_key: str
    claim: str = Field(min_length=1)
    source_refs: list[str] = Field(min_length=1)
    review_status: ReviewStatus
    version: str


class OpeningLine(BaseModel):
    id: str
    label: str
    moves_iccs: list[str]
    source_refs: list[str] = Field(min_length=1)
    review_status: ReviewStatus
    version: str


class ExerciseChoice(BaseModel):
    id: str
    text: str
    move_iccs: str = Field(min_length=4, max_length=4)
    feedback: str
    correct: bool = False
    counterplay: str = ""
    counterplay_moves_iccs: list[str] = Field(min_length=1)


class LessonExercise(BaseModel):
    id: str
    fen: str
    question: str
    skill_tags: list[str]
    rubric: list[str] = Field(min_length=1)
    hint_ladder: list[str] = Field(min_length=3, max_length=3)
    choices: list[ExerciseChoice] = Field(min_length=2)
    source_refs: list[str] = Field(min_length=1)
    review_status: ReviewStatus


class LessonStep(BaseModel):
    id: str
    title: str
    body: str
    moves_iccs: list[str] = []
    annotation_ids: list[str] = []


class Lesson(BaseModel):
    id: str
    slug: str
    title: str
    outcomes: list[str]
    steps: list[LessonStep]
    exercises: list[LessonExercise]
    content_version: str
    review_status: ReviewStatus


class OpeningKnowledge(BaseModel):
    opening_id: str
    name_vi: str
    classification_code: str
    description: str
    version: str
    review_status: ReviewStatus
    source_refs: list[SourceRef] = Field(min_length=1)
    lines: list[OpeningLine] = Field(min_length=2, max_length=3)
    annotations: list[Annotation]
    lesson: Lesson


class GraphPosition(BaseModel):
    position_key: str
    fen: str
    side_to_move: Literal["r", "b"]
    incoming_lines: list[str]


class GraphEdge(BaseModel):
    from_position_key: str
    move_iccs: str
    to_position_key: str
    line_ids: list[str]


class OpeningGraph(BaseModel):
    opening_id: str
    root_position_key: str
    positions: list[GraphPosition]
    edges: list[GraphEdge]


class OpeningDetail(BaseModel):
    opening: OpeningKnowledge
    graph: OpeningGraph
