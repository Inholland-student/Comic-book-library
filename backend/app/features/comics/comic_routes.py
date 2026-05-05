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


def serialize_comic(comic):
    return {
        "id": comic.id,
        "serie": comic.serie,
        "number": comic.number,
        "title": comic.title,
        "created_by": comic.created_by,
        "created_at": comic.created_at.isoformat() if comic.created_at else None,
        "updated_at": comic.updated_at.isoformat() if comic.updated_at else None,
    }


@comics_bp.route("", methods=["GET"])
@require_any_user
def list_comics():
    """
    Get paginated comics list.

    Query params:
        page: int (default 1)
        per_page: int (default 20, max 100)
    """
    page_param = request.args.get("page", "1")
    per_page_param = request.args.get("per_page", "20")

    try:
        page = int(page_param)
        per_page = int(per_page_param)
    except ValueError:
        return jsonify({"error": "page and per_page must be integers"}), 400

    if page < 1 or per_page < 1:
        return jsonify({"error": "page and per_page must be positive integers"}), 400

    if per_page > 100:
        return jsonify({"error": "per_page cannot exceed 100"}), 400

    offset = (page - 1) * per_page
    total = count_comics()
    comics = get_comics_page(per_page, offset)
    has_more = (offset + len(comics)) < total

    return (
        jsonify(
            {
                "comics": [serialize_comic(c) for c in comics],
                "page": page,
                "per_page": per_page,
                "total": total,
                "has_more": has_more,
            }
        ),
        200,
    )


@comics_bp.route("/<int:comic_id>", methods=["GET"])
@require_any_user
def get_comic(comic_id):
    """
    Get one comic.
    Requires authenticated user.
    """
    comic = get_comic_by_id(comic_id)

    if not comic:
        return jsonify({"error": "Comic not found"}), 404

    return jsonify(serialize_comic(comic)), 200


@comics_bp.route("", methods=["POST"])
@require_admin
def create_comic_endpoint():
    """
    Create new comic.

    Requires admin or super_admin.

    Request JSON:
        serie: str
        number: str
        title: str
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    serie = str(data.get("serie", "")).strip()
    number = str(data.get("number", "")).strip()
    title = str(data.get("title", "")).strip()

    if not serie:
        return jsonify({"error": "serie is required"}), 400

    if not number:
        return jsonify({"error": "number is required"}), 400

    if not title:
        return jsonify({"error": "title is required"}), 400

    user_uuid = get_jwt_identity()
    user_id = get_user_id_by_uuid(user_uuid)

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

    except Exception as e:
        return jsonify({"error": f"Failed to create comic: {str(e)}"}), 500


@comics_bp.route("/<int:comic_id>", methods=["PUT"])
@require_admin
def update_comic_endpoint(comic_id):
    """
    Update comic.

    Requires admin or super_admin.

    Request JSON:
        serie: str optional
        number: str optional
        title: str optional
    """
    comic = get_comic_by_id(comic_id)

    if not comic:
        return jsonify({"error": "Comic not found"}), 404

    data = request.get_json()

    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    serie = comic.serie
    number = comic.number
    title = comic.title

    if "serie" in data:
        serie_val = str(data["serie"]).strip()

        if not serie_val:
            return jsonify({"error": "serie cannot be empty"}), 400

        serie = serie_val

    if "number" in data:
        number_val = str(data["number"]).strip()

        if not number_val:
            return jsonify({"error": "number cannot be empty"}), 400

        number = number_val

    if "title" in data:
        title_val = str(data["title"]).strip()

        if not title_val:
            return jsonify({"error": "title cannot be empty"}), 400

        title = title_val

    try:
        updated_comic = update_comic(
            comic_id,
            serie=serie,
            number=number,
            title=title,
        )

        return jsonify(serialize_comic(updated_comic)), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update comic: {str(e)}"}), 500


@comics_bp.route("/<int:comic_id>", methods=["DELETE"])
@require_admin
def delete_comic_endpoint(comic_id):
    """
    Delete comic.

    Requires admin or super_admin.
    """
    comic = get_comic_by_id(comic_id)

    if not comic:
        return jsonify({"error": "Comic not found"}), 404

    try:
        delete_comic(comic_id)
        return "", 204

    except Exception as e:
        return jsonify({"error": f"Failed to delete comic: {str(e)}"}), 500
