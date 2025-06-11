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
