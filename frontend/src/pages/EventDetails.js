import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import API from '../api/axios';
import { AuthContext } from '../context/AuthContext';
import { isPublisher, isAdmin } from '../utils/roleUtils';

const EventDetails = () => {
  const { eventId } = useParams();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [registering, setRegistering] = useState(false);
  const [isRegistered, setIsRegistered] = useState(false);
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [registrationError, setRegistrationError] = useState(null);
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchEventDetails = async () => {
      try {
        // Check if there's a token in local storage
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        
        // Fetch the event details
        const response = await API.get(`/api/events/${eventId}`, { headers });
        setEvent(response.data);
        
        // If user is authenticated, check if they're registered for this event
        if (currentUser && !isPublisher(currentUser) && !isAdmin(currentUser)) {
          try {
            const registrationsResponse = await API.get('/api/events/my-registrations/', { headers });
            const userRegistrations = registrationsResponse.data;
            const isRegistered = userRegistrations.some(reg => reg.id === parseInt(eventId));
            setIsRegistered(isRegistered);
          } catch (err) {
            console.error("Failed to check registration status:", err);
          }
        }
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load event details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchEventDetails();
  }, [eventId, currentUser]);

  const handleRegistration = async () => {
    try {
      await API.post(`/api/events/${eventId}/register/`);
      setIsRegistered(true);
      setRegistrationSuccess(true);
      
      // Update attendee count
      setEvent({
        ...event,
        attendee_count: (event.attendee_count || 0) + 1
      });
    } catch (err) {
      setRegistrationError(err.response?.data?.message || 'Registration failed');
      console.error(err);
    }
  };

  const handleUnregister = async () => {
    setRegistering(true);
    try {
      await API.delete(`/api/events/${eventId}/unregister/`);
      // Update event data
      const response = await API.get(`/api/events/${eventId}`);
      setEvent(response.data);
      setIsRegistered(false);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to unregister from event');
      console.error(err);
    } finally {
      setRegistering(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
      try {
        await API.delete(`/api/events/${eventId}`);
        // Redirect admins to admin dashboard, others to events page
        if (isAdmin(currentUser)) {
          navigate('/admin');
        } else {
          navigate('/events');
        }
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to delete event');
        console.error(err);
      }
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center my-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
        {error === 'You need to be logged in to view this event.' && (
          <div className="mt-3">
            <Link to="/login" className="btn btn-primary">Login</Link>
          </div>
        )}
      </div>
    );
  }

  // Format date and time for display
  const formatDateTime = (dateTimeStr) => {
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
  };

  const isEventOwner = currentUser && currentUser.id === event.publisher_id;
  const isUserAdmin = isAdmin(currentUser);
  const canEdit = isEventOwner || isUserAdmin;
  const canRegister = currentUser && !isPublisher(currentUser) && !isAdmin(currentUser);
  
  const isEventFull = event.capacity && event.attendee_count >= event.capacity;
  const isPastEvent = new Date(event.end_time) < new Date();

  return (
    <div className="event-details">
      <div className="card">
        <div className="card-body">
          <h2 className="card-title">{event.title}</h2>
          
          {!event.is_published && (
            <div className="alert alert-warning mb-3">
              <strong>Draft Event:</strong> This event is not yet published and is only visible to you as the publisher.
            </div>
          )}
          
          {canEdit && (
            <div className="mb-3">
              <Link to={`/events/edit/${event.id}`} className="btn btn-warning me-2">
                Edit Event
              </Link>
              <button className="btn btn-danger" onClick={handleDelete}>
                Delete Event
              </button>
            </div>
          )}
          
          <div className="row mb-4">
            <div className="col-md-6">
              <h5>Details</h5>
              <div className="mb-2">
                <strong>Location:</strong> {event.location}
              </div>
              <div className="mb-2">
                <strong>Start:</strong> {formatDateTime(event.start_time)}
              </div>
              <div className="mb-2">
                <strong>End:</strong> {formatDateTime(event.end_time)}
              </div>
              {event.capacity && (
                <div className="mb-2">
                  <strong>Capacity:</strong> {event.attendee_count || 0}/{event.capacity}
                </div>
              )}
              <div className="mb-2">
                <strong>Published:</strong> {event.is_published ? 'Yes' : 'No'}
              </div>
            </div>
            
            <div className="col-md-6">
              <h5>Description</h5>
              <p>{event.description}</p>
            </div>
          </div>
          
          {/* Only show registration options for published events and regular users */}
          {event.is_published && canRegister && !isPastEvent && (
            <div className="text-center">
              {isRegistered ? (
                <button 
                  className="btn btn-danger btn-lg" 
                  onClick={handleUnregister}
                  disabled={registering}
                >
                  {registering ? 'Processing...' : 'Cancel Registration'}
                </button>
              ) : (
                <button 
                  className="btn btn-success btn-lg" 
                  onClick={handleRegistration}
                  disabled={registering || isEventFull}
                >
                  {registering ? 'Processing...' : (isEventFull ? 'Event Full' : 'Register for Event')}
                </button>
              )}
            </div>
          )}
          
          {isPastEvent && (
            <div className="alert alert-warning text-center">
              This event has already ended.
            </div>
          )}
          
          {!currentUser && !isPastEvent && event.is_published && (
            <div className="alert alert-info text-center">
              Please <Link to="/login">login</Link> to register for this event.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EventDetails; 