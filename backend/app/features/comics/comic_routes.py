"""
Comic CRUD routes blueprint
🔒 Security: RBAC enforced for create/update/delete
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.features.common.middleware.rbac import require_admin, require_any_user
from app.features.auth.user_db import get_user_id_by_uuid
from .comic_db import (
    get_comics_page,
    count_comics,
    get_comic_by_id,
    create_comic,
    update_comic,
    delete_comic,
)

comics_bp = Blueprint("comics", __name__, url_prefix="/api/comics")

# ── Field constraints ────────────────────────────────────────────────────────
_MAX_SERIE_LEN = 200   # slightly under the DB column (255) for headroom
_MAX_TITLE_LEN = 255   # matches db.String(255)
_MAX_NUMBER    = 9999  # reasonable upper bound for comic issue numbers


# ── Validation helpers ───────────────────────────────────────────────────────

def _parse_positive_int(value, field_name: str) -> int:
    """
    Parse *value* as a positive integer (1 – _MAX_NUMBER).

    Accepts an int or any string whose stripped form is a valid base-10
    integer. Raises ValueError with a user-visible message on any invalid
    input, including SQL fragments ("131 AND 1=1"), format-string payloads
    ("ZAP%n%s"), floats,
    empty strings, and out-of-range values.
    """
    try:
        n = int(str(value).strip())
    except (ValueError, TypeError):
        raise ValueError(f"Invalid {field_name}: must be a positive integer")
    if n < 1:
        raise ValueError(f"Invalid {field_name}: must be a positive integer")
    if n > _MAX_NUMBER:
        raise ValueError(f"Invalid {field_name}: must not exceed {_MAX_NUMBER}")
    return n


def _validate_text(value, field_name: str, max_len: int) -> str:
    """
    Validate a text field.

    Rules:
      - Must not be empty after stripping whitespace.
      - Must not exceed *max_len* characters.
      - Must not contain HTML angle brackets (< or >) — prevents
        storing raw HTML/script payloads (persistent XSS risk
        in consumers that do not escape output).

    Returns the stripped string on success.
    Raises ValueError with a user-visible message on failure.
    """
    s = str(value).strip()
    if not s:
        raise ValueError(f"{field_name} is required")
    if len(s) > max_len:
        raise ValueError(f"{field_name} cannot exceed {max_len} characters")
    if "<" in s or ">" in s:
        raise ValueError(f"{field_name} contains invalid characters")
    return s


# ── Serialiser ───────────────────────────────────────────────────────────────

def serialize_comic(comic):
    return {
        "id":         comic.id,
        "serie":      comic.serie,
        "number":     comic.number,
        "title":      comic.title,
        "created_by": comic.created_by,
        "created_at": comic.created_at.isoformat() if comic.created_at else None,
        "updated_at": comic.updated_at.isoformat() if comic.updated_at else None,
    }


# ── Routes ───────────────────────────────────────────────────────────────────

@comics_bp.route("", methods=["GET"])
@require_any_user
def list_comics():
    """
    Get paginated comics list.

    Query params:
        page:     int (default 1)
        per_page: int (default 20, max 100)

    Both parameters are validated as positive integers server-side;
    non-integer or out-of-range values return 400.
    """
    page_param     = request.args.get("page",     "1")
    per_page_param = request.args.get("per_page", "20")

    try:
        page     = int(page_param)
        per_page = int(per_page_param)
    except ValueError:
        return jsonify({"error": "page and per_page must be integers"}), 400

    if page < 1 or per_page < 1:
        return jsonify({"error": "page and per_page must be positive integers"}), 400

    if per_page > 100:
        return jsonify({"error": "per_page cannot exceed 100"}), 400

    offset   = (page - 1) * per_page
    total    = count_comics()
    comics   = get_comics_page(per_page, offset)
    has_more = (offset + len(comics)) < total

    return (
        jsonify(
            {
                "comics":   [serialize_comic(c) for c in comics],
                "page":     page,
                "per_page": per_page,
                "total":    total,
                "has_more": has_more,
            }
        ),
        200,
    )


@comics_bp.route("/<int:comic_id>", methods=["GET"])
@require_any_user
def get_comic(comic_id):
    """
    Get one comic by ID.

    Flask's <int:comic_id> converter rejects non-integer URL segments
    with a 404 before this function is called, so no further id
    validation is needed here.
    """
    comic = get_comic_by_id(comic_id)
    if not comic:
        return jsonify({"error": "Comic not found"}), 404
    return jsonify(serialize_comic(comic)), 200


@comics_bp.route("", methods=["POST"])
@require_admin
def create_comic_endpoint():
    """
    Create a new comic.
    Requires admin or super_admin role.

    Request JSON:
        serie:  str  — required, max 200 chars, no HTML angle brackets
        number: int  — required, positive integer 1–9999
        title:  str  — required, max 255 chars, no HTML angle brackets
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    try:
        serie  = _validate_text(data.get("serie",  ""), "serie",  _MAX_SERIE_LEN)
        number = str(_parse_positive_int(data.get("number"), "number"))
        title  = _validate_text(data.get("title",  ""), "title",  _MAX_TITLE_LEN)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    user_uuid = get_jwt_identity()
    user_id   = get_user_id_by_uuid(user_uuid)
    if not user_id:
        return jsonify({"error": "User not found"}), 404

    try:
        comic = create_comic(
            serie=serie,
            number=number,
            title=title,
            created_by=user_id,
        )
        return jsonify(serialize_comic(comic)), 201
    except Exception:
        # Do not expose internal exception details (may contain DB schema info).
        return jsonify({"error": "Failed to create comic"}), 500


@comics_bp.route("/<int:comic_id>", methods=["PUT"])
@require_admin
def update_comic_endpoint(comic_id):
    """
    Update an existing comic.
    Requires admin or super_admin role.

    Request JSON (all fields optional — only supplied fields are updated):
        serie:  str  — max 200 chars, no HTML angle brackets
        number: int  — positive integer 1–9999
        title:  str  — max 255 chars, no HTML angle brackets

    Flask's <int:comic_id> converter rejects non-integer URL segments with 404.
    """
    comic = get_comic_by_id(comic_id)
    if not comic:
        return jsonify({"error": "Comic not found"}), 404

    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Start from current stored values; only overwrite fields present in the request.
    serie  = comic.serie
    number = comic.number
    title  = comic.title

    try:
        if "serie" in data:
            serie = _validate_text(data["serie"], "serie", _MAX_SERIE_LEN)
        if "number" in data:
            number = str(_parse_positive_int(data["number"], "number"))
        if "title" in data:
            title = _validate_text(data["title"], "title", _MAX_TITLE_LEN)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        updated_comic = update_comic(
            comic_id,
            serie=serie,
            number=number,
            title=title,
        )
        return jsonify(serialize_comic(updated_comic)), 200
    except Exception:
        return jsonify({"error": "Failed to update comic"}), 500


@comics_bp.route("/<int:comic_id>", methods=["DELETE"])
@require_admin
def delete_comic_endpoint(comic_id):
    """
    Delete a comic.
    Requires admin or super_admin role.

    Flask's <int:comic_id> converter rejects non-integer URL segments with 404.
    """
    comic = get_comic_by_id(comic_id)
    if not comic:
        return jsonify({"error": "Comic not found"}), 404

    try:
        delete_comic(comic_id)
        return "", 204
    except Exception:
        return jsonify({"error": "Failed to delete comic"}), 500
