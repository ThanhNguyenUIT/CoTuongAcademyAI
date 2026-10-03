"""Create and integrity-check a SQLite backup of local learner data."""

from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path


def backup(source: Path, destination: Path) -> None:
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Learning database not found: {source}")
    if source == destination:
        raise ValueError("Backup destination must differ from the source database.")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing backup: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sqlite3.connect(source) as source_db, sqlite3.connect(destination) as backup_db:
            source_db.backup(backup_db)
            result = backup_db.execute("PRAGMA integrity_check").fetchone()
            if result is None or result[0] != "ok":
                raise sqlite3.DatabaseError(f"Backup integrity check failed: {result}")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    print(f"Backup verified: {destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new backup file; existing files are never overwritten")
    args = parser.parse_args()
    source = Path(os.getenv("LEARNING_DB_PATH", ".local-data/learning.sqlite3"))
    backup(source, args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
