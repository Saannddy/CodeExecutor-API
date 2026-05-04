"""
Cheat mode utilities — in-memory state, security-hardened.

CHEAT_MODE is held purely in memory (module-level flag) and resets on every
server restart. This is intentional: cheat mode should not silently persist
across deployments or container restarts.

CHEAT_CODE env var holds a SHA-256 hex digest of the secret passphrase.
The raw secret is NEVER stored anywhere — only its hash is in .env.

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

# ---------------------------------------------------------------------------
# In-memory state — process-local, resets on restart
# ---------------------------------------------------------------------------

# Initialize from CHEAT_MODE env var so you can pre-enable it if needed,
# but this is purely optional. Default is always False (safe).
_cheat_mode: bool = os.getenv("CHEAT_MODE", "false").lower() == "true"
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Security helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_cheat_mode() -> bool:
    """Return current cheat mode state (thread-safe read)."""
    with _lock:
        return _cheat_mode


def toggle_cheat_mode(raw_cheat_code: str) -> dict:
    """
    Validate raw_cheat_code against the stored SHA-256 hash, then flip the
    in-memory cheat mode flag. No disk writes — fast and race-condition-safe.

    Returns: { success: bool, message: str, cheat_mode: bool | None }
    """
    global _cheat_mode

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

    with _lock:
        _cheat_mode = not _cheat_mode
        new_mode = _cheat_mode

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
