from datetime import datetime
from app import db
from app.models.user import event_attendees

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to the publisher (user who created this event)
    publisher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # attendees relationship is defined in the User model through backref
    
    def can_register(self, user):
        """Check if a user can register for this event"""
        # Event must be published
        if not self.is_published:
            return False
            
        # Check if event is already full
        if self.capacity and len(self.attendees) >= self.capacity:
            return False
            
        # Check if user is already registered
        if user in self.attendees:
            return False
            
        return True
    
    def register_user(self, user):
        """Register a user for this event"""
        if self.can_register(user):
            self.attendees.append(user)
            return True
        return False
    
    def unregister_user(self, user):
        """Unregister a user from this event"""
        if user in self.attendees:
            self.attendees.remove(user)
            return True
        return False
    
    def get_attendee_count(self):
        """Get the number of attendees"""
        return len(self.attendees)
    
    def is_full(self):
        """Check if the event is at capacity"""
        if not self.capacity:
            return False
        return self.get_attendee_count() >= self.capacity
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'capacity': self.capacity,
            'is_published': self.is_published,
            'publisher_id': self.publisher_id,
            'attendee_count': self.get_attendee_count(),
            'is_full': self.is_full(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 