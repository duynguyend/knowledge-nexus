# Knowledge Nexus

## Project Overview

**Project Name:** Knowledge Nexus

**Main Purpose:** Knowledge Nexus is a multi-agent AI application designed to provide users with thoroughly researched, verified, and professionally presented knowledge on any given topic.

**Key Capabilities:**
- **Automated Internet Research:** Leverages advanced AI agents to scour the internet for relevant information.
- **Data Verification with Human Oversight:** Incorporates a robust data verification process, enhanced by human oversight, to ensure accuracy and reliability.
- **Knowledge Storage:** Efficiently stores researched and verified information, creating a rich and organized knowledge base.
- **Content Synthesis:** AI agents excel at synthesizing disparate pieces of information into coherent, well-structured content.
- **Tailored Document Generation:** Generates customized documents based on the synthesized knowledge in various formats.

**Problem Solved:** In an age of information overload and rampant misinformation, Knowledge Nexus addresses a critical need for reliable and trustworthy knowledge. By combining the speed and efficiency of AI with the critical judgment of human oversight, it offers an unparalleled solution for accessing verified information.


## System Architecture

The Knowledge Nexus application employs a modern, multi-component architecture designed for scalability and maintainability.

### Main Components:

*   **Frontend:** Developed using **React**, the frontend provides a dynamic and responsive user interface. It handles user interactions, sends requests to the backend, and displays the processed knowledge, including real-time updates and interfaces for human oversight.
*   **Backend:** Built with **Python**, the backend leverages:
    *   **FastAPI:** A high-performance web framework for creating API endpoints that the frontend interacts with. It handles request/response cycles and asynchronous operations.
    *   **LangGraph:** The core of the multi-agent system, LangGraph orchestrates the workflows between different AI agents (e.g., Researcher, Verifier, Synthesizer), manages state, and integrates human-in-the-loop processes.
*   **Database:**
    *   **ChromaDB:** A specialized vector database used for storing and retrieving text embeddings. This is crucial for efficient similarity searches, supporting Retrieval Augmented Generation (RAG) for the AI agents, and managing the knowledge base.

### Architecture Diagram:

The overall architecture can be visualized as follows:

```
+-------------------+      HTTP/WebSocket     +-----------------------------+
|     Frontend      | <---------------------> |           Backend           |
|    (React App)    |                         | (FastAPI + LangGraph Agents)|
+-------------------+                         +-----------------------------+
        ^                                                 |
        | API Calls (Data, Commands)                      | Vector Embeddings,
        |                                                 | Storage & Retrieval
        |                                                 v
        +-------------------------------------------> +----------------------+
                                                      |       ChromaDB       |
                                                      | (Vector Database)    |
                                                      +----------------------+
```

**Flow:**

1.  The **Frontend (React)** sends user requests (e.g., topic for research) to the **Backend (FastAPI)**.
2.  **FastAPI** receives the request and triggers a workflow orchestrated by **LangGraph**.
3.  **LangGraph Agents** perform tasks such as research, verification, and synthesis. During these processes, they interact with:
    *   External data sources (e.g., internet APIs).
    *   **ChromaDB** for storing and retrieving relevant vectorized information.
    *   Human users via the frontend for oversight and verification steps.
4.  Results and updates are streamed or sent back to the **Frontend** for display to the user.


## Project Structure

The Knowledge Nexus project is organized into top-level `backend/` and `frontend/` directories, alongside other supporting files and folders. The active development code resides directly within these `backend/` and `frontend/` folders at the repository root.

```
.
├── backend/
│   ├── agents/
│   ├── tools/
│   ├── models/
│   ├── services/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   └── App.js
│   ├── package.json
│   └── ...
├── design/
│   └── ...
├── chroma_db_store/
└── README.md
```

An older directory named `knowledge_nexus/` also exists at the root; it contains outdated or redundant code and should be ignored. Attempts to remove or rename this legacy directory were unsuccessful due to tooling limitations.

### Key Directory Descriptions:

*   **`./` (Repository Root):**
    *   This is the main container for the entire project. The primary active directories are `backend/` and `frontend/`, alongside design documents and other project-level files.

*   **`backend/` (Top-Level Directory):**
    *   Houses the Python-based backend application.
    *   **`main.py`**: The entry point for the FastAPI application.
    *   **`agents/`**: Contains definitions and logic for the LangGraph agents (e.g., Researcher, Verifier, Synthesizer).
    *   **`tools/`**: Custom Python functions and tools used by the LangGraph agents.
    *   **`models/`**: Pydantic models for data validation and serialization (API request/response schemas).
    *   **`services/`**: Modules for integrating with external services, such as the ChromaDB client (`chroma_service.py`) and LLM integrations.
    *   **`requirements.txt`**: Lists the Python dependencies for the backend.
    *   **`.env` (or `.env.example`)**: Used for managing environment variables (e.g., API keys, database paths).

