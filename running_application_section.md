## Running the Application

To run the Knowledge Nexus application locally, both the backend and frontend development servers must be running simultaneously. They typically operate in separate terminal sessions.

1.  **Start the Backend Server:**
    *   Navigate to the `knowledge_nexus/backend` directory.
    *   Ensure your Python virtual environment is activated.
    *   Run the command:
        ```bash
        uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
        ```
    *   The backend API server will typically be available at `http://localhost:8000`.

2.  **Start the Frontend Development Server:**
    *   Navigate to the `knowledge_nexus/frontend` directory.
    *   Run the command:
        ```bash
        npm start
        ```
    *   The frontend React application will typically open automatically in your web browser at `http://localhost:3000`.

**Once both servers are running:**

*   You can access the Knowledge Nexus application by navigating to `http://localhost:3000` in your web browser.
*   The frontend application is configured to send API requests to the backend server (usually at `http://localhost:8000`).

Ensure that any necessary environment variables (e.g., API keys for backend services, API base URL for the frontend) are correctly configured in their respective `.env` files before starting the servers. Refer to the backend and frontend setup sections for details on environment variables.
