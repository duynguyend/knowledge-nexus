import React, { useState } from 'react';
import { startResearchTopic } from '../api';
import ResearchProgress from './ResearchProgress';
import './Home.css';

function Home() {
  const [topic, setTopic] = useState('');
  const [researchStatus, setResearchStatus] = useState(null);
  const [error, setError] = useState(null);

  const handleTopicChange = (event) => {
    setTopic(event.target.value);
  };

  const handleStartResearch = async (predefinedTopic = null) => {
    const currentTopic = predefinedTopic || topic;
    if (!currentTopic.trim()) {
      setError('Please enter a research topic.');
      return;
    }
    setError(null);
    setResearchStatus(null);

    try {
      console.log(`Starting research for topic: "${currentTopic}"`);
      if (predefinedTopic) {
        setTopic(predefinedTopic);
      }
      const response = await startResearchTopic(currentTopic);
      console.log("Research started successfully:", response);
      setResearchStatus(response);
    } catch (err) {
      console.error("Error starting research:", err);
      let errorMessage = err.message || 'Failed to start research. Please check console for details.';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMessage = `Failed to start research: ${err.response.data.detail}`;
      }
      setError(errorMessage);
    }
  };

  const popularTopics = [
    "The impact of social media on mental health",
    "The future of renewable energy",
    "The history of artificial intelligence",
    "The ethics of genetic engineering",
    "The science of climate change"
  ];

  if (researchStatus && researchStatus.task_id) {
    return <ResearchProgress taskId={researchStatus.task_id} />;
  }

  return (
    <div className="kn-home-container">
      <main className="kn-main-content">
        <div className="kn-main-content-container">
          <div className="kn-search-card">
            <div className="kn-search-card-header">
              <h1 className="kn-search-title">Uncover the Truth with Multi-Agent AI</h1>
              <p className="kn-search-subtitle">Enter your research topic or question to begin your journey of discovery.</p>
            </div>
            <div className="kn-search-input-wrapper">
              <div className="kn-search-icon-wrapper">
                <span className="material-symbols-outlined kn-search-icon">search</span>
              </div>
              <input
                className="kn-search-input"
                placeholder="E.g., The impact of AI on climate change"
                type="text"
                value={topic}
                onChange={handleTopicChange}
              />
            </div>

            {error && (
              <div className="kn-error-message">
                <p>{error}</p>
              </div>
            )}

            <div className="kn-popular-topics-section">
              <h2 className="kn-popular-topics-title">Or explore some popular topics:</h2>
              <div className="kn-popular-topics-buttons">
                {popularTopics.map((popTopic, index) => (
                  <button
                    key={index}
                    className="kn-popular-topic-button"
                    onClick={() => handleStartResearch(popTopic)}
                  >
                    <span>{popTopic}</span>
                  </button>
                ))}
              </div>
            </div>
            <button
              className="kn-start-research-button"
              onClick={() => handleStartResearch()}
            >
              <span className="material-symbols-outlined">auto_awesome</span>
              Start Researching
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Home;
