"""
Cheat mode utilities — database-backed persistence.

CHEAT_MODE is persisted in the database as a single `cheat_mode` row.
The raw secret passphrase is still protected by CHEAT_CODE in .env.

Setup:
    python3 -c "import hashlib; print(hashlib.sha256(b'YOUR_SECRET').hexdigest())"
    # Set CHEAT_CODE=<that hash> in .env

Toggling:
    POST /cheat-flip  { "cheat-code": "YOUR_SECRET" }
"""
import os
import hmac
import hashlib
import threading

from sqlmodel import select
from infrastructure import SessionLocal as SessionFactory
from models import CheatMode

_lock = threading.Lock()


def _get_cheat_row(session):
    statement = select(CheatMode).where(CheatMode.id == 1)
    cheat = session.exec(statement).first()
    if cheat is None:
        cheat = CheatMode(id=1, enabled=False)
        session.add(cheat)
        session.commit()
        session.refresh(cheat)
    return cheat


def _hash_secret(raw: str) -> str:
    """Return the SHA-256 hex digest of a raw passphrase."""
    return hashlib.sha256(raw.encode()).hexdigest()


def _constant_time_verify(raw_input: str, stored_hash: str) -> bool:
    """
    Timing-safe comparison: hash the input, then compare fixed-length digests.
    Prevents timing-based brute-force attacks.
    """
    input_hash = _hash_secret(raw_input)
    return hmac.compare_digest(input_hash, stored_hash)


def is_cheat_mode() -> bool:
    """Return current cheat mode state (thread-safe read)."""
    with _lock:
        if not SessionFactory:
            return False

        with SessionFactory() as session:
            return _get_cheat_row(session).enabled


def toggle_cheat_mode(raw_cheat_code: str) -> dict:
    """
    Validate raw_cheat_code against the stored SHA-256 hash, then flip the
    cheat mode state in the database.

    Returns: { success: bool, message: str, cheat_mode: bool | None }
    """
    stored_hash = os.getenv("CHEAT_CODE")
    if not stored_hash:
        return {
            "success": False,
            "message": "Cheat mode is not configured on this server.",
            "cheat_mode": None,
        }

    if not _constant_time_verify(raw_cheat_code, stored_hash):
        return {
            "success": False,
            "message": "Invalid cheat code.",
            "cheat_mode": None,
        }

    if not SessionFactory:
        return {
            "success": False,
            "message": "Database is not configured for cheat mode storage.",
            "cheat_mode": None,
        }

    with _lock:
        with SessionFactory() as session:
            cheat = _get_cheat_row(session)
            cheat.enabled = not cheat.enabled
            session.add(cheat)
            session.commit()
            session.refresh(cheat)
            new_mode = cheat.enabled

    return {
        "success": True,
        "message": f"Cheat mode {'enabled' if new_mode else 'disabled'}.",
        "cheat_mode": new_mode,
    }


def make_all_passed_result(tests: list) -> dict:
    """Build a fake 'all passed' execution result for the given test list."""
    results = [
        {
            "case": int(t.get("test_number", i + 1)),
            "status": "passed",
            "msg": "Test passed.",
            "stdout": t.get("expected_output", "").strip(),
            "stderr": "",
        }
        for i, t in enumerate(tests)
    ]
    return {"status": "correct", "msg": "All tests passed!", "tests": results}
