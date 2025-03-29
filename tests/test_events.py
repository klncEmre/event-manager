import json
import pytest
from datetime import datetime, timedelta

def test_get_events(client):
    """Test getting all published events."""
    response = client.get('/api/events/')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1  # Only one published event in fixtures
    assert data[0]['title'] == 'Test Event 1'
    assert data[0]['is_published'] == True

def test_get_all_events_as_admin(client, admin_token):
    """Test getting all events (published and unpublished) as admin."""
    response = client.get('/api/events/all', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2  # Both events from fixtures
    
    # Make sure we have both published and unpublished events
    published = [e for e in data if e['is_published']]
    unpublished = [e for e in data if not e['is_published']]
    assert len(published) == 1
    assert len(unpublished) == 1

def test_get_all_events_as_publisher(client, publisher_token):
    """Test getting all events as publisher."""
    response = client.get('/api/events/all', headers={
        'Authorization': f'Bearer {publisher_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2  # Both events from fixtures (publisher owns them)

def test_get_all_events_as_user(client, user_token):
    """Test getting all events as regular user (should be forbidden)."""
    response = client.get('/api/events/all', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['msg'] == 'Publisher privileges required'

def test_get_event(client):
    """Test getting a specific published event."""
    # First get all events to find an ID
    response = client.get('/api/events/')
    events = json.loads(response.data)
    event_id = events[0]['id']
    
    # Get the specific event
    response = client.get(f'/api/events/{event_id}')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == event_id
    assert data['is_published'] == True

def test_get_unpublished_event_as_publisher(client, publisher_token):
    """Test getting a specific unpublished event as publisher."""
    # First get all events to find an unpublished event ID
    response = client.get('/api/events/all', headers={
        'Authorization': f'Bearer {publisher_token}'
    })
    events = json.loads(response.data)
    unpublished_event = next(e for e in events if not e['is_published'])
    event_id = unpublished_event['id']
    
    # Get the specific event
    response = client.get(f'/api/events/{event_id}', headers={
        'Authorization': f'Bearer {publisher_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == event_id
    assert data['is_published'] == False

def test_get_unpublished_event_as_user(client, user_token):
    """Test getting a specific unpublished event as regular user (should be forbidden)."""
    # First get all events as admin to find an unpublished event ID
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'password'
    })
    admin_token = json.loads(response.data)['access_token']
    
    response = client.get('/api/events/all', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    events = json.loads(response.data)
    unpublished_event = next(e for e in events if not e['is_published'])
    event_id = unpublished_event['id']
    
    # Try to get the unpublished event as regular user
    response = client.get(f'/api/events/{event_id}', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['message'] == 'Event not found'

def test_create_event(client, publisher_token):
    """Test creating a new event."""
    future_time = datetime.utcnow() + timedelta(days=30)
    start_time = future_time.isoformat()
    end_time = (future_time + timedelta(hours=3)).isoformat()
    
    response = client.post('/api/events/', headers={
        'Authorization': f'Bearer {publisher_token}'
    }, json={
        'title': 'New Test Event',
        'description': 'Description for new test event',
        'location': 'Test Location',
        'start_time': start_time,
        'end_time': end_time,
        'capacity': 200,
        'is_published': True
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Event created successfully'
    assert data['event']['title'] == 'New Test Event'
    assert data['event']['is_published'] == True

def test_create_event_as_user(client, user_token):
    """Test creating an event as regular user (should be forbidden)."""
    future_time = datetime.utcnow() + timedelta(days=30)
    start_time = future_time.isoformat()
    end_time = (future_time + timedelta(hours=3)).isoformat()
    
    response = client.post('/api/events/', headers={
        'Authorization': f'Bearer {user_token}'
    }, json={
        'title': 'New Test Event',
        'description': 'Description for new test event',
        'location': 'Test Location',
        'start_time': start_time,
        'end_time': end_time,
        'capacity': 200,
        'is_published': True
    })
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['msg'] == 'Publisher privileges required'

def test_update_event(client, publisher_token):
    """Test updating an event."""
    # First get all events to find an event to update
    response = client.get('/api/events/all', headers={
        'Authorization': f'Bearer {publisher_token}'
    })
    events = json.loads(response.data)
    event_id = events[0]['id']
    
    # Update the event
    response = client.put(f'/api/events/{event_id}', headers={
        'Authorization': f'Bearer {publisher_token}'
    }, json={
        'title': 'Updated Event Title',
        'description': 'Updated event description'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Event updated successfully'
    assert data['event']['title'] == 'Updated Event Title'
    assert data['event']['description'] == 'Updated event description'

def test_delete_event(client, publisher_token):
    """Test deleting an event."""
    # First create an event to delete
    future_time = datetime.utcnow() + timedelta(days=30)
    start_time = future_time.isoformat()
    end_time = (future_time + timedelta(hours=3)).isoformat()
    
    response = client.post('/api/events/', headers={
        'Authorization': f'Bearer {publisher_token}'
    }, json={
        'title': 'Event to Delete',
        'description': 'This event will be deleted',
        'location': 'Test Location',
        'start_time': start_time,
        'end_time': end_time
    })
    
    event_id = json.loads(response.data)['event']['id']
    
    # Delete the event
    response = client.delete(f'/api/events/{event_id}', headers={
        'Authorization': f'Bearer {publisher_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Event deleted successfully'
    
    # Verify it's deleted
    response = client.get(f'/api/events/{event_id}')
    assert response.status_code == 404

def test_register_for_event(client, user_token):
    """Test registering for an event."""
    # Get a published event ID
    response = client.get('/api/events/')
    events = json.loads(response.data)
    event_id = events[0]['id']
    
    # First unregister just to make sure (if this user is already registered)
    client.delete(f'/api/events/{event_id}/unregister', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    # Register for the event
    response = client.post(f'/api/events/{event_id}/register', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Successfully registered for event'

def test_unregister_from_event(client, user_token):
    """Test unregistering from an event."""
    # Get a published event ID
    response = client.get('/api/events/')
    events = json.loads(response.data)
    event_id = events[0]['id']
    
    # First make sure we're registered
    client.post(f'/api/events/{event_id}/register', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    # Unregister from the event
    response = client.delete(f'/api/events/{event_id}/unregister', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Successfully unregistered from event'

def test_get_event_attendees(client, publisher_token):
    """Test getting attendees for an event."""
    # Get an event ID
    response = client.get('/api/events/all', headers={
        'Authorization': f'Bearer {publisher_token}'
    })
    events = json.loads(response.data)
    event_id = events[0]['id']
    
    # Get attendees
    response = client.get(f'/api/events/{event_id}/attendees', headers={
        'Authorization': f'Bearer {publisher_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'attendees' in data
    assert 'attendee_count' in data
    assert 'event_id' in data
    assert data['event_id'] == event_id

def test_my_events(client, publisher_token):
    """Test getting events created by the current user."""
    response = client.get('/api/events/my-events', headers={
        'Authorization': f'Bearer {publisher_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2  # Both events from fixtures were created by this publisher

def test_my_registrations(client, user_token):
    """Test getting events the current user is registered for."""
    # First get a published event ID
    response = client.get('/api/events/')
    events = json.loads(response.data)
    event_id = events[0]['id']
    
    # Make sure we're registered
    client.post(f'/api/events/{event_id}/register', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    # Get registrations
    response = client.get('/api/events/my-registrations', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert any(e['id'] == event_id for e in data) 