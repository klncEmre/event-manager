import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API from '../api/axios';

const EditEvent = () => {
  const { eventId } = useParams();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    start_time: '',
    end_time: '',
    capacity: '',
    is_published: false
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fetch event data on component mount
  useEffect(() => {
    const fetchEvent = async () => {
      try {
        const response = await API.get(`/events/${eventId}`);
        const event = response.data;
        
        // Format dates for datetime-local input
        const formatDate = (dateString) => {
          const date = new Date(dateString);
          return date.toISOString().slice(0, 16);
        };
        
        setFormData({
          title: event.title,
          description: event.description,
          location: event.location,
          start_time: formatDate(event.start_time),
          end_time: formatDate(event.end_time),
          capacity: event.capacity || '',
          is_published: event.is_published
        });
      } catch (err) {
        setError('Failed to load event data. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchEvent();
  }, [eventId]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    // Format payload
    const payload = {
      ...formData,
      capacity: formData.capacity ? parseInt(formData.capacity) : null
    };

    try {
      await API.put(`/events/${eventId}`, payload);
      navigate(`/events/${eventId}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update event. Please try again.');
      console.error(err);
      setSaving(false);
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

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <div className="card">
          <div className="card-body">
            <h2 className="card-title text-center mb-4">Edit Event</h2>

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
                    min={formData.start_time}
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
                <label className="form-check-label" htmlFor="is_published">Published</label>
              </div>

              <div className="d-grid">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditEvent; 