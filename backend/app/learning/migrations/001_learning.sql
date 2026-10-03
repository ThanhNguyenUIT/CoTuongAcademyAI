PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS learners (
    learner_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS games (
    game_id TEXT PRIMARY KEY,
    learner_id TEXT NOT NULL REFERENCES learners(learner_id) ON DELETE CASCADE,
    starting_fen TEXT NOT NULL,
    moves_json TEXT NOT NULL,
    positions_json TEXT NOT NULL,
    ended INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attempts (
    attempt_id TEXT NOT NULL,
    learner_id TEXT NOT NULL REFERENCES learners(learner_id) ON DELETE CASCADE,
    game_id TEXT NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    idempotency_hash TEXT NOT NULL,
    lesson_id TEXT NOT NULL,
    exercise_id TEXT NOT NULL,
    exercise_version TEXT NOT NULL,
    selected_move TEXT NOT NULL,
    learner_reason TEXT NOT NULL,
    hint_level INTEGER NOT NULL,
    skill_ids_json TEXT NOT NULL,
    outcome_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY(learner_id, attempt_id)
);

CREATE INDEX IF NOT EXISTS idx_attempts_learner_skill
    ON attempts(learner_id, created_at);

CREATE TABLE IF NOT EXISTS review_schedule (
    learner_id TEXT NOT NULL REFERENCES learners(learner_id) ON DELETE CASCADE,
    exercise_id TEXT NOT NULL,
    skill_id TEXT NOT NULL,
    interval_days INTEGER NOT NULL,
    repetitions INTEGER NOT NULL,
    due_at TEXT NOT NULL,
    last_attempt_id TEXT NOT NULL,
    PRIMARY KEY(learner_id, exercise_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_review_due
    ON review_schedule(learner_id, due_at);
