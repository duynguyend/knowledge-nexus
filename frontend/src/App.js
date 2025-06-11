import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import ResultsView from './components/ResultsView'; // Ensure this path is correct
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/results/:taskId" element={<ResultsView />} />
        </Routes>
      </div>
    </Router>
  );
}
export default App;
