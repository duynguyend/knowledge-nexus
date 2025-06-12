import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header'; // Import the new Header component
import Home from './components/Home';
import ReviewDashboard from './components/ReviewDashboard';
import ResultsView from './components/ResultsView';
import CustomizeOutput from './components/CustomizeOutput';
import SynthesisView from './components/SynthesisView'; // Added import
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header /> {/* Add the Header component here */}
        <div className="main-content-area"> {/* Added a wrapper for content below header */}
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/review" element={<ReviewDashboard />} />
          <Route path="/results/:taskId" element={<ResultsView />} />
          <Route path="/customize/:taskId" element={<CustomizeOutput />} />
          <Route path="/synthesis" element={<SynthesisView />} />
          {/* Adding placeholder routes for new nav links if they don't exist */}
          <Route path="/explore" element={<div>Explore Page Placeholder</div>} />
          <Route path="/community" element={<div>Community Page Placeholder</div>} />
        </Routes>
      </div>
    </Router>
  );
}
export default App;
