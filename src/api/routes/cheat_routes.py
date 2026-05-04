from flask import Blueprint, request, jsonify
from core.cheat import toggle_cheat_mode

cheat_bp = Blueprint("cheat", __name__)


@cheat_bp.post("/cheat-flip")
def cheat_flip():
    """
    Toggle cheat mode on/off.

    Body (JSON):
        { "cheat-code": "<raw secret passphrase>" }

    The server compares SHA-256(cheat-code) against the stored CHEAT_CODE hash
    using a constant-time comparison, so brute-forcing via timing is not possible.

    Returns 200 with current cheat_mode state on success.
    Returns 400 for malformed requests, 401 for wrong code, 500 if unconfigured.
    """
    if not request.is_json:
        return jsonify(status="error", message="Request body must be JSON"), 400

    data = request.get_json(silent=True) or {}
    cheat_code = data.get("cheat-code")

    if not cheat_code:
        return jsonify(status="error", message="Missing 'cheat-code' in request body"), 400

    result = toggle_cheat_mode(cheat_code)

    if not result["success"]:
        if result["cheat_mode"] is None:
            # Server-side misconfiguration
            return jsonify(status="error", message=result["message"]), 500
        # Wrong code — do NOT reveal whether mode is on or off
        return jsonify(status="error", message=result["message"]), 401

    return jsonify(
        status="success",
        message=result["message"],
        cheat_mode=result["cheat_mode"],
    ), 200
