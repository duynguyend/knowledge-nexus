## Frontend Development Setup

This section outlines the steps to set up and run the frontend React application for Knowledge Nexus.

### Prerequisites

*   **Node.js:** The latest Long-Term Support (LTS) version of Node.js is recommended. You can download it from [nodejs.org](https://nodejs.org/).
*   **npm:** Node Package Manager, which is included with Node.js.

### Setup Steps

1.  **Navigate to the Frontend Directory:**
    Open your terminal and change to the frontend directory:
    ```bash
    cd frontend
    ```

2.  **Install Dependencies:**
    Install all required Node.js packages listed in `package.json`:
    ```bash
    npm install
    ```
    This command will download and install all the necessary libraries for the React application.

3.  **Start the Frontend Development Server:**
    Once the dependencies are installed, you can start the React development server:
    ```bash
    npm start
    ```
    This command will:
    *   Compile the React application.
    *   Start a development server (usually on `http://localhost:3000`).
    *   Open the application in your default web browser.
    *   Watch for file changes and automatically reload the application when you save edits.

    You should see output in your terminal indicating that the development server is running and the application is accessible at `http://localhost:3000`.

### Environment Variables (Frontend)

If the frontend application requires specific environment variables (e.g., API base URLs), these are typically managed using `.env` files in the `frontend/` directory, prefixed with `REACT_APP_`.

Example `frontend/.env` file:
```env
REACT_APP_API_BASE_URL=http://localhost:8000
```
Refer to the Create React App documentation for more details on managing environment variables. Remember to restart the development server after adding or modifying `.env` files.
