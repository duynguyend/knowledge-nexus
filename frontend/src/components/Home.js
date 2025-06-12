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
      // If a predefined topic was used, update the main topic state as well
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


  // If a research task is active, show the ResearchProgress component
  if (researchStatus && researchStatus.task_id) {
    return <ResearchProgress taskId={researchStatus.task_id} />;
    // Note: The new header and footer from home.html are not rendered here.
    // If they should persist, ResearchProgress would need to be a sub-part of the layout.
    // For now, per instructions, it replaces the main search area.
    // To include header/footer, the structure would be:
    // <div className="kn-container"> <Header /> <ResearchProgress ... /> <Footer /> </div>
  }

  return (
    <div className="kn-body-bg"> {/* Corresponds to body class="bg-slate-50" */}
      <div className="kn-layout-container"> {/* Corresponds to layout-container */}
        <header className="kn-header">
          <div className="kn-header-logo-title">
            <svg className="kn-logo-svg" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
              <path clipRule="evenodd" d="M24 18.4228L42 11.475V34.3663C42 34.7796 41.7457 35.1504 41.3601 35.2992L24 42V18.4228Z" fill="currentColor" fillRule="evenodd"></path>
              <path clipRule="evenodd" d="M24 8.18819L33.4123 11.574L24 15.2071L14.5877 11.574L24 8.18819ZM9 15.8487L21 20.4805V37.6263L9 32.9945V15.8487ZM27 37.6263V20.4805L39 15.8487V32.9945L27 37.6263ZM25.354 2.29885C24.4788 1.98402 23.5212 1.98402 22.646 2.29885L4.98454 8.65208C3.7939 9.08038 3 10.2097 3 11.475V34.3663C3 36.0196 4.01719 37.5026 5.55962 38.098L22.9197 44.7987C23.6149 45.0671 24.3851 45.0671 25.0803 44.7987L42.4404 38.098C43.9828 37.5026 45 36.0196 45 34.3663V11.475C45 10.2097 44.2061 9.08038 43.0155 8.65208L25.354 2.29885Z" fill="currentColor" fillRule="evenodd"></path>
            </svg>
            <h2 className="kn-header-title-text">Knowledge Nexus</h2>
          </div>
          <div className="kn-header-nav-actions">
            <nav className="kn-nav">
              <a className="kn-nav-link" href="#">Home</a>
              <a className="kn-nav-link" href="#">My Library</a>
              <a className="kn-nav-link" href="#">Explore</a>
              <a className="kn-nav-link" href="#">Community</a>
            </nav>
            <button className="kn-icon-button">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <div className="kn-profile-pic" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuB-HVDEzkObyXib5cSjrUZf62SxPe626h4qDiipYrVw0zGdRcsunrav7VsuccMP4MEnA7KxcAe8zmoq3AGTJurMF71gdEnfufi5aqn70XJSg1bwuaeUOU0JxnSBYG1Qhf5NUI8yzArfai2hZq1TQFVf3XrQjH6tKXo5onq_r6tUbbVjRDqt_R8BYgAiiAdxZViHR2gAYiG5LwPCRya4it_cGQ_6hfuSOEPfk1M3snzKxXWaJUvwrPufeuBdJlvoQ3NDCTliMhM-X1w")' }}></div>
          </div>
        </header>

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
                <div className="kn-error-message"> {/* Basic error display */}
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

        <footer className="kn-footer">
          <p className="kn-footer-text">© 2024 Knowledge Nexus. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
}

export default Home;
