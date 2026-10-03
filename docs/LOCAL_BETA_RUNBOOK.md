# Local supervised beta runbook

This runbook supports local evaluation only. It is not a hosted deployment guide. Never bind this prototype to `0.0.0.0` or a public interface. Public beta remains blocked on the gates in [`BETA_READINESS.md`](BETA_READINESS.md).

## Start on Windows

From the project root in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
$env:APP_ENV = 'development'
$env:LLM_PROVIDER = 'none'
$env:ENGINE_COMMAND = (Resolve-Path '.local-engines/Pikafish-Windows-x86-64-universal.exe').Path
npm run dev
```

Place the locally licensed `pikafish.nnue` next to the executable. Use this weight only for legal, non-commercial evaluation under its included terms unless written permission says otherwise. Without `ENGINE_COMMAND`, rules and authored fallback still work; engine analysis/rematch reports unavailable. The default tutor does not call a network provider.

The dev launcher binds frontend and backend to loopback. Uvicorn reload is disabled because the Windows selector loop cannot manage the engine's asyncio subprocess. Restart the backend after Python changes.

## Smoke and bounded local load check

In another PowerShell window with the virtual environment active:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-WebRequest http://127.0.0.1:5173/ -UseBasicParsing
python scripts/load_smoke.py --mode health --requests 20 --concurrency 5
python scripts/load_smoke.py --mode engine --requests 12 --concurrency 2 --engine-time-ms 300 --depth 6
```

The script prints HTTP status counts, total time, client p50/p95/max, and engine elapsed p50/p95. Engine concurrency is intentionally capped at three. Results describe only this machine and run. Never call them hosted beta capacity or an SLO.

## Local data backup and recovery

Learner records are in `.local-data/learning.sqlite3`. Treat the database and backups as personal learning data. Stop the app before copying files manually. A new snapshot can be made and integrity-checked without overwriting an existing backup:

```powershell
python scripts/backup_learning_db.py .local-data/backups/learning-YYYYMMDD-HHMMSS.sqlite3
```

For recovery, stop the app, preserve the current database under a different name, copy the selected verified snapshot to `.local-data/learning.sqlite3`, then restart and check `/health` and dashboard/export. Roll back the restore by stopping the app and putting the preserved database back. Do not restore test/synthetic learner data into a pilot profile.

This is a manual local procedure; automatic rotation, encrypted backups, off-site recovery, and a rehearsed production rollback are not implemented.

## Shutdown and incidents

Stop both processes with `Ctrl+C` in the `npm run dev` terminal. For a local engine hang, stop the backend process and restart it; engine service tests cover cancellation/restart. Do not delete the database to recover an engine.

Stop a pilot immediately if legal-move results are wrong, learner records appear under the wrong local profile, an engine fails to stop, a secret/free-text answer appears in logs, or unlicensed content is found. Record time, app revision if available, sanitized symptom, action taken, and affected synthetic/session IDs; do not copy learner explanations into the incident log.

## Rollback boundary

No deployable release artifact, Git tag, database migration rollback, or public endpoint exists. The current workspace lacks Git metadata. A rollback means returning local source files and SQLite from a separately preserved copy. Do not claim production rollback readiness until a release revision and rehearsal exist.
