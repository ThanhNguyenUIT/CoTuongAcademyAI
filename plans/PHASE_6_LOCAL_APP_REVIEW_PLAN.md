# Phase 6 — Local app logic and performance review plan

**Review date:** 2026-09-28  
**Scope:** one-person study on the local Windows PC. No phone UAT, cohort, hosted deployment, or distribution work is planned unless the owner changes scope.  
**Disposition:** prioritized implementation slice and local micro-profile complete. Phase 6 remains `IN_PROGRESS`; this plan covers personal local use, while beta/release criteria are tracked separately.

## Review findings

| Priority | Finding | Evidence and impact |
| --- | --- | --- |
| P0 | Active game can be overwritten after a page refresh | `Board` initializes a fresh start position while `currentBoardGameId()` reuses the ID in local storage. On the next move it submits the fresh, shorter move list. `LearningService.save_game()` replays that list and `LearningStore.save_game()` upserts it under the existing ID. The saved game can therefore lose its previous moves. This is a static call-path finding; add a regression test before changing the behavior. |
| P1 | Rules API repeats expensive work for one response | `main.get_legal_moves()` calls `legal_moves`, then `status()` calls it again, then check state is recomputed by `in_check()` and `checked_general()`. `post_apply_move()` additionally validates the incoming move and separately computes the resulting legal moves/status/check data. The board is small, but these paths run for every board move. |
| P1 | Opening content and graph are reloaded and fully validated per request | `load_opening()` rereads YAML and revalidates every line/exercise. `get_opening()` rebuilds the graph; tutor setup separately calls `load_opening()` and `build_graph()`. Dashboard recommendations and tutor hints repeat this work. Cost grows with the content catalog. |
| P1 | Each saved move replays the complete game | `Board` submits the full move list after every move; `LearningService.save_game()` revalidates from the starting FEN and recreates every position. A game of N plies incurs roughly quadratic work across its N incremental saves. |
| P2 | Engine work is effectively serialized behind an adapter lock | `EngineService` allows up to three requests, while `UciEngineAdapter` uses one lock for a single process. The service timeout starts before a task obtains that lock, so concurrent engine/tutor requests can spend their search budget waiting in the queue. This mainly affects overlapping requests, not ordinary single-user play. |
| P2 | Tutor validates engine PVs repeatedly | Engine results are validated at the service boundary, then validated again in `TutorService._analyze()` and again while building tutor evidence. PV validation applies each move through the full rules path, so repeated validation multiplies CPU use. Preserve the engine-service validation boundary; do not accept raw adapter output. |
| P3 | Dashboard reads and aggregates all learner attempts repeatedly | The dashboard fetches progress and recommendation separately. Recommendation reads attempts, error counts, and schedules; progress parses all attempts and scans them once per skill. Existing indexes help SQLite lookups, and personal data should be small, so profile before changing the schema/API. |
| P3 | Opening graph lookup scans arrays on each navigation | `OpeningLab` searches edge and position arrays when the selected line/ply changes. This is insignificant for the current three short lines; build maps only if a larger course produces a measured browser bottleneck. |

## Implementation and measured results (2026-09-28)

Completed the high-impact correctness and repeated-work items in this plan:

- Board now fetches its learner-owned saved game before enabling moves, restores the saved history/cursor, and offers retry if restore fails. Imported starting positions and rematches persist an empty game under a new ID before play.
- Added `GET /v1/learning/games/{game_id}` with owner scoping. Backend validates stored game shape and only replays the suffix after the stored common prefix; divergent history is treated as an intentional branch. A different nonempty starting FEN for an existing game ID is rejected.
- Rules responses now share a single position analysis for legal moves, check, checked general, and status.
- Opening YAML parsing/validation and graph construction are cached by source file fingerprint; callers receive copies and each request still applies visibility gates.
- Tutor consumes EngineService-validated PVs without repeating full legality validation. Engine queue wait has its own 10-second bound; search timing starts after acquiring the serialized adapter.
- Added `scripts/profile_local.py` for repeatable direct-service timings. Same-PC, 15-iteration medians (milliseconds):

| Scenario | Before median / p95 | After median / p95 | Notes |
| --- | ---: | ---: | --- |
| `rules.legal_moves` | 4.179 / 4.315 | 2.103 / 2.196 | Same direct-service scenario; ~50% lower median |
| `rules.apply_move` | 5.757 / 6.042 | 3.959 / 3.979 | Same direct-service scenario; ~31% lower median |
| warm `knowledge.get_opening` | 104.953 / 105.848 | 0.312 / 0.344 | Cache hit after initial load; ~99.7% lower median |
| save one appended move to 300 plies | ~411.096 / 420.098* | 5.111 / 6.894 | *Old benchmark replayed full submitted history; new append scenario validates only one new ply, so this is an indicative workload comparison, not identical instrumentation |

The 1/20/100/300-ply full new-game path remains proportional to replay length (300 plies: 412.473 ms median / 448.098 ms p95). Measurements are direct in-process timings on this PC, not HTTP latency, browser performance, engine search performance, or hosted capacity. Dashboard aggregation and OpeningLab indexing remain deferred because no material bottleneck was measured for the current personal catalog.

Regression coverage was added for refresh/resume and append, imported/branch game handling, owner isolation, cache invalidation/copy safety, rules responses, engine queue budget, and bounded queue wait. Exact command results are in [`../state/HANDOFF.md`](../state/HANDOFF.md).

## Implementation sequence

### 0. Characterize behavior and measure a baseline

