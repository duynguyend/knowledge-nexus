## Project Structure

The Knowledge Nexus project is organized into several key directories. The main structure, typically rooted in a `knowledge_nexus/` directory (or your chosen repository name), is as follows:

```
knowledge_nexus/
├── backend/
│   ├── agents/
│   ├── tools/
│   ├── models/
│   ├── services/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── ... (other Python modules)
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   ├── package.json
│   └── ... (other React app files)
├── design/
│   ├── requirement.md
│   ├── SRS.md
│   └── system_architecture.md
├── chroma_db_store/  (Example name, location may vary based on backend config)
└── README.md
```

### Key Directory Descriptions:

*   **`knowledge_nexus/` (Root Directory):**
    *   This is the main container for the entire project, including both the backend and frontend applications, as well as design documents and other project-level files.

*   **`knowledge_nexus/backend/`:**
    *   Houses the Python-based backend application.
    *   **`main.py`**: The entry point for the FastAPI application.
    *   **`agents/`**: Contains definitions and logic for the LangGraph agents (e.g., Researcher, Verifier, Synthesizer).
    *   **`tools/`**: Custom Python functions and tools used by the LangGraph agents.
    *   **`models/`**: Pydantic models for data validation and serialization (API request/response schemas).
    *   **`services/`**: Modules for integrating with external services, such as the ChromaDB client (`chroma_service.py`) and LLM integrations.
    *   **`requirements.txt`**: Lists the Python dependencies for the backend.
    *   **`.env` (or `.env.example`)**: Used for managing environment variables (e.g., API keys, database paths).

*   **`knowledge_nexus/frontend/`:**
    *   Contains the React-based frontend application.
    *   **`src/`**: The primary folder for React components, pages, services, and other JavaScript/TypeScript code.
    *   **`public/`**: Stores static assets like `index.html`, favicons, and images.
    *   **`package.json`**: Defines frontend project metadata, dependencies (managed by npm or yarn), and scripts (like `start`, `build`).

*   **`knowledge_nexus/design/`:**
    *   Stores all project design and planning documents.
    *   **`requirement.md`**: Initial requirements and high-level goals.
    *   **`SRS.md` (Software Requirement Specification)**: Detailed description of the software's capabilities, features, and constraints.
    *   **`system_architecture.md`**: Documentation of the overall system architecture, including components, interactions, and technology stack.

*   **`chroma_db_store/` (or similar, e.g., `backend/chroma_db/`):**
    *   This directory is the default location where ChromaDB persists its vector database files when configured for local storage. The exact path might be configured in the backend (`ChromaService` typically specifies a `persist_directory`). It's crucial for maintaining the knowledge base between application restarts. This directory will be created automatically by ChromaDB if it doesn't exist when data is first persisted.

This structure helps in organizing the codebase logically, separating concerns between the frontend, backend, and design documentation.
