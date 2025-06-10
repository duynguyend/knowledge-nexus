import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './App.css';
import { checkBackendHealth } from './api';
import Home from './components/Home';
import ReviewDashboard from './components/ReviewDashboard';
import SynthesisView from './components/SynthesisView';
import ExportOptions from './components/ExportOptions';

function App() {
  const [backendStatus, setBackendStatus] = useState('Checking backend connection...');

  useEffect(() => {
    const fetchBackendStatus = async () => {
      try {
        const healthData = await checkBackendHealth();
        if (healthData && healthData.status === 'ok') {
          setBackendStatus('Backend Connection: OK');
        } else {
          setBackendStatus(`Backend Status: ${healthData ? JSON.stringify(healthData) : 'Unknown response'}`);
        }
      } catch (error) {
        setBackendStatus(`Backend Connection: Error - ${error.message}`);
      }
    };

    fetchBackendStatus();
  }, []); // Empty dependency array means this effect runs once on mount

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Knowledge Nexus</h1>
          <p>{backendStatus}</p>
          <nav className="App-nav">
            <ul>
              <li><Link to="/">Home</Link></li>
              <li><Link to="/review">Review Dashboard</Link></li>
              <li><Link to="/synthesis">Synthesis View</Link></li>
              {/* Example link to an export page for a specific task ID */}
              {/* In a real app, this might be generated dynamically or accessed from another part of the UI */}
              <li><Link to="/export/task123">Export Task (ID: task123)</Link></li>
            </ul>
          </nav>
        </header>
        <main className="App-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/review" element={<ReviewDashboard />} />
            <Route path="/synthesis" element={<SynthesisView />} />
            <Route path="/export/:taskId" element={<ExportOptions />} />
            {/* You might want a specific route for ResearchProgress if it's not always shown via Home */}
            {/* e.g. <Route path="/task/:taskId/progress" element={<ResearchProgress />} /> */}
          </Routes>
        </main>
        <footer className="App-footer">
          <p>&copy; {new Date().getFullYear()} Knowledge Nexus. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
