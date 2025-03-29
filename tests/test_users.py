import json
import pytest
from app.models import User, UserRole

def test_get_users_as_admin(client, admin_token):
    """Test getting all users as admin."""
    response = client.get('/api/users/', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 3  # At least the three users from the fixtures

def test_get_users_as_publisher(client, publisher_token):
    """Test getting all users as publisher (should be forbidden)."""
    response = client.get('/api/users/', headers={
        'Authorization': f'Bearer {publisher_token}'
    })
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['msg'] == 'Admin privileges required'

def test_get_specific_user_as_admin(client, admin_token):
    """Test getting a specific user as admin."""
    # Get all users first to find an ID
    response = client.get('/api/users/', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    users = json.loads(response.data)
    user_id = users[0]['id']
    
    # Get the specific user
    response = client.get(f'/api/users/{user_id}', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == user_id

def test_get_specific_user_as_same_user(client, user_token):
    """Test getting your own user details."""
    # Get current user details
    response = client.get('/api/auth/me', headers={
        'Authorization': f'Bearer {user_token}'
    })
    current_user = json.loads(response.data)
    user_id = current_user['id']
    
    # Get the specific user
    response = client.get(f'/api/users/{user_id}', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == user_id

def test_get_specific_user_as_different_user(client, user_token):
    """Test getting a different user's details as regular user (should be forbidden)."""
    # We know admin must have a different ID
    # Using a high number that shouldn't match our test user
    user_id = 999
    
    response = client.get(f'/api/users/{user_id}', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    # Should get either 403 (permission denied) or 404 (not found)
    assert response.status_code in (403, 404)

def test_get_publishers(client, user_token):
    """Test getting all publishers."""
    response = client.get('/api/users/publishers', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 2  # At least admin and publisher from fixtures
    
    # Verify all returned users are either publishers or admins
    for user in data:
        assert user['role'] in (UserRole.PUBLISHER, UserRole.ADMIN)

def test_make_publisher(client, admin_token):
    """Test making a user a publisher."""
    # First create a regular user
    client.post('/api/auth/register', json={
        'username': 'promoteme',
        'email': 'promoteme@example.com',
        'password': 'password123'
    })
    
    # Find the user's ID
    response = client.get('/api/users/', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    users = json.loads(response.data)
    user = next(u for u in users if u['username'] == 'promoteme')
    user_id = user['id']
    
    # Promote to publisher
    response = client.put(f'/api/users/make-publisher/{user_id}', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'User role updated to publisher successfully'
    assert data['user']['role'] == UserRole.PUBLISHER

def test_make_admin(client, admin_token):
    """Test making a user an admin."""
    # First create a regular user
    client.post('/api/auth/register', json={
        'username': 'makeadmin',
        'email': 'makeadmin@example.com',
        'password': 'password123'
    })
    
    # Find the user's ID
    response = client.get('/api/users/', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    users = json.loads(response.data)
    user = next(u for u in users if u['username'] == 'makeadmin')
    user_id = user['id']
    
    # Promote to admin
    response = client.put(f'/api/users/make-admin/{user_id}', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'User role updated to admin successfully'
    assert data['user']['role'] == UserRole.ADMIN

def test_revoke_privileges(client, admin_token):
    """Test revoking privileges from a publisher."""
    # First create a publisher
    client.post('/api/auth/register', json={
        'username': 'demote',
        'email': 'demote@example.com',
        'password': 'password123'
    })
    
    # Find the user's ID
    response = client.get('/api/users/', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    users = json.loads(response.data)
    user = next(u for u in users if u['username'] == 'demote')
    user_id = user['id']
    
    # Make them a publisher first
    client.put(f'/api/users/make-publisher/{user_id}', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    
    # Revoke privileges
    response = client.put(f'/api/users/revoke-privileges/{user_id}', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'User privileges revoked successfully'
    assert data['user']['role'] == UserRole.USER 