import React, { useContext, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import { isAdmin, isPublisher, getHomePageForUser } from '../utils/roleUtils';

const Home = () => {
  const { currentUser, loading } = useContext(AuthContext);
  
  if (loading) {
    return (
      <div className="d-flex justify-content-center my-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  // Redirect based on user role
  if (currentUser) {
    return <Navigate to={getHomePageForUser(currentUser)} />;
  }

  // No user is logged in, redirect to events page
  return <Navigate to="/events" />;
};

export default Home; 