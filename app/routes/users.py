from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserRole
from app.utils.auth import admin_required, get_current_user

users_bp = Blueprint('users', __name__)

# Add a route to handle OPTIONS preflight requests for all users endpoints
@users_bp.route('/<path:path>', methods=['OPTIONS'])
@users_bp.route('/', methods=['OPTIONS'])
def handle_options(path=None):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@users_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required()
def get_users():
    """Get all users (admin only)"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user"""
    current_user = get_current_user()
    
    # Regular users can only view their own profile
    if not current_user.is_admin() and current_user.id != user_id:
        return jsonify({'message': 'Permission denied'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    return jsonify(user.to_dict()), 200

@users_bp.route('/publishers', methods=['GET'])
@jwt_required()
def get_publishers():
    """Get all publishers"""
    publishers = User.query.filter(User.role.in_([UserRole.PUBLISHER, UserRole.ADMIN])).all()
    return jsonify([user.to_dict() for user in publishers]), 200

@users_bp.route('/make-publisher/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def make_publisher(user_id):
    """Make a user a publisher (admin only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Skip if already a publisher
    if user.role == UserRole.PUBLISHER:
        return jsonify({'message': 'User is already a publisher'}), 400
    
    # Skip if admin (admins already have publisher privileges)
    if user.role == UserRole.ADMIN:
        return jsonify({'message': 'Admin users already have publisher privileges'}), 400
    
    user.role = UserRole.PUBLISHER
    db.session.commit()
    
    return jsonify({
        'message': 'User role updated to publisher successfully',
        'user': user.to_dict()
    }), 200

@users_bp.route('/make-admin/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def make_admin(user_id):
    """Make a user an admin (admin only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Skip if already an admin
    if user.role == UserRole.ADMIN:
        return jsonify({'message': 'User is already an admin'}), 400
    
    user.role = UserRole.ADMIN
    db.session.commit()
    
    return jsonify({
        'message': 'User role updated to admin successfully',
        'user': user.to_dict()
    }), 200

@users_bp.route('/revoke-privileges/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def revoke_privileges(user_id):
    """Revoke publisher/admin privileges (admin only)"""
    current_user = get_current_user()
    
    # Admin cannot revoke their own privileges
    if current_user.id == user_id:
        return jsonify({'message': 'Cannot revoke your own admin privileges'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Skip if already a regular user
    if user.role == UserRole.USER:
        return jsonify({'message': 'User already has regular privileges'}), 400
    
    user.role = UserRole.USER
    db.session.commit()
    
    return jsonify({
        'message': 'User privileges revoked successfully',
        'user': user.to_dict()
    }), 200

@users_bp.route('/register-publisher', methods=['POST'])
@jwt_required()
@admin_required()
def register_publisher():
    """Register a new user as publisher (admin only)"""
    data = request.get_json()
    
    # Validate request data
    if not data or not all(key in data for key in ('username', 'email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    try:
        # Validate email
        from email_validator import validate_email, EmailNotValidError
        valid = validate_email(data['email'])
        email = valid.email
    except EmailNotValidError as e:
        return jsonify({'message': str(e)}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # Create new user with publisher role
    user = User(
        username=data['username'],
        email=email,
        password=data['password'],
        role=UserRole.PUBLISHER
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Event manager registered successfully',
        'user': user.to_dict()
    }), 201 