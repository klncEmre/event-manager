# Event Management System

A backend API for managing events with role-based access control.

## Features

- **Authentication System**: JWT-based authentication
- **Role-Based Access Control**: Three roles (admin, publisher, user)
- **Event Management**: Create, read, update, delete events
- **User Management**: Create users
- **Event Registration**: Users can register/unregister for events

## Technologies Used

- **Python Flask**: Web framework
- **SQLAlchemy**: ORM for database operations with many-to-many relationships
- **JWT**: Authentication and authorization
- **Flask-Migrate**: Database migrations

## Database Schema

### User Model
- Basic user information (username, email, password)
- Role-based permissions (admin, publisher, regular user)
- Relationships:
  - Published events (one-to-many)
  - Attending events (many-to-many)

### Event Model
- Event details (title, description, location, time)
- Publisher reference (foreign key to User)
- Attendees (many-to-many relationship with User)

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python run.py
```

## API Endpoints

### Authentication
- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Login and get tokens
- `POST /api/auth/refresh`: Refresh access token
- `GET /api/auth/me`: Get current user info

### Users
- `GET /api/users/`: Get all users (admin only)
- `GET /api/users/<user_id>`: Get specific user
- `GET /api/users/publishers`: Get all publishers
- `PUT /api/users/make-publisher/<user_id>`: Promote to publisher (admin only)
- `PUT /api/users/make-admin/<user_id>`: Promote to admin (admin only)
- `PUT /api/users/revoke-privileges/<user_id>`: Revoke privileges (admin only)

### Events
- `GET /api/events/`: Get all published events
- `GET /api/events/all`: Get all events (publishers only)
- `GET /api/events/<event_id>`: Get specific event
- `POST /api/events/`: Create new event (publishers only)
- `PUT /api/events/<event_id>`: Update event (owner or admin)
- `DELETE /api/events/<event_id>`: Delete event (owner or admin)
- `POST /api/events/<event_id>/register`: Register for event
- `DELETE /api/events/<event_id>/unregister`: Unregister from event
- `GET /api/events/<event_id>/attendees`: Get event attendees (owner or admin)
- `GET /api/events/my-events`: Get events created by current user
- `GET /api/events/my-registrations`: Get events user is registered for

## Default Admin User

The system automatically creates an admin user on first run:
- Username: `admin`
- Email: `admin@example.com`
- Password: `admin123`

Please change this password after first login for security purposes.

## SQLAlchemy Relationship Highlights

The system demonstrates SQLAlchemy's capabilities with:

1. **Many-to-Many Relationship**: Between User and Event models, allowing users to attend multiple events and events to have multiple attendees. This uses an association table `event_attendees`.

2. **One-to-Many Relationship**: Between User (as publisher) and Event models, where a publisher can create multiple events.

## Role-Based Access Control

- **Admin**: Can manage all users and events
- **Publisher**: Can create and manage events
- **Regular User**: Can register for events 