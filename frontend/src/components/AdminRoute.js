import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { isAdmin } from '../utils/roleUtils';

const AdminRoute = ({ children }) => {
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

  // If not logged in or not an admin, redirect to home
  if (!isAdmin(currentUser)) {
    return <Navigate to="/" />;
  }

  // Otherwise, render the protected admin component
  return children;
};

export default AdminRoute; 