*   **`frontend/` (Top-Level Directory):**
    *   Contains the React-based frontend application.
    *   **`src/`**: The primary folder for React components, pages, services, and other JavaScript/TypeScript code.
    *   **`public/`**: Stores static assets like `index.html`, favicons, and images.
    *   **`package.json`**: Defines frontend project metadata, dependencies (managed by npm or yarn), and scripts (like `start`, `build`).

*   **`design/` (Top-Level Directory):**
    *   Stores all project design and planning documents.
    *   **`requirement.md`**: Initial requirements and high-level goals.
    *   **`SRS.md` (Software Requirement Specification)**: Detailed description of the software's capabilities, features, and constraints.
    *   **`system_architecture.md`**: Documentation of the overall system architecture, including components, interactions, and technology stack.

*   **`chroma_db_store/` (Top-Level Directory):**
    *   This directory is the default location where ChromaDB persists its vector database files when configured for local storage. The exact path might be configured in the backend (`ChromaService` typically specifies a `persist_directory`). It's crucial for maintaining the knowledge base between application restarts. This directory will be created automatically by ChromaDB if it doesn't exist when data is first persisted.

This structure helps in organizing the codebase logically, separating concerns between the frontend, backend, and design documentation.


## Backend Development Setup

This section outlines the steps to set up and run the backend server for Knowledge Nexus.

### Prerequisites

*   **Python:** Python 3.9 or newer is recommended.
*   **Pip:** Python's package installer, usually included with Python.

### Setup Steps

1.  **Navigate to the Backend Directory:**
    Open your terminal and change to the backend directory:
    ```bash
    cd backend
    ```

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
    *   Create a `.env` file in the `backend/` directory by copying the `backend/.env.example` file:
        ```bash
        cp backend/.env.example backend/.env
        ```
    *   Then, populate `backend/.env` with your specific key-value pairs. The application is configured to use Azure OpenAI by default if the relevant variables are set.

    *   **Key Environment Variables (refer to `backend/.env.example` for a full list):**
        *   `TAVILY_API_KEY`: Your API key for Tavily Search.
        *   `AZURE_OPENAI_API_KEY`: Your API key for Azure OpenAI.
        *   `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI service endpoint (e.g., `https://your-resource-name.openai.azure.com/`).
        *   `OPENAI_API_VERSION`: The API version for Azure OpenAI (e.g., `2023-07-01-preview`).
        *   `AZURE_OPENAI_DEPLOYMENT_NAME`: The name of your model deployment in Azure AI Studio.
        *   `OPENAI_API_KEY` (Optional): Standard OpenAI API key. Can be used if Azure variables are not set and fallback is implemented, or for other OpenAI direct uses.

    *   Example content for `backend/.env`:
        ```env
        # backend/.env
        TAVILY_API_KEY="your_tavily_api_key"

        # Azure OpenAI Credentials (Recommended)
        AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
        AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
        OPENAI_API_VERSION="2023-07-01-preview"
        AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"

        # Optional: Standard OpenAI API Key (if not using Azure or for fallback)
        # OPENAI_API_KEY="your_openai_api_key_here"

        # Langsmith API Key (if used)
        # LANGSMITH_API_KEY="your_langsmith_api_key_here"
        ```
    *   Ensure the `.env` file is listed in your `.gitignore` file to prevent committing sensitive information. The `python-dotenv` package (listed in `requirements.txt`) will automatically load these variables when the application starts.

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


## Running the Application

To run the Knowledge Nexus application locally, both the backend and frontend development servers must be running simultaneously. They typically operate in separate terminal sessions.

1.  **Start the Backend Server:**
    *   Navigate to the `backend` directory.
    *   Ensure your Python virtual environment is activated.
    *   Run the command:
        ```bash
        uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
        ```
    *   The backend API server will typically be available at `http://localhost:8000`.

2.  **Start the Frontend Development Server:**
    *   Navigate to the `frontend` directory.
    *   Run the command:
        ```bash
        npm start
        ```
    *   The frontend React application will typically open automatically in your web browser at `http://localhost:3000`.

**Once both servers are running:**

*   You can access the Knowledge Nexus application by navigating to `http://localhost:3000` in your web browser.
*   The frontend application is configured to send API requests to the backend server (usually at `http://localhost:8000`).

Ensure that any necessary environment variables (e.g., API keys for backend services, API base URL for the frontend) are correctly configured in their respective `.env` files before starting the servers. Refer to the backend and frontend setup sections for details on environment variables.
