from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.event import Event
from app.models.user import User
from app.utils.auth import publisher_required, get_current_user

events_bp = Blueprint('events', __name__)

@events_bp.route('/', methods=['GET'])
def get_events():
    """Get all published events"""
    events = Event.query.filter_by(is_published=True).all()
    return jsonify([event.to_dict() for event in events]), 200

@events_bp.route('/all', methods=['GET'])
@jwt_required()
@publisher_required()
def get_all_events():
    """Get all events (published and unpublished) - publishers only"""
    user = get_current_user()
    
    # Admins can see all events
    if user.is_admin():
        events = Event.query.all()
    else:
        # Publishers can only see their own events (published or not) and all published events
        events = Event.query.filter(
            (Event.publisher_id == user.id) | (Event.is_published == True)
        ).all()
    
    return jsonify([event.to_dict() for event in events]), 200

@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event"""
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    # Check if the event is published or the requester is the publisher/admin
    if not event.is_published:
        # Check if user is authenticated
        try:
            user = get_current_user()
            # Only publisher of this event or admin can see unpublished events
            if not user or (user.id != event.publisher_id and not user.is_admin()):
                return jsonify({'message': 'Event not found'}), 404
        except:
            return jsonify({'message': 'Event not found'}), 404
    
    return jsonify(event.to_dict()), 200

@events_bp.route('/', methods=['POST'])
@jwt_required()
@publisher_required()
def create_event():
    """Create a new event (publishers only)"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'description', 'location', 'start_time', 'end_time']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Parse datetime strings
    try:
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'message': 'Invalid datetime format'}), 400
    
    # Validate event time
    if start_time >= end_time:
        return jsonify({'message': 'End time must be after start time'}), 400
    
    # Get current user (publisher)
    user = get_current_user()
    
    # Create new event
    event = Event(
        title=data['title'],
        description=data['description'],
        location=data['location'],
        start_time=start_time,
        end_time=end_time,
        capacity=data.get('capacity'),
        is_published=data.get('is_published', False),
        publisher_id=user.id
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify({
        'message': 'Event created successfully',
        'event': event.to_dict()
    }), 201

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
@publisher_required()
def update_event(event_id):
    """Update an event (publisher of the event or admin only)"""
    data = request.get_json()
    user = get_current_user()
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    # Check if user is the publisher of this event or an admin
    if event.publisher_id != user.id and not user.is_admin():
        return jsonify({'message': 'Permission denied'}), 403
    
    # Update fields if provided
    if 'title' in data:
        event.title = data['title']
    
    if 'description' in data:
        event.description = data['description']
    
    if 'location' in data:
        event.location = data['location']
    
    if 'capacity' in data:
        event.capacity = data['capacity']
    
    if 'is_published' in data:
        event.is_published = data['is_published']
    
    if 'start_time' in data:
        try:
            event.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Invalid start time format'}), 400
    
    if 'end_time' in data:
        try:
            event.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Invalid end time format'}), 400
    
    # Validate event time
    if event.start_time >= event.end_time:
        return jsonify({'message': 'End time must be after start time'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': 'Event updated successfully',
        'event': event.to_dict()
    }), 200

@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
@publisher_required()
def delete_event(event_id):
    """Delete an event (publisher of the event or admin only)"""
    user = get_current_user()
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    # Check if user is the publisher of this event or an admin
    if event.publisher_id != user.id and not user.is_admin():
        return jsonify({'message': 'Permission denied'}), 403
    
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({
        'message': 'Event deleted successfully'
    }), 200

@events_bp.route('/<int:event_id>/register', methods=['POST'])
@jwt_required()
def register_for_event(event_id):
    """Register for an event (any authenticated user)"""
    user = get_current_user()
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    # Check if event is published
    if not event.is_published:
        return jsonify({'message': 'Event is not published'}), 400
    
    # Check if user is already registered
    if user in event.attendees:
        return jsonify({'message': 'Already registered for this event'}), 400
    
    # Check if event is full
    if event.capacity and len(event.attendees) >= event.capacity:
        return jsonify({'message': 'Event is at full capacity'}), 400
    
    # Register user for event
    event.attendees.append(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Successfully registered for event',
        'event': event.to_dict()
    }), 200

@events_bp.route('/<int:event_id>/unregister', methods=['DELETE'])
@jwt_required()
def unregister_from_event(event_id):
    """Unregister from an event (any authenticated user)"""
    user = get_current_user()
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    # Check if user is registered
    if user not in event.attendees:
        return jsonify({'message': 'Not registered for this event'}), 400
    
    # Unregister user from event
    event.attendees.remove(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Successfully unregistered from event',
        'event': event.to_dict()
    }), 200

@events_bp.route('/<int:event_id>/attendees', methods=['GET'])
@jwt_required()
def get_event_attendees(event_id):
    """Get attendees for a specific event (publisher of the event or admin only)"""
    user = get_current_user()
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    # Check if user is the publisher of this event or an admin
    if event.publisher_id != user.id and not user.is_admin():
        return jsonify({'message': 'Permission denied'}), 403
    
    attendees = [user.to_dict() for user in event.attendees]
    
    return jsonify({
        'event_id': event.id,
        'event_title': event.title,
        'attendee_count': len(attendees),
        'attendees': attendees
    }), 200

@events_bp.route('/my-events', methods=['GET'])
@jwt_required()
def get_my_events():
    """Get events created by the current user (publishers only)"""
    user = get_current_user()
    
    if not user.is_publisher():
        return jsonify({'message': 'Permission denied'}), 403
    
    events = Event.query.filter_by(publisher_id=user.id).all()
    
    return jsonify([event.to_dict() for event in events]), 200

@events_bp.route('/my-registrations', methods=['GET'])
@jwt_required()
def get_my_registrations():
    """Get events the current user is registered for"""
    user = get_current_user()
    
    # Get all events the user is attending
    events = user.events_attending
    
    return jsonify([event.to_dict() for event in events]), 200 