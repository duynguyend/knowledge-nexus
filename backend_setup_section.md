## Backend Development Setup

This section outlines the steps to set up and run the backend server for Knowledge Nexus.

### Prerequisites

*   **Python:** Python 3.9 or newer is recommended.
*   **Pip:** Python's package installer, usually included with Python.

### Setup Steps

1.  **Navigate to the Backend Directory:**
    Open your terminal and change to the backend directory:
    ```bash
    cd knowledge_nexus/backend
    ```
    *(Adjust `knowledge_nexus/` if your project is cloned under a different root name).*

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.

    *   **Create the environment (e.g., named `venv`):**
        ```bash
        python3 -m venv venv
        ```
        *(On Windows, you might use `python` instead of `python3`)*

    *   **Activate the environment:**
        *   On macOS and Linux:
            ```bash
            source venv/bin/activate
            ```
        *   On Windows (Git Bash or PowerShell):
            ```bash
            source venv/Scripts/activate
            ```
        *   On Windows (Command Prompt):
            ```bash
            venv\Scripts\activate
            ```
        Your terminal prompt should change to indicate that the virtual environment is active (e.g., `(venv)`).

3.  **Install Dependencies:**
    Install all required Python packages listed in `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    The backend uses a `.env` file for configuration, such as API keys, database connection strings, or other settings.
    *   Locate or create a file named `.env` in the `backend/` directory.
    *   Populate it with the necessary key-value pairs. Example:
        ```env
        # backend/.env
        OPENAI_API_KEY="your_openai_api_key_here"
        LANGSMITH_API_KEY="your_langsmith_api_key_here"
        # Add other necessary environment variables
        ```
    *   Ensure this `.env` file is listed in your `.gitignore` file to prevent committing sensitive information. The `python-dotenv` package (listed in `requirements.txt`) will automatically load these variables when the application starts.

5.  **Run the Backend Server:**
    Once the dependencies are installed and environment variables are set up, you can run the FastAPI development server using Uvicorn:
    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   `backend.main:app`: Points Uvicorn to the `app` instance in the `main.py` file located in the `backend` directory.
    *   `--reload`: Enables auto-reloading the server when code changes are detected. Ideal for development.
    *   `--host 0.0.0.0`: Makes the server accessible from your local network (not just `localhost`).
    *   `--port 8000`: Specifies the port on which the server will listen.

    You should see output indicating that the Uvicorn server is running and listening on `http://0.0.0.0:8000`. You can access the API documentation (usually Swagger UI) at `http://localhost:8000/docs`.

### Deactivating the Virtual Environment
When you're done working, you can deactivate the virtual environment:
```bash
deactivate
```
