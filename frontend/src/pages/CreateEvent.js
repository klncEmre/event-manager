import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api/axios';

const CreateEvent = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    start_time: '',
    end_time: '',
    capacity: '',
    is_published: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Format payload
    const payload = {
      ...formData,
      capacity: formData.capacity ? parseInt(formData.capacity) : null
    };

    try {
      const response = await API.post('/events/', payload);
      navigate(`/events/${response.data.event.id}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create event. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Get current date and time in ISO format for the datetime-local input
  const getCurrentDateTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return now.toISOString().slice(0, 16);
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <div className="card">
          <div className="card-body">
            <h2 className="card-title text-center mb-4">Create New Event</h2>

            {error && (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="title" className="form-label">Title</label>
                <input
                  type="text"
                  className="form-control"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="mb-3">
                <label htmlFor="description" className="form-label">Description</label>
                <textarea
                  className="form-control"
                  id="description"
                  name="description"
                  rows="4"
                  value={formData.description}
                  onChange={handleChange}
                  required
                ></textarea>
              </div>

              <div className="mb-3">
                <label htmlFor="location" className="form-label">Location</label>
                <input
                  type="text"
                  className="form-control"
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="row">
                <div className="col-md-6 mb-3">
                  <label htmlFor="start_time" className="form-label">Start Time</label>
                  <input
                    type="datetime-local"
                    className="form-control"
                    id="start_time"
                    name="start_time"
                    value={formData.start_time}
                    onChange={handleChange}
                    min={getCurrentDateTime()}
                    required
                  />
                </div>

                <div className="col-md-6 mb-3">
                  <label htmlFor="end_time" className="form-label">End Time</label>
                  <input
                    type="datetime-local"
                    className="form-control"
                    id="end_time"
                    name="end_time"
                    value={formData.end_time}
                    onChange={handleChange}
                    min={formData.start_time || getCurrentDateTime()}
                    required
                  />
                </div>
              </div>

              <div className="mb-3">
                <label htmlFor="capacity" className="form-label">Capacity (Optional)</label>
                <input
                  type="number"
                  className="form-control"
                  id="capacity"
                  name="capacity"
                  value={formData.capacity}
                  onChange={handleChange}
                  min="1"
                />
                <small className="text-muted">Leave blank for unlimited capacity</small>
              </div>

              <div className="mb-3 form-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  id="is_published"
                  name="is_published"
                  checked={formData.is_published}
                  onChange={handleChange}
                />
                <label className="form-check-label" htmlFor="is_published">Publish immediately</label>
              </div>

              <div className="d-grid">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Creating...' : 'Create Event'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateEvent; 