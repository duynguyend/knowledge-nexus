import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
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
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/review" element={<ReviewDashboard />} />
          <Route path="/results/:taskId" element={<ResultsView />} />
          <Route path="/customize/:taskId" element={<CustomizeOutput />} />
          <Route path="/synthesis" element={<SynthesisView />} /> {/* Added route */}
        </Routes>
      </div>
    </Router>
  );
}
export default App;
