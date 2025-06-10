import React, { useState } from 'react';
import { startResearchTopic } from '../api';
import ResearchProgress from './ResearchProgress'; // Import ResearchProgress
import './Home.css';

function Home() {
  const [topic, setTopic] = useState('');
  const [researchStatus, setResearchStatus] = useState(null);
  const [error, setError] = useState(null);

  const handleTopicChange = (event) => {
    setTopic(event.target.value);
  };

  const handleStartResearch = async () => {
    if (!topic.trim()) {
      setError('Please enter a research topic.');
      return;
    }
    setError(null); // Clear previous errors
    setResearchStatus(null); // Clear previous status

    try {
      console.log(`Starting research for topic: "${topic}"`);
      const response = await startResearchTopic(topic);
      console.log("Research started successfully:", response);
      setResearchStatus(response); // Should be { task_id, status, message, ... }
    } catch (err) {
      console.error("Error starting research:", err);
      setError(err.message || 'Failed to start research. Please check console for details.');
      if (err.response && err.response.data && err.response.data.detail) {
        setError(`Failed to start research: ${err.response.data.detail}`);
      }
    }
  };

  return (
    <div className="home-container">
      <header className="home-header">
        <h1>Uncover the Truth with Multi-Agent AI</h1>
        <p className="home-subtitle">
          Enter a topic below and let our intelligent agents gather, verify, and synthesize information for you.
        </p>
      </header>

      <div className="research-input-section">
        <input
          type="text"
          value={topic}
          onChange={handleTopicChange}
          placeholder="E.g., The impact of AI on climate change"
          className="research-topic-input"
        />
        <button onClick={handleStartResearch} className="start-research-button">
          Start Researching
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
        </div>
      )}

      {researchStatus && researchStatus.task_id && (
        <ResearchProgress taskId={researchStatus.task_id} />
      )}
      {/*
        Alternative: If you want to show basic status from Home.js itself
        before ResearchProgress takes over or if ResearchProgress is a sub-component.
        For now, replacing it entirely when task_id is available.
      */}
      {/* {researchStatus && !researchStatus.task_id && ( // If status is there but no task_id (e.g. initial error from startResearchTopic)
        <div className="research-status-display">
          <p>Status: {researchStatus.status || 'N/A'}</p>
          {researchStatus.message && <p>Message: {researchStatus.message}</p>}
        </div>
      )} */}
    </div>
  );
}

export default Home;
