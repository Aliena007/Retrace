import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function Home() {
  const navigate = useNavigate();
  
  return (
    <div className="home-container">
      <div className="hero-section">
        <div className="logo-box">
          <div className="logo-icon">🔍</div>
          <h1 className="logo-text">Retrace</h1>
        </div>
        <p className="tagline">Campus Lost & Found Made Simple</p>
        <p className="description">AI-powered item tracking with automated matching and notifications</p>
        
        <div className="cta-buttons">
          <button className="btn btn-primary" onClick={() => navigate('/report-lost')} data-testid="report-lost-btn">
            Report Lost Item
          </button>
          <button className="btn btn-secondary" onClick={() => navigate('/report-found')} data-testid="report-found-btn">
            Report Found Item
          </button>
        </div>
        
        <div className="quick-links">
          <Link to="/browse" className="link" data-testid="browse-items-link">Browse All Items</Link>
        </div>
      </div>
    </div>
  );
}

function ReportLost() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    date_lost: new Date().toISOString().split('T')[0],
    location_lost: '',
    contact_info: '',
  });
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const formDataToSend = new FormData();
      Object.keys(formData).forEach(key => {
        formDataToSend.append(key, formData[key]);
      });
      if (image) {
        formDataToSend.append('image', image);
      }

      await axios.post(`${API_URL}/api/ai/lost/`, formDataToSend, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setMessage('Lost item reported successfully! We\'ll notify you if we find a match.');
      setTimeout(() => navigate('/browse'), 2000);
    } catch (error) {
      setMessage('Error reporting item: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <div className="form-card">
        <h2 data-testid="report-lost-title">Report Lost Item</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Item Name *</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              data-testid="lost-item-name"
            />
          </div>

          <div className="form-group">
            <label>Description *</label>
            <textarea
              required
              rows="3"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              data-testid="lost-item-description"
            />
          </div>

          <div className="form-group">
            <label>Date Lost</label>
            <input
              type="date"
              value={formData.date_lost}
              onChange={(e) => setFormData({...formData, date_lost: e.target.value})}
              data-testid="lost-date"
            />
          </div>

          <div className="form-group">
            <label>Location Lost *</label>
            <input
              type="text"
              required
              placeholder="e.g., Library, Cafeteria"
              value={formData.location_lost}
              onChange={(e) => setFormData({...formData, location_lost: e.target.value})}
              data-testid="lost-location"
            />
          </div>

          <div className="form-group">
            <label>Contact Info (Email/Phone) *</label>
            <input
              type="text"
              required
              placeholder="your.email@example.com"
              value={formData.contact_info}
              onChange={(e) => setFormData({...formData, contact_info: e.target.value})}
              data-testid="lost-contact"
            />
          </div>

          <div className="form-group">
            <label>Upload Image (Optional)</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setImage(e.target.files[0])}
              data-testid="lost-image-upload"
            />
          </div>

          {message && <div className={`message ${message.includes('Error') ? 'error' : 'success'}`} data-testid="message">{message}</div>}

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/')}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading} data-testid="submit-lost-btn">
              {loading ? 'Submitting...' : 'Report Lost Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ReportFound() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    date_found: new Date().toISOString().split('T')[0],
    location_found: '',
    contact_info: '',
  });
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const formDataToSend = new FormData();
      Object.keys(formData).forEach(key => {
        formDataToSend.append(key, formData[key]);
      });
      if (image) {
        formDataToSend.append('image', image);
      }

      await axios.post(`${API_URL}/api/ai/found/`, formDataToSend, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setMessage('Found item reported successfully! We\'ll match it with lost items.');
      setTimeout(() => navigate('/browse'), 2000);
    } catch (error) {
      setMessage('Error reporting item: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <div className="form-card">
        <h2 data-testid="report-found-title">Report Found Item</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Item Name *</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              data-testid="found-item-name"
            />
          </div>

          <div className="form-group">
            <label>Description *</label>
            <textarea
              required
              rows="3"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              data-testid="found-item-description"
            />
          </div>

          <div className="form-group">
            <label>Date Found</label>
            <input
              type="date"
              value={formData.date_found}
              onChange={(e) => setFormData({...formData, date_found: e.target.value})}
              data-testid="found-date"
            />
          </div>

          <div className="form-group">
            <label>Location Found *</label>
            <input
              type="text"
              required
              placeholder="e.g., Library, Cafeteria"
              value={formData.location_found}
              onChange={(e) => setFormData({...formData, location_found: e.target.value})}
              data-testid="found-location"
            />
          </div>

          <div className="form-group">
            <label>Contact Info (Email/Phone) *</label>
            <input
              type="text"
              required
              placeholder="your.email@example.com"
              value={formData.contact_info}
              onChange={(e) => setFormData({...formData, contact_info: e.target.value})}
              data-testid="found-contact"
            />
          </div>

          <div className="form-group">
            <label>Upload Image (Optional)</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setImage(e.target.files[0])}
              data-testid="found-image-upload"
            />
          </div>

          {message && <div className={`message ${message.includes('Error') ? 'error' : 'success'}`} data-testid="message">{message}</div>}

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/')}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading} data-testid="submit-found-btn">
              {loading ? 'Submitting...' : 'Report Found Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function BrowseItems() {
  const navigate = useNavigate();
  const [lostItems, setLostItems] = useState([]);
  const [foundItems, setFoundItems] = useState([]);
  const [activeTab, setActiveTab] = useState('lost');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const [lostRes, foundRes] = await Promise.all([
        axios.get(`${API_URL}/api/ai/lost/`),
        axios.get(`${API_URL}/api/ai/found/`)
      ]);
      setLostItems(lostRes.data);
      setFoundItems(foundRes.data);
    } catch (error) {
      console.error('Error fetching items:', error);
    } finally {
      setLoading(false);
    }
  };

  const items = activeTab === 'lost' ? lostItems : foundItems;

  return (
    <div className="browse-container">
      <div className="browse-header">
        <h2 data-testid="browse-title">Browse Items</h2>
        <button className="btn btn-primary" onClick={() => navigate('/')} data-testid="back-home-btn">Back to Home</button>
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'lost' ? 'active' : ''}`} 
          onClick={() => setActiveTab('lost')}
          data-testid="lost-tab"
        >
          Lost Items ({lostItems.length})
        </button>
        <button 
          className={`tab ${activeTab === 'found' ? 'active' : ''}`} 
          onClick={() => setActiveTab('found')}
          data-testid="found-tab"
        >
          Found Items ({foundItems.length})
        </button>
      </div>

      {loading ? (
        <div className="loading" data-testid="loading">Loading items...</div>
      ) : (
        <div className="items-grid" data-testid="items-grid">
          {items.length === 0 ? (
            <div className="no-items" data-testid="no-items">No {activeTab} items reported yet.</div>
          ) : (
            items.map((item) => (
              <div key={item.id} className="item-card" data-testid="item-card">
                {item.image && (
                  <div className="item-image">
                    <img src={`${API_URL}${item.image}`} alt={item.name} />
                  </div>
                )}
                <div className="item-content">
                  <h3 data-testid="item-name">{item.name}</h3>
                  <p className="item-description" data-testid="item-description">{item.description}</p>
                  <div className="item-meta">
                    <span data-testid="item-location">📍 {activeTab === 'lost' ? item.location_lost : item.location_found}</span>
                    <span data-testid="item-date">📅 {activeTab === 'lost' ? item.date_lost : item.date_found}</span>
                  </div>
                  <div className="item-contact" data-testid="item-contact">
                    Contact: {item.contact_info}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/report-lost" element={<ReportLost />} />
          <Route path="/report-found" element={<ReportFound />} />
          <Route path="/browse" element={<BrowseItems />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;