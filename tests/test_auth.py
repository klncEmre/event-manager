import json
import pytest
from app.models import User, UserRole

def test_register(client):
    """Test user registration."""
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User registered successfully'
    assert data['user']['username'] == 'testuser'
    assert data['user']['email'] == 'test@example.com'
    assert data['user']['role'] == UserRole.USER

def test_register_duplicate_username(client):
    """Test registration with duplicate username."""
    # First registration
    client.post('/api/auth/register', json={
        'username': 'duplicate',
        'email': 'first@example.com',
        'password': 'password123'
    })
    
    # Second registration with same username
    response = client.post('/api/auth/register', json={
        'username': 'duplicate',
        'email': 'second@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == 'Username already exists'

def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    # First registration
    client.post('/api/auth/register', json={
        'username': 'user1',
        'email': 'duplicate@example.com',
        'password': 'password123'
    })
    
    # Second registration with same email
    response = client.post('/api/auth/register', json={
        'username': 'user2',
        'email': 'duplicate@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == 'Email already exists'

def test_login(client):
    """Test user login."""
    # Register a user first
    client.post('/api/auth/register', json={
        'username': 'logintest',
        'email': 'login@example.com',
        'password': 'password123'
    })
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'login@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Login successful'
    assert data['user']['username'] == 'logintest'
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/api/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Invalid email or password'

def test_get_me(client, admin_token):
    """Test getting current user info."""
    response = client.get('/api/auth/me', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == 'admin_test'
    assert data['email'] == 'admin@test.com'
    assert data['role'] == UserRole.ADMIN

def test_refresh_token(client, user_token):
    """Test refreshing access token."""
    # First get a refresh token
    response = client.post('/api/auth/login', json={
        'email': 'user@test.com',
        'password': 'password'
    })
    refresh_token = json.loads(response.data)['refresh_token']
    
    # Use refresh token to get a new access token
    response = client.post('/api/auth/refresh', headers={
        'Authorization': f'Bearer {refresh_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data 