from flask import jsonify, Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Event Manager API is running",
        "api_endpoints": {
            "auth": "/api/auth",
            "users": "/api/users", 
            "events": "/api/events"
        }
    }) 