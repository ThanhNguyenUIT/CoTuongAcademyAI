# Phase 6 — Beta readiness report

**Review date:** 2026-09-27 · **Disposition:** `READY_FOR_APPROVAL` for supervised local evaluation only; **not ready for a public or hosted beta**.

This report records prototype evidence. It is not a legal opinion, security certification, independent accessibility audit, or evidence of improved playing strength.

## Scope and threat model

- Supported evaluation shape: one trusted user on one Windows machine, frontend/backend bound to loopback, SQLite stored on that machine, Pikafish configured locally only for non-commercial use under the included upstream NNUE terms. The local learner UUID is a browser identifier, not authentication.
- The application does not implement authenticated multi-user access. Learning routes explicitly return `503 learning_auth_required` in `APP_ENV=production`; do not expose FastAPI on a public interface. The development launcher binds to `127.0.0.1`. Same-machine users/processes can access the local app and database.
- Tutor defaults to `LLM_PROVIDER=none`; authored fallback requires no provider network request. Optional OpenAI-compatible mode sends lesson context and learner text to the configured endpoint. Do not enable it for real learner data until the provider, retention, region, and user notice are approved. API key stays in the backend environment.
- Engine requests are bounded to 100–5000 ms, depth 1–20, MultiPV 1–3; engine service permits at most three active searches, sets at most two engine threads and a 128 MB hash cap. Tutor analysis uses at most 400 ms/depth 8/MultiPV 2; provider timeout is 12 seconds, response token cap 700, process-local uncached request ceiling 20/client/minute. Process-local quotas do not protect multiple workers or a public deployment.
- Existing tests cover invalid moves/FEN, unsupported tutor claims, upstream error sanitization, log privacy, production content restriction, learner export/delete/isolation and engine timeout/cancel/restart. These are regression tests, not a penetration test.

## Data and privacy notice for a local pilot

The app stores a random learner UUID in browser local storage. The backend stores that ID, validated local game moves/positions, exercise/version, selected choice, free-text reason, hint level, self-checks, observable outcome, and review schedule in `.local-data/learning.sqlite3`. There is no account, cloud sync, or analytics service.

Dashboard metrics are an instructional prototype: one point for the author's focus-aligned choice and one for entering any reason. The reason's meaning and self-check quality are not machine-scored. No Elo/mastery claim is made. Use Export to save JSON and Delete to remove the current learner's records. Deletion is local and should be used before sharing the device; operating-system backups may retain prior copies. The optional LLM provider would receive submitted learning context; it is off by default.

Before inviting beta learners, present this notice and obtain explicit opt-in for the study and any provider use. Do not collect names/contact details in the MVP. Do not enroll minors until appropriate guardian consent and a privacy/legal review are complete.

## Proposed small beta protocol (not yet run)

1. After written content-rights clearance and a chess educator review, invite 5–10 adults to a supervised one-session pilot. Explain local storage/export/delete and optional provider processing; record consent separately from game data.
2. Use a fixed, versioned pre-test of threat recognition and response prediction, then the current course, then a difficulty-matched held-out post-test. Score move choice and a short human-reviewed explanation using a rubric fixed before data collection.
3. Collect only anonymous session IDs, completion, answer/rubric outcomes, time, and voluntary product feedback. Keep names/contact/consent records separately. Delete pilot records at the end of the agreed retention window; do not present the small sample as proof of learning efficacy.
4. Stop enrollment on any leaked secret, cross-learner data access, engine process runaway, incorrect rules result, lost records, or unlicensed content discovery. Preserve the incident report without retaining learner free text.
5. Report cohort size, missing responses, confidence/uncertainty, and pre/post task versions. Do not claim learning gains unless a suitable analysis supports that claim.

**Pilot evidence:** No beta cohort, consent flow, educator review, or pre/post result exists in this workspace. The browser walkthrough in `state/HANDOFF.md` was a local functional smoke using synthetic data and was cleaned afterward.

## Evidence snapshot

| Area | Evidence | Result and limit |
| --- | --- | --- |
| Frontend security dependencies | `npm audit --json` after upgrading Vitest toolchain | 0 reported vulnerabilities in the current lockfile; no continuous audit service configured |
| Python environment | `.venv\Scripts\python.exe -m pip check` | No broken requirements; this does not scan CVEs |
| Engine/resource bounds | `backend/app/engine/service.py`, engine integration/unit tests | Per-process bounds only; not a production worker or memory benchmark |
| Tutor safety/quota | `backend/app/tutor/service.py`, provider timeout and security tests | Fallback works with provider off; quota is process-local |
| Local smoke/load | See `state/HANDOFF.md` for exact `scripts/load_smoke.py` command and output | Loopback hardware only; not a beta load target or SLO |
| Accessibility/layout | Keyboard semantics and responsive CSS exist; automated frontend tests cover keyboard destination announcement | Mobile/touch screen-reader UAT and independent WCAG review remain outstanding |
| Content | Source links and `experimental` review status recorded in YAML | No educator-approved lesson and no explicit redistribution license recorded |

## Release gates still open

- Rights holder permission/review for all course text, sourced examples, and any bundled engine/weights. The current local Pikafish NNUE prohibits commercial use absent permission; neither engine binary/weights nor learner data are shipped in the frontend bundle.
- A real, isolated beta environment, multi-worker quota/auth review, load/security/accessibility report, and rollback rehearsal.
- Educator-approved MVP content and a real consenting learner cohort using pre/post held-out tasks.
- A supported distribution target and reproducible release source revision. This workspace has no `.git` metadata; no commit/tag or release package was created.

Do not set `APP_ENV=production`, bind a public host, redistribute the engine/weights/content, or represent the service as ready for public beta until the relevant gates are closed. Public deployment was not performed.
