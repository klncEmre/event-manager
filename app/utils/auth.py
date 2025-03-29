from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required
from app.models.user import User

def admin_required():
    """
    Decorator to check if the current user is an admin
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Convert string ID to integer if needed
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
                
            user = User.query.filter_by(id=user_id).first()
            
            if not user:
                return jsonify({"msg": "User not found"}), 404
                
            if not user.is_admin():
                return jsonify({"msg": "Admin privileges required"}), 403
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def publisher_required():
    """
    Decorator to check if the current user is a publisher or admin
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Convert string ID to integer if needed
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
                
            user = User.query.filter_by(id=user_id).first()
            
            if not user:
                return jsonify({"msg": "User not found"}), 404
                
            if not user.is_publisher():
                return jsonify({"msg": "Publisher privileges required"}), 403
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def get_current_user():
    """
    Utility function to get the current user from JWT token
    """
    try:
        # First check if the request has a valid token
        verify_jwt_in_request()
        
        # Get user ID from token
        user_id = get_jwt_identity()
        if not user_id:
            print(f"JWT token exists but identity is None or empty")
            return None
        
        # Convert string ID to integer if needed
        if isinstance(user_id, str) and user_id.isdigit():
            user_id = int(user_id)
        
        # Get user from database
        user = User.query.filter_by(id=user_id).first()
        if not user:
            print(f"User with ID {user_id} not found in database")
        else:
            print(f"Successfully authenticated user: {user.username} (ID: {user.id}, Role: {user.role})")
        return user
    except Exception as e:
        import traceback
        print(f"Error in get_current_user: {str(e)}")
        traceback.print_exc()
        return None

def custom_jwt_required():
    """
    Custom wrapper for jwt_required that handles JWT validation errors
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # Check for Authorization header
                auth_header = request.headers.get('Authorization', '')
                if not auth_header or not auth_header.startswith('Bearer '):
                    print(f"Missing or invalid Authorization header: {auth_header}")
                    return jsonify({"message": "Missing or invalid Authorization header", "error_type": "no_token"}), 401
                
                # Extract the token manually
                token = auth_header.replace('Bearer ', '')
                print(f"Token extracted from header: {token[:10]}...")
                
                # Attempt to verify the JWT token
                verify_jwt_in_request()
                
                # If we get here, token is valid
                return fn(*args, **kwargs)
            except Exception as e:
                # Print detailed error for debugging
                import traceback
                print(f"JWT Validation Error: {str(e)}")
                print(traceback.format_exc())
                
                # Return more specific error response
                if 'expired' in str(e).lower():
                    return jsonify({"message": "Authentication token has expired", "error_type": "token_expired"}), 401
                elif 'signature' in str(e).lower():
                    return jsonify({"message": "Invalid token signature", "error_type": "invalid_signature"}), 401
                else:
                    return jsonify({"message": f"Authentication failed: {str(e)}", "error_type": "auth_failed"}), 401
        return decorator
    return wrapper 