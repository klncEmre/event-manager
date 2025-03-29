from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from app import db
from app.models.user import User, UserRole
from email_validator import validate_email, EmailNotValidError
from app.utils.auth import custom_jwt_required
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Add a route to handle OPTIONS preflight requests for all auth endpoints
@auth_bp.route('/<path:path>', methods=['OPTIONS'])
@auth_bp.route('/', methods=['OPTIONS'])
def handle_options(path=None):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@auth_bp.route('/register', methods=['POST'])
@auth_bp.route('/register/', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate request data
    if not data or not all(key in data for key in ('username', 'email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    try:
        # Validate email
        valid = validate_email(data['email'])
        email = valid.email
    except EmailNotValidError as e:
        return jsonify({'message': str(e)}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # Create new user (default role is regular user)
    user = User(
        username=data['username'],
        email=email,
        password=data['password']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
@auth_bp.route('/login/', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate request data
    if not data or not all(key in data for key in ('email', 'password')):
        return jsonify({'message': 'Missing email or password'}), 400
    
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    
    # Check if user exists and password is correct
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    # Create access and refresh tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200

def custom_jwt_refresh_required():
    """
    Custom wrapper for jwt_required(refresh=True) that handles JWT validation errors
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # Check for Authorization header
                auth_header = request.headers.get('Authorization', '')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"message": "Missing or invalid refresh token", "error_type": "no_token"}), 401
                
                # Attempt to verify the JWT token with refresh=True
                verify_jwt_in_request(refresh=True)
                return fn(*args, **kwargs)
            except Exception as e:
                # Print detailed error for debugging
                import traceback
                print(f"Refresh Token Validation Error: {str(e)}")
                print(traceback.format_exc())
                
                # Return more specific error response
                if 'expired' in str(e).lower():
                    return jsonify({"message": "Refresh token has expired", "error_type": "token_expired"}), 401
                elif 'signature' in str(e).lower():
                    return jsonify({"message": "Invalid refresh token signature", "error_type": "invalid_signature"}), 401
                else:
                    return jsonify({"message": f"Refresh token validation failed: {str(e)}", "error_type": "auth_failed"}), 401
        return decorator
    return wrapper

@auth_bp.route('/refresh', methods=['POST'])
@auth_bp.route('/refresh/', methods=['POST'])
@custom_jwt_refresh_required()
def refresh():
    identity = get_jwt_identity()
    # Make sure identity is a string
    if not isinstance(identity, str):
        identity = str(identity)
    access_token = create_access_token(identity=identity)
    
    return jsonify({
        'access_token': access_token
    }), 200

@auth_bp.route('/me', methods=['GET'])
@auth_bp.route('/me/', methods=['GET'])
@custom_jwt_required()
def get_me():
    user_id = get_jwt_identity()
    
    # Convert string ID to integer if needed
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/validate-token', methods=['POST'])
@auth_bp.route('/validate-token/', methods=['POST'])
def validate_token():
    """Validate a token without requiring authentication"""
    try:
        data = request.get_json()
        
        if not data or 'token' not in data:
            return jsonify({'message': 'Token is required'}), 400
            
        # Extract the token
        token = data['token']
        
        # Manually decode and validate the token
        from flask_jwt_extended import decode_token
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
            user = User.query.filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'message': 'User not found for this token', 'valid': False}), 404
                
            return jsonify({
                'message': 'Token is valid',
                'valid': True, 
                'user': user.to_dict()
            }), 200
            
        except Exception as e:
            import traceback
            print(f"Token validation error: {str(e)}")
            print(traceback.format_exc())
            
            return jsonify({
                'message': f'Token validation failed: {str(e)}',
                'valid': False,
                'error': str(e)
            }), 401
            
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'valid': False}), 500 