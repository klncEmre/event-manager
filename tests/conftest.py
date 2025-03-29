import pytest
from app import create_app, db
from app.models import User, Event, UserRole

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()
        
        # Create test users
        admin = User(username='admin_test', email='admin@test.com', password='password', role=UserRole.ADMIN)
        publisher = User(username='publisher_test', email='publisher@test.com', password='password', role=UserRole.PUBLISHER)
        user = User(username='user_test', email='user@test.com', password='password')
        
        db.session.add_all([admin, publisher, user])
        db.session.commit()

        # Create test events
        event1 = Event(
            title='Test Event 1',
            description='Description for test event 1',
            location='Test Location 1',
            start_time='2023-12-01T12:00:00',
            end_time='2023-12-01T15:00:00',
            capacity=100,
            is_published=True,
            publisher_id=publisher.id
        )
        
        event2 = Event(
            title='Test Event 2',
            description='Description for test event 2',
            location='Test Location 2',
            start_time='2023-12-15T12:00:00',
            end_time='2023-12-15T15:00:00',
            capacity=50,
            is_published=False,
            publisher_id=publisher.id
        )
        
        db.session.add_all([event1, event2])
        db.session.commit()
        
        # Register user for event1
        event1.attendees.append(user)
        db.session.commit()

    yield app
    
    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def admin_token(client):
    """Get admin JWT token."""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'password'
    })
    return response.json['access_token']

@pytest.fixture
def publisher_token(client):
    """Get publisher JWT token."""
    response = client.post('/api/auth/login', json={
        'email': 'publisher@test.com',
        'password': 'password'
    })
    return response.json['access_token']

@pytest.fixture
def user_token(client):
    """Get regular user JWT token."""
    response = client.post('/api/auth/login', json={
        'email': 'user@test.com',
        'password': 'password'
    })
    return response.json['access_token'] 