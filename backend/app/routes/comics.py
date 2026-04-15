"""
Comic CRUD routes blueprint
🔒 Security: RBAC enforced for create/update/delete
"""
from flask import Blueprint, request, jsonify
from app.rbac import require_admin, require_super_admin
from app.db import (
    get_comics_page, count_comics, get_comic_by_id, create_comic, update_comic, delete_comic,
    get_user_id_by_uuid
)
from flask_jwt_extended import get_jwt_identity, jwt_required

comics_bp = Blueprint('comics', __name__, url_prefix='/api/comics')


@comics_bp.route('', methods=['GET'])
def list_comics():
    """
    Get paginated comics list (public)

    Query params:
        page: int (default 1)
        per_page: int (default 20, max 100)
    """
    page_param = request.args.get('page', '1')
    per_page_param = request.args.get('per_page', '20')

    try:
        page = int(page_param)
        per_page = int(per_page_param)
    except ValueError:
        return jsonify({'error': 'page and per_page must be integers'}), 400

    if page < 1 or per_page < 1:
        return jsonify({'error': 'page and per_page must be positive integers'}), 400

    if per_page > 100:
        return jsonify({'error': 'per_page cannot exceed 100'}), 400

    offset = (page - 1) * per_page
    total = count_comics()
    comics = get_comics_page(per_page, offset)
    has_more = (offset + len(comics)) < total

    return jsonify({
        'comics': [{
            'id': c.id,
            'serie': c.serie,
            'number': c.number,
            'title': c.title,
            'created_by': c.created_by,
            'created_at': c.created_at.isoformat() if c.created_at else None,
            'updated_at': c.updated_at.isoformat() if c.updated_at else None
        } for c in comics],
        'page': page,
        'per_page': per_page,
        'total': total,
        'has_more': has_more
    }), 200


@comics_bp.route('/<int:comic_id>', methods=['GET'])
def get_comic(comic_id):
    """
    Get individual comic (public - anyone can read)
    
    Response:
        200: Comic details
        404: Comic not found
    """
    comic = get_comic_by_id(comic_id)
    
    if not comic:
        return jsonify({'error': 'Comic not found'}), 404
    
    return jsonify({
        'id': comic.id,
        'serie': comic.serie,
        'number': comic.number,
        'title': comic.title,
        'created_by': comic.created_by,
        'created_at': comic.created_at.isoformat() if comic.created_at else None,
        'updated_at': comic.updated_at.isoformat() if comic.updated_at else None
    }), 200


@comics_bp.route('', methods=['POST'])
@require_admin  # Admin or super_admin only
def create_comic_endpoint():
    """
    Create new comic
    
    🔒 Security: Requires admin or super_admin role
    
    Request JSON:
        serie: str (required)
        number: int (required)
        title: str (required)
    
    Response:
        201: Comic created
        400: Validation error
        403: Insufficient role
        401: Not authenticated
    """
    from flask_jwt_extended import get_jwt_identity
    
    data = request.get_json()
    
    # Validation
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    serie = data.get('serie', '').strip()
    number = data.get('number')
    title = data.get('title', '').strip()
    
    if not serie:
        return jsonify({'error': 'serie is required'}), 400
    if number is None:
        return jsonify({'error': 'number is required'}), 400
    if not title:
        return jsonify({'error': 'title is required'}), 400
    
    if not isinstance(number, int) or number < 0:
        return jsonify({'error': 'number must be a positive integer'}), 400
    
    # Get creator ID from JWT
    user_uuid = get_jwt_identity()
    user_id = get_user_id_by_uuid(user_uuid)
    
    try:
        comic = create_comic(
            serie=serie,
            number=number,
            title=title,
            created_by=user_id
        )
        
        return jsonify({
            'id': comic.id,
            'serie': comic.serie,
            'number': comic.number,
            'title': comic.title,
            'created_by': comic.created_by,
            'created_at': comic.created_at.isoformat() if comic.created_at else None,
            'updated_at': comic.updated_at.isoformat() if comic.updated_at else None
        }), 201
    except Exception as e:
        return jsonify({'error': f'Failed to create comic: {str(e)}'}), 500


@comics_bp.route('/<int:comic_id>', methods=['PUT'])
@require_admin  # Admin or super_admin only
def update_comic_endpoint(comic_id):
    """
    Update comic
    
    🔒 Security: Requires admin or super_admin role
    
    Request JSON:
        serie: str (optional)
        number: int (optional)
        title: str (optional)
    
    Response:
        200: Comic updated
        400: Validation error
        403: Insufficient role
        404: Comic not found
        401: Not authenticated
    """
    comic = get_comic_by_id(comic_id)
    
    if not comic:
        return jsonify({'error': 'Comic not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    # Use existing values as defaults for fields not in request
    serie = comic.serie
    number = comic.number
    title = comic.title
    
    # Update fields if provided
    if 'serie' in data:
        serie_val = data['serie'].strip() if isinstance(data['serie'], str) else data['serie']
        if not serie_val:
            return jsonify({'error': 'serie cannot be empty'}), 400
        serie = serie_val
    
    if 'number' in data:
        if not isinstance(data['number'], int) or data['number'] < 0:
            return jsonify({'error': 'number must be a positive integer'}), 400
        number = data['number']
    
    if 'title' in data:
        title_val = data['title'].strip() if isinstance(data['title'], str) else data['title']
        if not title_val:
            return jsonify({'error': 'title cannot be empty'}), 400
        title = title_val
    
    try:
        updated_comic = update_comic(comic_id, serie=serie, number=number, title=title)
        
        return jsonify({
            'id': updated_comic.id,
            'serie': updated_comic.serie,
            'number': updated_comic.number,
            'title': updated_comic.title,
            'created_by': updated_comic.created_by,
            'created_at': updated_comic.created_at.isoformat() if updated_comic.created_at else None,
            'updated_at': updated_comic.updated_at.isoformat() if updated_comic.updated_at else None
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update comic: {str(e)}'}), 500


@comics_bp.route('/<int:comic_id>', methods=['DELETE'])
@require_admin  # Admin or super_admin only
def delete_comic_endpoint(comic_id):
    """
    Delete comic
    
    🔒 Security: Requires admin or super_admin role
    
    Response:
        204: Comic deleted
        403: Insufficient role
        404: Comic not found
        401: Not authenticated
    """
    comic = get_comic_by_id(comic_id)
    
    if not comic:
        return jsonify({'error': 'Comic not found'}), 404
    
    try:
        delete_comic(comic_id)
        return '', 204
    except Exception as e:
        return jsonify({'error': f'Failed to delete comic: {str(e)}'}), 500
