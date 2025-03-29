from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
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
    user_id = get_jwt_identity()
    return User.query.filter_by(id=user_id).first() 