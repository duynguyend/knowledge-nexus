import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getTaskResults } from '../api';
import './ResultsView.css';

const ResultsView = () => {
  const { taskId } = useParams();
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      if (!taskId) return;
      setIsLoading(true);
      setError(null);
      try {
        const data = await getTaskResults(taskId);
        setResults(data);
      } catch (err) {
        setError(err.message || 'Failed to fetch results');
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [taskId]);

  return (
    <div className="results-view-container">
      {isLoading && <p>Loading results for task {taskId}...</p>}
      {error && <p className="error-message">Error fetching results: {error}</p>}
      {results && (
        <>
          <h1>Research Results</h1>
          {/* Optional: Display topic if available */}
          {/* <p><strong>Topic:</strong> {results.topic || taskId}</p> */}
          <article className="results-content" dangerouslySetInnerHTML={{ __html: results.document_content }} />
        </>
      )}
    </div>
  );
};

export default ResultsView;
