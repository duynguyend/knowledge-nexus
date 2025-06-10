import React, { useState, useEffect, useCallback } from 'react';
import { getTaskStatus, submitVerification } from '../api';
import './ResearchProgress.css';

const DEFAULT_POLL_INTERVAL = 5000; // 5 seconds

function ResearchProgress({ taskId }) {
  const [statusDetails, setStatusDetails] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false); // For individual actions like submitting verification
  const [isPollingLoading, setIsPollingLoading] = useState(false); // For background polling

  const [humanApproval, setHumanApproval] = useState({
    approved: true,
    notes: '',
    corrected_content: '',
  });

  const handleApprovalInputChange = (event) => {
    const { name, value, type } = event.target;
    // Special handling for radio button if its value is string "true" or "false"
    if (name === "approved") {
      setHumanApproval(prev => ({ ...prev, approved: value === 'true' }));
    } else {
      setHumanApproval(prev => ({ ...prev, [name]: value }));
    }
  };

  const fetchStatus = useCallback(async (isInitialFetch = false) => {
    if (!taskId) return false; // Stop polling if no taskId

    if (isInitialFetch) setIsLoading(true); // Show main loading for the very first fetch
    else setIsPollingLoading(true); // Show subtle loading for background polls

    // Don't clear general error on polling, only on initial load or manual action
    if (isInitialFetch) setError(null);

    try {
      const data = await getTaskStatus(taskId);
      setStatusDetails(data);
      setError(null); // Clear previous errors on successful fetch

      if (data.status === 'completed' || data.status === 'failed') {
        return false; // Stop polling
      }
    } catch (err) {
      console.error(`Error fetching status for task ${taskId}:`, err);
      // Only set general error if it's not a background poll or if statusDetails are missing
      if (!statusDetails || isInitialFetch) {
        setError(err.message || 'Failed to fetch task status.');
      } else {
        // For polling errors, maybe a more subtle notification or just log
        console.warn("Polling error, keeping existing data:", err.message);
      }
      return false; // Stop polling on error for safety, can be made more resilient
    } finally {
      if (isInitialFetch) setIsLoading(false);
      setIsPollingLoading(false);
    }
    return true; // Continue polling
  }, [taskId, statusDetails]); // Added statusDetails to dependencies of fetchStatus

  useEffect(() => {
    if (!taskId) {
      setStatusDetails(null);
      setError(null);
      return;
    }

    fetchStatus(true); // Initial fetch with main loading indicator

    const intervalId = setInterval(async () => {
      if (document.hidden) return; // Don't poll if tab is not visible

      // Check if polling should continue based on current statusDetails
      if (statusDetails && (statusDetails.status === 'completed' || statusDetails.status === 'failed')) {
        clearInterval(intervalId);
        return;
      }

      const shouldContinue = await fetchStatus(false); // Subsequent fetches are background polls
      if (!shouldContinue) {
        clearInterval(intervalId);
      }
    }, DEFAULT_POLL_INTERVAL);

    return () => clearInterval(intervalId);
  }, [taskId, fetchStatus, statusDetails]); // Added statusDetails to useEffect dependencies

  const handleSubmitVerification = async (event) => {
    event.preventDefault();
    if (!taskId || !statusDetails || statusDetails.status !== 'awaiting_human_verification' || !statusDetails.verification_request) {
      setError("Not in a state to submit verification, or verification data is missing.");
      return;
    }
    setIsLoading(true); // Use main loading for this action
    setError(null);
    try {
      const approvalPayload = {
        task_id: taskId,
        data_id: statusDetails.verification_request.data_id,
        approved: humanApproval.approved, // This should be a boolean
        notes: humanApproval.notes,
        corrected_content: humanApproval.corrected_content,
      };
      const response = await submitVerification(taskId, approvalPayload);
      console.log("Verification submitted:", response);
      setHumanApproval({ approved: true, notes: '', corrected_content: '' }); // Reset form
      await fetchStatus(true); // Force a refresh of status with loading indicator
    } catch (err) {
      console.error(`Error submitting verification for task ${taskId}:`, err);
      setError(err.message || 'Failed to submit verification.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!taskId) {
    return <div className="research-progress-container"><p>No research task specified.</p></div>;
  }

  if (isLoading && !statusDetails) {
    return <div className="research-progress-container"><p>Loading task details for {taskId}...</p></div>;
  }

  // If there's an error and no status details at all (initial load failed)
  if (error && !statusDetails) {
    return <div className="research-progress-container error-message"><p>Error loading task {taskId}: {error}</p></div>;
  }

  // If statusDetails are not yet loaded (e.g. taskId just changed but first fetchStatus hasn't completed)
  if (!statusDetails) {
    return <div className="research-progress-container"><p>Initializing details for task {taskId}...</p></div>;
  }

  const {
    status,
    message,
    progress,
    verification_request
  } = statusDetails;

  return (
    <div className="research-progress-container">
      <h2>Research Progress</h2>
      <p><strong>Task ID:</strong> {statusDetails.task_id}</p>
      <p><strong>Status:</strong> <span className={`status-${status}`}>{status || 'N/A'}</span> {isPollingLoading && status !== 'completed' && status !== 'failed' ? "(Updating...)" : ""}</p>
      {message && <p><strong>Message:</strong> {message}</p>}
      {typeof progress === 'number' && (
        <div className="progress-bar-container">
          <div className_name="progress-bar" style={{ width: `${Math.max(0, Math.min(progress,1)) * 100}%` }}>
            {(Math.max(0, Math.min(progress,1)) * 100).toFixed(0)}%
          </div>
        </div>
      )}
      {/* Display general error if it occurred during an action or if initial load failed but we have some old data */}
      {error && <div className="error-message general-error-display"><p>Notice: {error}</p></div>}


      {status === 'awaiting_human_verification' && verification_request && (
        <div className="human-verification-section">
          <h3>Human Verification Needed</h3>
          <div className="verification-item card">
            <h4>Item to Verify (ID: {verification_request.data_id})</h4>
            <p><strong>Content Preview:</strong> {verification_request.data_to_verify.content_preview}</p>
            {verification_request.data_to_verify.url && (
              <p><strong>URL:</strong> <a href={verification_request.data_to_verify.url} target="_blank" rel="noopener noreferrer">{verification_request.data_to_verify.url}</a></p>
            )}
          </div>

          {verification_request.conflicting_sources && verification_request.conflicting_sources.length > 0 && (
            <div className="conflicting-sources card">
              <h4>Conflicting Sources:</h4>
              <ul>
                {verification_request.conflicting_sources.map(source => (
                  <li key={source.id}>
                    <p><strong>ID:</strong> {source.id}</p>
                    <p><strong>Preview:</strong> {source.content_preview}</p>
                    {source.url && <p><strong>URL:</strong> <a href={source.url} target="_blank" rel="noopener noreferrer">{source.url}</a></p>}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <form onSubmit={handleSubmitVerification} className="verification-form card">
            <h4>Submit Your Feedback</h4>
            <div className="form-group approval-radios">
              <label className="radio-label">
                <input
                  type="radio"
                  name="approved"
                  value="true" // String value for radio
                  checked={humanApproval.approved === true}
                  onChange={handleApprovalInputChange}
                /> Approve
              </label>
              <label className="radio-label">
                <input
                  type="radio"
                  name="approved"
                  value="false" // String value for radio
                  checked={humanApproval.approved === false}
                  onChange={handleApprovalInputChange}
                /> Reject
              </label>
            </div>
            <div className="form-group">
              <label htmlFor="notes">Notes:</label>
              <textarea
                id="notes"
                name="notes"
                value={humanApproval.notes}
                onChange={handleApprovalInputChange}
                rows="3"
              />
            </div>
            <div className="form-group">
              <label htmlFor="corrected_content">Corrected Content (Optional):</label>
              <textarea
                id="corrected_content"
                name="corrected_content"
                value={humanApproval.corrected_content}
                onChange={handleApprovalInputChange}
                rows="5"
                placeholder="If rejecting or needs modification, provide corrected content here..."
              />
            </div>
            <button type="submit" disabled={isLoading} className="submit-verification-button">
              {isLoading ? 'Submitting...' : 'Submit Verification'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default ResearchProgress;
