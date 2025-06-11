import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

/**
 * Checks the health of the backend API.
 * @returns {Promise<Object>} A promise that resolves to the health check response data.
 * @throws {Error} If the request fails or the backend is unhealthy.
 */
export const checkBackendHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    // You might want to check response.data for a specific status, e.g., response.data.status === 'ok'
    if (response.status === 200 && response.data) {
      console.log('Backend health check successful:', response.data);
      return response.data;
    } else {
      console.error('Backend health check failed with status or no data:', response);
      throw new Error(`Backend unhealthy or unexpected response: ${response.status}`);
    }
  } catch (error) {
    console.error('Error during backend health check:', error.message);
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Error request:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error message:', error.message);
    }
    throw error; // Re-throw the error so UI can catch it
  }
};

/**
 * Starts a new research task for the given topic.
 * @param {string} topic - The research topic.
 * @returns {Promise<Object>} A promise that resolves to the research status response data.
 * @throws {Error} If the request fails.
 */
export const startResearchTopic = async (topic) => {
  if (!topic || typeof topic !== 'string' || topic.trim() === '') {
    throw new Error('Research topic cannot be empty.');
  }
  try {
    const response = await axios.post(`${API_BASE_URL}/research`, { topic });
    console.log('API call /research successful, response data:', response.data);
    return response.data; // Should be ResearchStatus: { task_id, status, message, ... }
  } catch (error) {
    console.error('Error starting research topic:', error.message);
    if (error.response) {
      console.error('Error response data (startResearchTopic):', error.response.data);
      console.error('Error response status (startResearchTopic):', error.response.status);
      // Rethrow a more specific error or include details from backend
      throw new Error(error.response.data.detail || `Failed to start research (status ${error.response.status})`);
    } else if (error.request) {
      console.error('Error request (startResearchTopic): No response received', error.request);
      throw new Error('No response from server. Please check network connection.');
    } else {
      console.error('Error message (startResearchTopic):', error.message);
      throw new Error(`An unexpected error occurred: ${error.message}`);
    }
  }
};

/**
 * Fetches the results of a specific research task.
 * @param {string} taskId - The ID of the task.
 * @returns {Promise<Object>} A promise that resolves to the task results data.
 * @throws {Error} If the request fails.
 */
export const getTaskResults = async (taskId) => {
  if (!taskId) {
    throw new Error('Task ID cannot be empty for getTaskResults.');
  }
  try {
    const response = await axios.get(`${API_BASE_URL}/results/${taskId}`);
    console.log(`API call /results/${taskId} successful, response data:`, response.data);
    return response.data; // Expected: { document_content: "...", ... }
  } catch (error) {
    console.error(`Error fetching results for task ${taskId}:`, error.message);
    if (error.response) {
      console.error('Error response data (getTaskResults):', error.response.data);
      throw new Error(error.response.data.detail || `Failed to fetch results (status ${error.response.status})`);
    } else if (error.request) {
      throw new Error('No response from server while fetching task results.');
    } else {
      throw new Error(`An unexpected error occurred while fetching task results: ${error.message}`);
    }
  }
};

/**
 * (Placeholder) Initiates document generation for a task with specified options.
 * @param {string} taskId - The ID of the task.
 * @param {Object} exportOptions - Options for document generation.
 * @returns {Promise<Object>} A promise that resolves to the generation status.
 */
export const generateDocument = async (taskId, exportOptions) => {
  if (!taskId) {
    throw new Error('Task ID cannot be empty for document generation.');
  }
  console.log(`API Call (Mock): Generate document for task ${taskId} with options:`, exportOptions);
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Simulate a successful response
  return {
    message: `Document generation started for task ${taskId}.`,
    downloadUrl: `/mock-documents/report-${taskId}.pdf` // Example mock URL
  };
  // Simulate an error response (for testing)
  // throw new Error("Simulated document generation error.");
};

// You can add other API functions here as the application grows

/**
 * Fetches the status of a specific research task.
 * @param {string} taskId - The ID of the task.
 * @returns {Promise<Object>} A promise that resolves to the task status data.
 * @throws {Error} If the request fails.
 */
export const getTaskStatus = async (taskId) => {
  if (!taskId) {
    throw new Error('Task ID cannot be empty for getTaskStatus.');
  }
  try {
    const response = await axios.get(`${API_BASE_URL}/status/${taskId}`);
    console.log(`API call /status/${taskId} successful, response data:`, response.data);
    return response.data; // Expected: ResearchStatus model
  } catch (error) {
    console.error(`Error fetching status for task ${taskId}:`, error.message);
    if (error.response) {
      console.error('Error response data (getTaskStatus):', error.response.data);
      throw new Error(error.response.data.detail || `Failed to fetch status (status ${error.response.status})`);
    } else if (error.request) {
      throw new Error('No response from server while fetching task status.');
    } else {
      throw new Error(`An unexpected error occurred while fetching task status: ${error.message}`);
    }
  }
};

/**
 * Submits human verification data for a task.
 * @param {string} taskId - The ID of the task.
 * @param {Object} approvalData - The human approval data.
 * @param {boolean} approvalData.approved - Whether the data is approved.
 * @param {string} [approvalData.notes] - Optional notes.
 * @param {string} [approvalData.corrected_content] - Optional corrected content.
 * @returns {Promise<Object>} A promise that resolves to the submission response data.
 * @throws {Error} If the request fails.
 */
export const submitVerification = async (taskId, approvalData) => {
  if (!taskId) {
    throw new Error('Task ID cannot be empty for submitVerification.');
  }
  if (approvalData === null || typeof approvalData.approved !== 'boolean') {
    throw new Error('Approval data must include an "approved" boolean field.');
  }
  try {
    // The backend expects task_id and data_id in the HumanApproval model.
    // However, the HumanApproval model itself (from schemas.py) has task_id and data_id.
    // The endpoint /submit-verification/{task_id} already has task_id in the path.
    // The approvalData here should primarily contain { approved, notes, corrected_content }.
    // The backend's HumanApproval Pydantic model might need adjustment if it strictly expects task_id and data_id
    // in the body when they are already available via path or context.
    // For now, assuming approvalData sent is { approved, notes, corrected_content, task_id, data_id } as per HumanApproval model.
    // The component currently prepares a payload with task_id and data_id from verification_request.
    const response = await axios.post(`${API_BASE_URL}/submit-verification/${taskId}`, approvalData);
    console.log(`API call /submit-verification/${taskId} successful:`, response.data);
    return response.data; // Expected: { message: "..." }
  } catch (error) {
    console.error(`Error submitting verification for task ${taskId}:`, error.message);
    if (error.response) {
      console.error('Error response data (submitVerification):', error.response.data);
      throw new Error(error.response.data.detail || `Failed to submit verification (status ${error.response.status})`);
    } else if (error.request) {
      throw new Error('No response from server while submitting verification.');
    } else {
      throw new Error(`An unexpected error occurred while submitting verification: ${error.message}`);
    }
  }
};
