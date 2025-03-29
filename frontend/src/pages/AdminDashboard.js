import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import API from '../api/axios';
import { AuthContext } from '../context/AuthContext';

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('events');
  const { currentUser } = useContext(AuthContext);
  
  // New state for register form
  const [registerForm, setRegisterForm] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [registerSuccess, setRegisterSuccess] = useState(null);
  const [registerError, setRegisterError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all data in parallel
        const [eventsResponse, usersResponse] = await Promise.all([
          API.get('/events/all'),
          API.get('/users/'),
        ]);

        setEvents(eventsResponse.data);
        setUsers(usersResponse.data);
      } catch (err) {
        console.error('Error fetching admin data:', err);
        setError('Failed to load data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    // Only fetch if the user is an admin
    if (currentUser && currentUser.role === 'admin') {
      fetchData();
    }
  }, [currentUser]);

  // Handle register form input changes
  const handleRegisterInputChange = (e) => {
    const { name, value } = e.target;
    setRegisterForm({
      ...registerForm,
      [name]: value
    });
  };
  
  // Handle register form submission
  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setRegisterSuccess(null);
    setRegisterError(null);
    
    try {
      const response = await API.post('/users/register-publisher', registerForm);
      
      // Add the new user to the users list
      setUsers([...users, response.data.user]);
      
      // Reset form
      setRegisterForm({
        username: '',
        email: '',
        password: ''
      });
      
      // Show success message
      setRegisterSuccess('Event manager registered successfully!');
    } catch (err) {
      console.error('Error registering event manager:', err);
      setRegisterError(err.response?.data?.message || 'Failed to register event manager. Please try again.');
    }
  };

  // Format date and time for display
  const formatDateTime = (dateTimeStr) => {
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
  };

  if (!currentUser || currentUser.role !== 'admin') {
    return (
      <div className="alert alert-danger">
        You don't have permission to access this page.
      </div>
    );
  }

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
    <div className="container mt-4">
      <h1 className="mb-4">Admin Dashboard</h1>
      
      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'events' ? 'active' : ''}`}
            onClick={() => setActiveTab('events')}
          >
            All Events
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            All Users
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => setActiveTab('register')}
          >
            Register New Manager
          </button>
        </li>
      </ul>
      
      {/* All Events Section */}
      {activeTab === 'events' && (
        <div>
          <h2>All Events</h2>
          {events.length === 0 ? (
            <div className="alert alert-info">No events available.</div>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Publisher</th>
                    <th>Location</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Capacity</th>
                    <th>Attendees</th>
                    <th>Published</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {events.map(event => (
                    <tr key={event.id}>
                      <td>{event.id}</td>
                      <td>{event.title}</td>
                      <td>{event.publisher_id}</td>
                      <td>{event.location}</td>
                      <td>{formatDateTime(event.start_time)}</td>
                      <td>{formatDateTime(event.end_time)}</td>
                      <td>{event.capacity || 'Unlimited'}</td>
                      <td>{event.attendee_count}</td>
                      <td>{event.is_published ? 'Yes' : 'No'}</td>
                      <td>
                        <Link to={`/events/${event.id}`} className="btn btn-primary btn-sm me-2">View</Link>
                        <Link to={`/events/edit/${event.id}`} className="btn btn-warning btn-sm">Edit</Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      
      {/* All Users Section */}
      {activeTab === 'users' && (
        <div>
          <h2>All Users</h2>
          {users.length === 0 ? (
            <div className="alert alert-info">No users available.</div>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.username}</td>
                      <td>{user.email}</td>
                      <td>
                        <span className={`badge ${
                          user.role === 'admin' ? 'bg-danger' : 
                          user.role === 'publisher' ? 'bg-success' : 'bg-secondary'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td>{formatDateTime(user.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      
      {/* Register New Event Manager Section */}
      {activeTab === 'register' && (
        <div>
          <h2>Register New Event Manager</h2>
          <p>Create a new user account with event manager privileges. Event managers can create and manage events.</p>
          
          {registerSuccess && (
            <div className="alert alert-success" role="alert">
              {registerSuccess}
            </div>
          )}
          
          {registerError && (
            <div className="alert alert-danger" role="alert">
              {registerError}
            </div>
          )}
          
          <div className="card">
            <div className="card-body">
              <form onSubmit={handleRegisterSubmit}>
                <div className="mb-3">
                  <label htmlFor="username" className="form-label">Username</label>
                  <input
                    type="text"
                    className="form-control"
                    id="username"
                    name="username"
                    value={registerForm.username}
                    onChange={handleRegisterInputChange}
                    required
                  />
                </div>
                
                <div className="mb-3">
                  <label htmlFor="email" className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    id="email"
                    name="email"
                    value={registerForm.email}
                    onChange={handleRegisterInputChange}
                    required
                  />
                </div>
                
                <div className="mb-3">
                  <label htmlFor="password" className="form-label">Password</label>
                  <input
                    type="password"
                    className="form-control"
                    id="password"
                    name="password"
                    value={registerForm.password}
                    onChange={handleRegisterInputChange}
                    required
                  />
                  <div className="form-text">Password must be at least 6 characters long.</div>
                </div>
                
                <button type="submit" className="btn btn-primary">
                  Register Event Manager
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard; 