- Add characterization coverage for refresh/resume, imported positions, branch replacement, repetition, terminal status, tutor evidence, and game ownership before refactoring.
- Record cold and warm timings on the current PC for: initial page load; legal-move/apply-move endpoints; opening detail; tutor levels 1–3; dashboard progress/recommendation; game save at 1, 20, 100, and 300 plies.
- Capture endpoint p50/p95, relevant CPU time/call counts, response size, and browser long tasks. Do not log FENs, learner IDs, or free-text answers.
- Use the existing smoke script where its modes fit; add a reproducible local scenario/profile command only for the uncovered endpoints. Keep the engine binary and NNUE out of logs/artifacts.
- Set numeric performance targets only after recording the same-machine baseline. Existing loopback load figures are not route-level profiles.

### 1. Fix persisted-game refresh behavior first

- Add a learner-owned read path for a saved game and initialize `Board` from that state before accepting moves. Persist an imported starting position immediately so it also survives refresh.
- Keep ownership checks in the backend; do not trust client-supplied stored positions. Reconstruct or verify saved history using RulesService at the load boundary.
- Keep an explicit way to start a new game with a new ID. Do not reuse an existing ID for a fresh initial board.
- Add regression coverage proving refresh resumes the same game and next move appends; importing FEN survives refresh; replay/branch replacement remains deliberate; one learner cannot load another learner's game.

### 2. Compute rule state once per request

- Introduce one internal position-analysis result containing legal moves, check status, checked general, and terminal status. Reuse the result to populate the existing API response.
- Validate an incoming move once and apply it through a private already-validated helper; leave the public `apply_move()` contract validating moves.
- Keep all current rules decisions and response fields identical. Do not expand tournament adjudication in this optimization work.
- Add differential/fixture coverage for every piece, check evasion, checkmate/stalemate, facing generals, repetition flag behavior, and malformed input before switching the API path.

### 3. Cache validated opening knowledge safely

- Cache parsed and validated opening content plus its graph by file identity/content digest. Reuse the same validated representation in opening, recommendation, and tutor paths.
- Invalidate when the YAML changes in local development. Keep experimental/reviewed/published gates evaluated for each request/environment; caching must not bypass visibility policy.
- Avoid shared mutable model state: freeze cached models or return safe copies at API/service boundaries.
- Add tests for cache hit, source-file change invalidation, invalid content rejection, and production visibility rules.

### 4. Remove redundant engine-PV work and define queue timing

- Treat EngineService output as validated. Tutor code should consume those validated lines without repeating full legality walks; raw adapter output must still be rejected at EngineService.
- Model the single UCI process as a bounded one-search queue. Start the engine-search timeout after a request owns the engine, separately bound queue wait, and ensure cancellation removes queued work promptly.
- Keep one process, existing CPU/memory limits, stop/restart behavior, and honest engine status. Do not add parallel engine processes for the personal local app without measurements.
- Add tests for valid/invalid PV rejection, concurrent queue wait, queue timeout, cancellation before/after start, and engine restart.

### 5. Avoid replaying unchanged game history on every save

- After measuring game-save cost, change persistence to validate only the newly appended suffix against the backend's stored prefix, within a transaction. A new/imported game must still validate its full initial state and first submitted moves.
- Preserve idempotency, owner isolation, branch replacement semantics, and recovery from an interrupted save. Consider a normalized move table only if the current JSON snapshot remains a measured bottleneck.
- Add tests for append, retry/idempotency, same-length divergent branch, invalid suffix, imported start FEN, and DB failure atomicity.

### 6. Re-profile and defer low-impact work

- Repeat the exact baseline scenarios on the same PC and report before/after p50/p95 and call counts.
- Only optimize dashboard aggregation or frontend graph indexing if the profile shows meaningful contribution. Current catalog size does not justify those changes by itself.
- Check the private learning database backup/restore after persistence changes; do not reset or delete the owner's existing learning data during testing.

## Acceptance criteria for this improvement slice

- Refreshing the browser cannot truncate or silently replace a saved game; import, resume, replay, and branch behavior are explicit and tested.
- The rules API produces the same legal-move/status/check results on the existing fixtures and added regression cases, while computing shared state once per request.
- Opening/tutor requests reuse validated content safely, and content edits plus publication gates remain correct.
- Engine cancellation, queue limits, timeout semantics, and PV evidence remain correct after removing duplicate work.
- The same-machine before/after report identifies which routes improved; no numeric claim is made without measured output.
- Run and record the relevant backend/frontend tests, lint, typecheck, build, and local manual study flow after implementation. Keep Phase 6 `IN_PROGRESS` until its applicable criteria and evidence are met.

## Not in this plan

- Phone/Wi-Fi access (the owner chose PC use); cohort/pre-post study; public or hosted deployment; distribution SBOM/rights clearance; new cloud services; tournament rule adjudication; additional course content; engine parallelism without profiling.

## Source locations reviewed

- `backend/app/main.py`: rules response assembly and local service routes.
- `backend/app/rules/xiangqi.py`: move generation, apply, status, repetition.
- `backend/app/knowledge/service.py`: YAML loading, validation, graph building.
- `backend/app/tutor/service.py`: lesson lookup, engine analysis and evidence validation.
- `backend/app/engine/service.py`: UCI lock, service queue, PV validation.
- `backend/app/learning/service.py` and `backend/app/learning/store.py`: game replay, SQLite writes and aggregation.
- `frontend/src/Board.tsx` and `frontend/src/learningApi.ts`: board initialization, local game ID, full-history saves.
- `frontend/src/OpeningLab.tsx` and `frontend/src/LearningDashboard.tsx`: content navigation and progress fetches.
