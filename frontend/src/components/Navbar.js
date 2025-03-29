import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { isAdmin, isPublisher, isRegularUser, getHomePageForUser, ROLES } from '../utils/roleUtils';

const Navbar = () => {
  const { currentUser, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Helper to render role-specific title/badge next to username
  const getRoleBadge = () => {
    if (isAdmin(currentUser)) return <span className="badge bg-danger ms-1">Admin</span>;
    if (isPublisher(currentUser)) return <span className="badge bg-success ms-1">Event Manager</span>;
    return null;
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
      <div className="container">
        <Link className="navbar-brand" to={getHomePageForUser(currentUser)}>EVENT PLATFORM</Link>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            {/* Admin Navigation */}
            {isAdmin(currentUser) && (
              <li className="nav-item">
                <Link className="nav-link active" to="/admin">Admin Dashboard</Link>
              </li>
            )}
            
            {/* Publisher/Event Manager Navigation */}
            {isPublisher(currentUser) && (
              <>
                <li className="nav-item">
                  <Link className="nav-link" to="/events">All Events</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/my-events">My Events</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/events/create">Create Event</Link>
                </li>
              </>
            )}
            
            {/* Regular User Navigation */}
            {isRegularUser(currentUser) && (
              <>
                <li className="nav-item">
                  <Link className="nav-link" to="/events">Events</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/my-registrations">My Registrations</Link>
                </li>
              </>
            )}
            
            {/* Not Logged In Navigation */}
            {!currentUser && (
              <li className="nav-item">
                <Link className="nav-link" to="/events">Events</Link>
              </li>
            )}
          </ul>
          <ul className="navbar-nav">
            {currentUser ? (
              <>
                <li className="nav-item">
                  <span className="nav-link text-white">
                    {isAdmin(currentUser) ? 'Admin: ' : 'Welcome, '}
                    {currentUser.username}
                    {getRoleBadge()}
                  </span>
                </li>
                <li className="nav-item">
                  <button className="btn btn-link nav-link" onClick={handleLogout}>Logout</button>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item">
                  <Link className="nav-link" to="/login">Login</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/register">Register</Link>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 