// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [joke, setJoke] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchJoke = async () => {
    setLoading(true);
    setError(null);
    try {
      // Ensure this URL matches your backend service URL
      const response = await fetch('http://localhost:4000/api/joke');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setJoke(data.joke);
    } catch (e) {
      setError('Failed to fetch joke. Please ensure the backend is running.');
      console.error("Error fetching joke:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJoke();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>DevOps Joke Dispenser</h1>
        {loading && <p>Loading joke...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {!loading && !error && <p>{joke}</p>}
        <button onClick={fetchJoke}>Get New Joke</button>
      </header>
    </div>
  );
}

export default App;