import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import API from '../api/axios';

const MyEvents = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMyEvents = async () => {
      try {
        const response = await API.get('/events/my-events');
        setEvents(response.data);
      } catch (err) {
        setError('Failed to load your events. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMyEvents();
  }, []);

  const formatDateTime = (dateTimeStr) => {
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
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

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>My Events</h1>
        <Link to="/events/create" className="btn btn-primary">
          Create New Event
        </Link>
      </div>
      
      {events.length === 0 ? (
        <div className="alert alert-info">
          You haven't created any events yet. Click the button above to create your first event!
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>Title</th>
                <th>Location</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Capacity</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {events.map(event => (
                <tr key={event.id}>
                  <td>
                    <Link to={`/events/${event.id}`}>{event.title}</Link>
                  </td>
                  <td>{event.location}</td>
                  <td>{formatDateTime(event.start_time)}</td>
                  <td>{formatDateTime(event.end_time)}</td>
                  <td>{event.capacity || 'Unlimited'}</td>
                  <td>
                    {event.is_published ? (
                      <span className="badge bg-success">Published</span>
                    ) : (
                      <span className="badge bg-warning text-dark">Draft</span>
                    )}
                  </td>
                  <td>
                    <div className="btn-group btn-group-sm">
                      <Link 
                        to={`/events/${event.id}`} 
                        className="btn btn-info"
                      >
                        View
                      </Link>
                      <Link 
                        to={`/events/edit/${event.id}`} 
                        className="btn btn-warning"
                      >
                        Edit
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default MyEvents; 