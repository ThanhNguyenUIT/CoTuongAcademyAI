-- SQLite schema for the versioned Opening Lab knowledge graph.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY,
    position_key TEXT NOT NULL UNIQUE,
    fen_canonical TEXT NOT NULL,
    side_to_move TEXT NOT NULL CHECK (side_to_move IN ('r', 'b'))
);

CREATE TABLE IF NOT EXISTS openings (
    id TEXT PRIMARY KEY,
    name_vi TEXT NOT NULL,
    classification_code TEXT NOT NULL,
    description TEXT NOT NULL,
    version TEXT NOT NULL,
    review_status TEXT NOT NULL CHECK (review_status IN ('draft', 'experimental', 'engine_validated', 'reviewed', 'published', 'needs_review'))
);

CREATE TABLE IF NOT EXISTS opening_sources (
    id TEXT PRIMARY KEY,
    opening_id TEXT NOT NULL REFERENCES openings(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS position_edges (
    id INTEGER PRIMARY KEY,
    from_position_id INTEGER NOT NULL REFERENCES positions(id),
    move_iccs TEXT NOT NULL CHECK (length(move_iccs) = 4),
    to_position_id INTEGER NOT NULL REFERENCES positions(id),
    UNIQUE (from_position_id, move_iccs)
);

CREATE TABLE IF NOT EXISTS opening_lines (
    id TEXT PRIMARY KEY,
    opening_id TEXT NOT NULL REFERENCES openings(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    version TEXT NOT NULL,
    review_status TEXT NOT NULL,
    source_refs_json TEXT NOT NULL,
    edge_sequence_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS annotations (
    id TEXT PRIMARY KEY,
    opening_id TEXT NOT NULL REFERENCES openings(id) ON DELETE CASCADE,
    position_id INTEGER NOT NULL REFERENCES positions(id),
    claim TEXT NOT NULL,
    source_refs_json TEXT NOT NULL,
    review_status TEXT NOT NULL,
    version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lessons (
    id TEXT PRIMARY KEY,
    opening_id TEXT NOT NULL REFERENCES openings(id) ON DELETE CASCADE,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    outcomes_json TEXT NOT NULL,
    steps_json TEXT NOT NULL,
    content_version TEXT NOT NULL,
    review_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exercises (
    id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    fen TEXT NOT NULL,
    rubric_json TEXT NOT NULL,
    accepted_lines_json TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    source_refs_json TEXT NOT NULL,
    review_status TEXT NOT NULL
);
