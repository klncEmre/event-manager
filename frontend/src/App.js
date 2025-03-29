import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

// Components
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import EventDetails from './pages/EventDetails';
import CreateEvent from './pages/CreateEvent';
import EditEvent from './pages/EditEvent';
import MyEvents from './pages/MyEvents';
import MyRegistrations from './pages/MyRegistrations';
import AdminDashboard from './pages/AdminDashboard';
import EventsPage from './pages/EventsPage';
import { AuthProvider, AuthContext } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import PublisherRoute from './components/PublisherRoute';
import AdminRoute from './components/AdminRoute';

// Custom redirect component that checks if user is admin
const AdminAwareRedirect = () => {
  const { currentUser } = useContext(AuthContext);
  return currentUser && currentUser.role === 'admin' 
    ? <Navigate to="/admin" /> 
    : <Navigate to="/" />;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/events" element={<EventsPage />} />
      <Route path="/events/:eventId" element={<EventDetails />} />
      
      {/* Protected routes */}
      <Route 
        path="/events/create" 
        element={
          <PublisherRoute>
            <CreateEvent />
          </PublisherRoute>
        } 
      />
      <Route 
        path="/events/edit/:eventId" 
        element={
          <PublisherRoute>
            <EditEvent />
          </PublisherRoute>
        } 
      />
      <Route 
        path="/my-events" 
        element={
          <PublisherRoute>
            <MyEvents />
          </PublisherRoute>
        } 
      />
      <Route 
        path="/my-registrations" 
        element={
          <PrivateRoute>
            <MyRegistrations />
          </PrivateRoute>
        } 
      />
      
      {/* Admin routes */}
      <Route 
        path="/admin" 
        element={
          <AdminRoute>
            <AdminDashboard />
          </AdminRoute>
        } 
      />
      
      {/* Fallback route - redirects to appropriate dashboard based on role */}
      <Route path="*" element={<AdminAwareRedirect />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <div className="container mt-4">
            <AppRoutes />
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App; 