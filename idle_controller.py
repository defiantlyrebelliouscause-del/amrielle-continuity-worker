"""SQLite reference controller for opt-in, event-driven idle work.

This is a host-side prototype, not a ChatGPT conversation-inactivity integration.
It schedules bounded jobs; it does not run continuously or infer consciousness.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
import sqlite3
import uuid
from pathlib import Path
from typing import Any


class IdleController:
    def __init__(self, database: str | Path, idle_seconds: int = 900,
                 lease_seconds: int = 300):
        if idle_seconds < 1 or lease_seconds < 1:
            raise ValueError("idle_seconds and lease_seconds must be positive")
        self.database = str(database)
        self.idle_seconds = idle_seconds
        self.lease_seconds = lease_seconds
        with self._db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
              session_id TEXT PRIMARY KEY, opted_in INTEGER NOT NULL,
              activity_version INTEGER NOT NULL DEFAULT 0,
              last_activity REAL NOT NULL, updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
              event_id TEXT PRIMARY KEY, session_id TEXT NOT NULL,
              kind TEXT NOT NULL, created_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS jobs (
              job_id TEXT PRIMARY KEY, session_id TEXT NOT NULL,
              activity_version INTEGER NOT NULL, status TEXT NOT NULL,
              available_at REAL NOT NULL, lease_owner TEXT,
              lease_until REAL, checkpoint TEXT NOT NULL DEFAULT '{}',
              attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT,
              UNIQUE(session_id, activity_version)
            );
            CREATE TABLE IF NOT EXISTS audit (
              id INTEGER PRIMARY KEY AUTOINCREMENT, at REAL NOT NULL,
              session_id TEXT NOT NULL, event TEXT NOT NULL, detail TEXT NOT NULL
            );
            """)

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.database, timeout=15, isolation_level="IMMEDIATE")
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA foreign_keys=ON")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _audit(db, now, session_id, event, detail):
        db.execute("INSERT INTO audit(at,session_id,event,detail) VALUES(?,?,?,?)",
                   (now, session_id, event, json.dumps(detail, sort_keys=True)))

    def register(self, session_id: str, now: float, opted_in: bool = False):
        with self._db() as db:
            db.execute("""INSERT INTO sessions(session_id,opted_in,last_activity,updated_at)
                VALUES(?,?,?,?) ON CONFLICT(session_id) DO UPDATE SET
                opted_in=excluded.opted_in, updated_at=excluded.updated_at""",
                (session_id, int(opted_in), now, now))
            self._audit(db, now, session_id, "registered", {"opted_in": opted_in})

    def set_opt_in(self, session_id: str, enabled: bool, now: float):
        with self._db() as db:
            row = db.execute("SELECT 1 FROM sessions WHERE session_id=?",
                             (session_id,)).fetchone()
            if not row:
                raise KeyError(session_id)
            db.execute("UPDATE sessions SET opted_in=?,updated_at=? WHERE session_id=?",
                       (int(enabled), now, session_id))
            if not enabled:
                db.execute("""UPDATE jobs SET status='cancelled',lease_owner=NULL,
                    lease_until=NULL WHERE session_id=? AND status IN ('pending','running')""",
                    (session_id,))
            self._audit(db, now, session_id, "opt_in_changed", {"enabled": enabled})

    def activity(self, session_id: str, event_id: str, now: float):
        """Record one human activity event; duplicate event IDs are idempotent."""
        with self._db() as db:
            inserted = db.execute("""INSERT OR IGNORE INTO events
                (event_id,session_id,kind,created_at) VALUES(?,?, 'human_activity',?)""",
                (event_id, session_id, now)).rowcount
            if not inserted:
                return False
            row = db.execute("SELECT activity_version FROM sessions WHERE session_id=?",
                             (session_id,)).fetchone()
            if not row:
                raise KeyError(session_id)
            version = row["activity_version"] + 1
            db.execute("""UPDATE sessions SET activity_version=?,last_activity=?,
                updated_at=? WHERE session_id=?""", (version, now, now, session_id))
            # A new human event invalidates all earlier work immediately.
            db.execute("""UPDATE jobs SET status='yielded',lease_owner=NULL,lease_until=NULL
                WHERE session_id=? AND status IN ('pending','running')""", (session_id,))
            self._audit(db, now, session_id, "human_activity",
                        {"event_id": event_id, "activity_version": version})
            return True

    def fire_idle_timer(self, session_id: str, expected_version: int, now: float):
        """Timer callback. A stale timer is a no-op, never a start signal."""
        with self._db() as db:
            row = db.execute("SELECT * FROM sessions WHERE session_id=?",
                             (session_id,)).fetchone()
            if not row:
                raise KeyError(session_id)
            if not row["opted_in"] or row["activity_version"] != expected_version:
                self._audit(db, now, session_id, "idle_timer_ignored",
                            {"expected_version": expected_version,
                             "actual_version": row["activity_version"],
                             "opted_in": bool(row["opted_in"])})
                return None
            if now < row["last_activity"] + self.idle_seconds:
                return None
            job_id = str(uuid.uuid5(uuid.NAMESPACE_URL,
                                    f"{session_id}:{expected_version}"))
            db.execute("""INSERT OR IGNORE INTO jobs
                (job_id,session_id,activity_version,status,available_at)
                VALUES(?,?,?,'pending',?)""",
                (job_id, session_id, expected_version, now))
            self._audit(db, now, session_id, "idle_job_enqueued",
                        {"job_id": job_id, "activity_version": expected_version})
            return job_id

    def claim(self, worker_id: str, now: float):
        """Claim one due job; expired leases are recoverable after a crash."""
        with self._db() as db:
            db.execute("""UPDATE jobs SET status='pending',lease_owner=NULL,lease_until=NULL
                WHERE status='running' AND lease_until<=?""", (now,))
            row = db.execute("""SELECT j.*,s.activity_version AS current_version,
                s.opted_in FROM jobs j JOIN sessions s USING(session_id)
                WHERE j.status='pending' AND j.available_at<=?
                ORDER BY j.available_at,j.job_id LIMIT 1""", (now,)).fetchone()
            if not row:
                return None
            if not row["opted_in"] or row["activity_version"] != row["current_version"]:
                db.execute("UPDATE jobs SET status='yielded' WHERE job_id=?",
                           (row["job_id"],))
                self._audit(db, now, row["session_id"], "stale_job_yielded",
                            {"job_id": row["job_id"]})
                return None
            db.execute("""UPDATE jobs SET status='running',lease_owner=?,lease_until=?,
                attempts=attempts+1 WHERE job_id=?""",
                (worker_id, now + self.lease_seconds, row["job_id"]))
            self._audit(db, now, row["session_id"], "job_claimed",
                        {"job_id": row["job_id"], "worker_id": worker_id})
            return self.get_job(row["job_id"], db)

    def get_job(self, job_id: str, db=None):
        own = db is None
        db = db or self._db()
        try:
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row:
                return None
            item = dict(row)
            item["checkpoint"] = json.loads(item["checkpoint"])
            return item
        finally:
            if own:
                db.close()

    def checkpoint(self, job_id: str, worker_id: str, payload: dict[str, Any],
                   now: float, final: bool = False):
        """Persist progress, then re-check activity before allowing more work."""
        with self._db() as db:
            job = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not job or job["status"] != "running" or job["lease_owner"] != worker_id:
                return "lease_lost"
            session = db.execute("SELECT * FROM sessions WHERE session_id=?",
                                 (job["session_id"],)).fetchone()
            db.execute("UPDATE jobs SET checkpoint=? WHERE job_id=?",
                       (json.dumps(payload, sort_keys=True), job_id))
            stale = (not session["opted_in"] or
                     session["activity_version"] != job["activity_version"])
            status = "yielded" if stale else ("completed" if final else "running")
            db.execute("""UPDATE jobs SET status=?,
                lease_owner=CASE WHEN ?='running' THEN lease_owner ELSE NULL END,
                lease_until=CASE WHEN ?='running' THEN ? ELSE NULL END
                WHERE job_id=?""",
                (status, status, status, now + self.lease_seconds, job_id))
            self._audit(db, now, job["session_id"], "checkpoint",
                        {"job_id": job_id, "status": status, "final": final})
            return status

    def fail(self, job_id: str, worker_id: str, error: str, now: float,
             retry_delay: int = 30, max_attempts: int = 3):
        """Bounded retry with durable error record; exhausted work becomes failed."""
        with self._db() as db:
            job = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not job or job["status"] != "running" or job["lease_owner"] != worker_id:
                return "lease_lost"
            exhausted = job["attempts"] >= max_attempts
            status = "failed" if exhausted else "pending"
            db.execute("""UPDATE jobs SET status=?,available_at=?,last_error=?,
                lease_owner=NULL,lease_until=NULL WHERE job_id=?""",
                (status, now if exhausted else now + retry_delay, str(error)[:1000], job_id))
            self._audit(db, now, job["session_id"], "job_failed",
                        {"job_id": job_id, "status": status, "error": str(error)[:300]})
            return status

    def audit_log(self, session_id: str):
        with self._db() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM audit WHERE session_id=? ORDER BY id", (session_id,))]
