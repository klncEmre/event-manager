import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import API from '../api/axios';

const MyRegistrations = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancelling, setCancelling] = useState(null);

  useEffect(() => {
    const fetchMyRegistrations = async () => {
      try {
        const response = await API.get('/api/events/my-registrations/');
        setEvents(response.data);
      } catch (err) {
        setError('Failed to load your registrations. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMyRegistrations();
  }, []);

  const handleCancelRegistration = async (eventId) => {
    setCancelling(eventId);
    try {
      await API.delete(`/api/events/${eventId}/unregister/`);
      // Remove the event from the list
      setEvents(events.filter(event => event.id !== eventId));
    } catch (err) {
      setError('Failed to cancel registration. Please try again.');
      console.error(err);
    } finally {
      setCancelling(null);
    }
  };

  const formatDateTime = (dateTimeStr) => {
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
  };

  // Check if an event is in the past
  const isPastEvent = (endTime) => {
    return new Date(endTime) < new Date();
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
      </div>
    );
  }

  // Separate upcoming and past events
  const upcomingEvents = events.filter(event => !isPastEvent(event.end_time));
  const pastEvents = events.filter(event => isPastEvent(event.end_time));

  return (
    <div>
      <h1 className="mb-4">My Registrations</h1>
      
      {events.length === 0 ? (
        <div className="alert alert-info">
          You haven't registered for any events yet. Browse available events to find some that interest you!
        </div>
      ) : (
        <>
          <h2 className="h4 mb-3">Upcoming Events</h2>
          {upcomingEvents.length === 0 ? (
            <div className="alert alert-info mb-4">
              You don't have any upcoming events.
            </div>
          ) : (
            <div className="table-responsive mb-4">
              <table className="table table-striped table-hover">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Location</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {upcomingEvents.map(event => (
                    <tr key={event.id}>
                      <td>
                        <Link to={`/events/${event.id}`}>{event.title}</Link>
                      </td>
                      <td>{event.location}</td>
                      <td>{formatDateTime(event.start_time)}</td>
                      <td>{formatDateTime(event.end_time)}</td>
                      <td>
                        <div className="btn-group btn-group-sm">
                          <Link 
                            to={`/events/${event.id}`} 
                            className="btn btn-info"
                          >
                            View
                          </Link>
                          <button 
                            className="btn btn-danger"
                            onClick={() => handleCancelRegistration(event.id)}
                            disabled={cancelling === event.id}
                          >
                            {cancelling === event.id ? 'Cancelling...' : 'Cancel'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {pastEvents.length > 0 && (
            <>
              <h2 className="h4 mb-3">Past Events</h2>
              <div className="table-responsive">
                <table className="table table-striped table-hover">
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Location</th>
                      <th>Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pastEvents.map(event => (
                      <tr key={event.id}>
                        <td>
                          <Link to={`/events/${event.id}`}>{event.title}</Link>
                        </td>
                        <td>{event.location}</td>
                        <td>{formatDateTime(event.start_time)}</td>
                        <td>
                          <Link 
                            to={`/events/${event.id}`} 
                            className="btn btn-sm btn-info"
                          >
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default MyRegistrations; 