from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from app import db

# User roles as enum-like constants
class UserRole:
    ADMIN = 'admin'
    PUBLISHER = 'publisher'
    USER = 'user'

# Association table for many-to-many relationship between users and events (attendees)
event_attendees = db.Table('event_attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
    db.Column('registered_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.USER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # Events created by this user (if they are a publisher)
    published_events = db.relationship('Event', backref='publisher', lazy=True)
    
    # Events this user is attending (many-to-many)
    events_attending = db.relationship('Event', 
                                     secondary=event_attendees,
                                     lazy='subquery',
                                     backref=db.backref('attendees', lazy=True))

    def __init__(self, username, email, password, role=UserRole.USER):
        self.username = username
        self.email = email
        self.password_hash = Bcrypt().generate_password_hash(password).decode('utf-8')
        self.role = role

    def check_password(self, password):
        return Bcrypt().check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_publisher(self):
        return self.role == UserRole.PUBLISHER or self.role == UserRole.ADMIN
    
    def can_publish_events(self):
        return self.is_publisher()
    
    def can_manage_publishers(self):
        return self.is_admin()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 