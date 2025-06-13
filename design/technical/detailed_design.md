# Knowledge Nexus: Detailed Design Document

## 1. Introduction
- Purpose of this document.
- Brief overview of Knowledge Nexus: a multi-agent AI application for researched, verified, and professionally presented knowledge.
- Key goals: automated research, data verification with human oversight, knowledge storage, content synthesis, tailored document generation.

## 2. System Architecture

### 2.1. Overview
- High-level description of the multi-component architecture (Frontend, Backend, Database).
- Architecture Diagram (reuse and update from `system_architecture.md`):
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

### 2.2. Technology Stack
- **Frontend:** React (with Create React App), JavaScript/JSX, CSS, Axios (for HTTP).
- **Backend:** Python (3.9+), FastAPI (web framework), Uvicorn (ASGI server), LangGraph (multi-agent orchestration), Pydantic (data validation).
- **Database:** ChromaDB (vector database).
- **Search:** Google Custom Search API.
- **Language Models (LLMs):** Azure OpenAI services (preferred), Standard OpenAI API (fallback).
- **Embeddings:** Azure OpenAI Embedding services (via `chroma_service.py`).

### 2.3. Inter-Agent Communication and Data Flow
- **User Interaction:** User initiates research via Frontend -> FastAPI endpoint.
- **Task Initiation:** FastAPI creates a task, initializes `KnowledgeNexusState`, and starts the LangGraph workflow in the background.
- **LangGraph Workflow:**
    - Agents (nodes in the graph) operate sequentially or conditionally based on the `KnowledgeNexusState`.
    - Data is passed between agents by modifying fields within the `KnowledgeNexusState` object.
    - Agents use services (like `ChromaService`, LLM clients, Google Search client) to perform their tasks.
- **Human-in-the-Loop (HITL):**
    - If an agent (e.g., `verify_node`) determines human input is needed, it sets `human_in_loop_needed = True` and populates `current_verification_request` in `KnowledgeNexusState`.
    - The workflow transitions to `await_human_input_node` and effectively pauses (the `run_research_workflow_async` task for that `task_id` exits).
    - Frontend polls `/status/{task_id}`, sees `awaiting_human_verification` and `verification_request` data, and presents UI for human.
    - Human submits feedback via Frontend -> `/submit-verification/{task_id}` endpoint in `main.py`.
    - `main.py` updates `KnowledgeNexusState` with `human_feedback` and re-triggers `run_research_workflow_async` with the modified state.
    - `await_human_input_node` processes the feedback, clears flags, and the workflow continues (typically to `synthesize_node`).
- **Data Storage:** `research_node` stores fetched content and metadata in ChromaDB (one collection per `task_id`), using `AzureOpenAIEmbeddingFunction`.
- **Results:** Final document is stored in `KnowledgeNexusState` and retrieved via `/results/{task_id}`.

## 3. Module Breakdown

### 3.1. Frontend (`frontend/`)
- **Purpose:** Provides the user interface for initiating research, monitoring progress, performing human verification, and viewing results.
- **Key Components (Conceptual):**
    - `ResearchInput`: Form for users to submit research topics.
    - `ProgressDisplay`: Shows the current status (`current_stage`), progress percentage, and logs/messages for a task.
    - `VerificationInterface`: Displays data flagged for human review (`DataVerificationRequest`) and allows submission of `HumanApproval`.
    - `ResultsView`: Presents the final generated document.

### 3.2. Backend (`backend/`)

#### 3.2.1. `main.py` (FastAPI Application)
- **Responsibilities:**
    - Exposes HTTP API endpoints for frontend interaction.
    - Manages the lifecycle of research tasks (creation, status tracking, results retrieval).
    - Handles Human-in-the-Loop (HITL) interactions by receiving verification data.
    - Initializes and manages `ChromaService` and the LangGraph `knowledge_nexus_graph`.
    - Handles LLM availability warnings.
- **Key Endpoints:**
    - `POST /research`: Initiates a new research task.
    - `GET /status/{task_id}`: Provides detailed status, progress, and data for HITL if needed.
    - `POST /submit-verification/{task_id}`: Receives human verification decisions.
    - `GET /results/{task_id}`: Retrieves the final generated document.
    - `GET /health`: Health check.

#### 3.2.2. `agents/research_workflow.py` (LangGraph Workflow & Agents)
- **`KnowledgeNexusState` (TypedDict):** Central data structure holding all information for a task as it moves through the graph. (Details in Data Models section).
- **LLM Initialization (`build_knowledge_nexus_workflow`):**
    - Prioritizes Azure OpenAI (`AzureChatOpenAI`).
    - Falls back to Standard OpenAI (`ChatOpenAI`) if Azure is not configured.
    - If neither is configured or initialization fails, `llm_instance` is `None`, and agents use simulated responses.
    - Returns the compiled graph and an `llm_initialized_boolean` flag.
- **Agent Nodes:**
    - **`research_node`:**
        - Takes `topic` and `task_id` from state.
        - Sets `current_stage` to "researching".
        - Uses Google Custom Search API (via `googleapiclient`) to find relevant information.
        - **Fallback:** If Google API keys (`GOOGLE_API_KEY`, `GOOGLE_CSE_ID`) are missing or invalid, uses simulated search data.
        - Processes search results (snippets, URLs, titles).
        - Stores processed results in `state['research_data']` and updates `sources_explored`, `data_collected`.
        - Adds document snippets to ChromaDB using `chroma_service.add_documents` (collection named by `task_id`).
    - **`verify_node`:**
        - Sets `current_stage` to "verifying".
        - Currently, it's a pass-through for all data from `research_data` to `verified_data`.
        - **HITL Trigger (Potential):** Designed to set `state['human_in_loop_needed'] = True` and populate `state['current_verification_request']` if a piece of data needs human review (though currently this trigger is inactive by default in the node's code, the overall system supports it).
    - **`await_human_input_node`:**
        - If entered with `state['human_feedback']` present (meaning feedback was submitted):
            - Sets `current_stage` to "processing_human_feedback".
            - Processes the feedback (e.g., updates the status of the data item, incorporates corrected content).
            - Clears `human_in_loop_needed`, `current_verification_request`, and `human_feedback`.
        - If entered because `human_in_loop_needed` is true but no `human_feedback` (i.e., workflow is pausing):
            - Sets `current_stage` to "awaiting_human_verification".
            - The graph execution for this task pauses here until feedback is provided via the API.
    - **`synthesize_node`:**
        - Sets `current_stage` to "synthesizing".
        - Takes `state['verified_data']`.
        - If LLM (`llm_instance`) is available:
            - Formats verified data into a context string.
            - Constructs a prompt instructing the LLM to synthesize a coherent summary.
            - Invokes the LLM and stores the result in `state['synthesized_content']`.
        - **Fallback:** If LLM is unavailable or fails, generates simulated synthesized content.
    - **`conflict_detection_node`:**
        - Sets `current_stage` to "detecting_conflicts".
        - Currently a placeholder; sets `state['detected_conflicts']` to an empty list.
        - Intended to analyze data for contradictions.
    - **`document_generation_node`:**
        - Sets `current_stage` to "generating_document".
        - Takes `state['synthesized_content']`.
        - If LLM is available: Can be used for advanced formatting (currently passes through synthesized content with basic Markdown structure).
        - **Fallback:** If LLM is unavailable or content is placeholder, generates a simulated document structure.
        - Stores the final document text in `state['final_document']`.
- **Conditional Edges:**
    - `verify` node leads to `should_request_human_verification` (conditional function):
        - If `human_in_loop_needed` is true and `current_verification_request` exists: routes to `await_human_input`.
        - Otherwise: routes to `synthesize`.
    - `await_human_input` always routes to `synthesize` after processing/pausing.

#### 3.2.3. `services/chroma_service.py`
- **Responsibilities:** Abstraction layer for interacting with ChromaDB.
- **Embedding Function:** Uses `AzureOpenAIEmbeddingFunction`, which requires Azure OpenAI environment variables for embeddings (`AZURE_OPENAI_EMBEDDING_API_KEY`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`, `AZURE_OPENAI_ENDPOINT`, `OPENAI_API_VERSION`). Fails initialization if these are not set.
- **Key Methods:**
    - `get_or_create_collection(collection_name)`: Uses `collection_name` (typically `task_id`).
    - `add_documents(collection_name, documents, metadatas, ids)`
    - `query_documents(collection_name, query_texts, n_results)`
    - `get_document_by_id(collection_name, doc_id)`

## 4. Data Models/Schema

### 4.1. `KnowledgeNexusState` (LangGraph State - `agents/research_workflow.py`)
- `topic: str`: The user-provided research topic.
- `task_id: str`: Unique identifier for the research task.
- `current_stage: str`: Human-readable description of the current processing stage (e.g., "researching", "awaiting_human_verification").
- `research_data: List[Dict[str, Any]]`: List of raw data items collected by the `research_node`. Each item is a dictionary typically including `id`, `url`, `title`, `snippet`, `raw_content`, `score`, `source_name`.
- `verified_data: List[Dict[str, Any]]`: List of data items after the verification step. Structure similar to `research_data`.
- `synthesized_content: str`: The coherent summary generated by the `synthesize_node`.
- `detected_conflicts: List[Dict[str, Any]]`: List of identified conflicts (currently placeholder).
- `final_document: str`: The final, formatted knowledge document.
- `human_in_loop_needed: bool`: Flag indicating if the workflow should pause for human input.
- `current_verification_request: Optional[DataVerificationRequest]`: Holds the data needing verification when paused.
- `messages: List[BaseMessage]`: History of messages for LLM interactions (if applicable).
- `error_message: Optional[str]`: Stores any error message occurring during workflow execution.
- `human_feedback: Optional[HumanApproval]`: Stores the feedback received from a human for a verification request. Consumed after processing.
- `sources_explored: int`: Counter for the number of sources investigated by `research_node`.
- `data_collected: int`: Counter for the number of data items collected by `research_node`.

### 4.2. API Data Models (Pydantic Schemas - `models/schemas.py`)
- **`ResearchRequest`**:
    - `topic: str`
- **`ResearchStatus`**:
    - `task_id: str`
    - `status: str` (Reflects `current_stage` from `KnowledgeNexusState`)
    - `message: Optional[str]`
    - `progress: Optional[float]` (Calculated based on `current_stage`)
    - `sources_explored: Optional[int]`
    - `data_collected: Optional[int]`
    - `timestamp: datetime`
    - `verification_request: Optional[DataVerificationRequest]` (Sent to frontend if status is `awaiting_human_verification`)
- **`DocumentOutput`**:
    - `task_id: str`
    - `document_content: str`
    - `format: str` (e.g., "markdown")
- **`DataSource`**:
    - `id: str`
    - `url: Optional[str]`
    - `content_preview: str`
- **`DataVerificationRequest`**:
    - `task_id: str`
    - `data_id: str` (ID of the specific piece of data to verify)
    - `data_to_verify: DataSource` (The data item itself)
    - `conflicting_sources: Optional[List[DataSource]]`
- **`HumanApproval`**:
    - `task_id: str`
    - `data_id: str` (Matching `DataVerificationRequest.data_id`)
    - `approved: bool`
    - `notes: Optional[str]`
    - `corrected_content: Optional[str]`
- **`Conflict` (Planned Feature)**:
    - `conflict_id: str`
    - `task_id: str`
    - `description: str`
    - `sources_involved: List[DataSource]`
    - `suggested_resolution: Optional[str]`
- **`ConflictResolution` (Planned Feature)**:
    - `conflict_id: str`
    - `task_id: str`
    - `chosen_resolution: str`
    - `user_notes: Optional[str]`

### 4.3. ChromaDB Storage
- One collection is typically created per `task_id`.
- Stores document chunks (e.g., snippets from search results).
- **Embeddings:** Generated using `AzureOpenAIEmbeddingFunction`.
- **Metadata per document chunk:** Includes `source_url`, `title`, `research_topic`, `original_id_from_source`.

## 5. Key Algorithms/Logic

### 5.1. LLM Fallback Mechanism
- **Initialization:** During `build_knowledge_nexus_workflow`:
    1. Attempts to initialize `AzureChatOpenAI` using Azure-specific environment variables.
    2. If Azure vars are missing or initialization fails, it attempts to initialize `ChatOpenAI` using `OPENAI_API_KEY`.
    3. If both fail, `llm_instance` remains `None`.
- **Agent Behavior:** Nodes like `synthesize_node` and `document_generation_node` check if `llm_instance` is available:
    - If yes: Proceed with LLM-based operations.
    - If no (or if LLM call fails): Fall back to generating simulated/placeholder content (e.g., "Simulated synthesis for topic 'X'...") and log warnings.
- **User Notification:** `main.py` checks the `llm_initialized_boolean` flag from `build_knowledge_nexus_workflow` and prints a prominent console warning if no LLM is available, indicating degraded mode.

### 5.2. Simulated Search Data
- In `research_node`, if Google Custom Search API keys (`GOOGLE_API_KEY`, `GOOGLE_CSE_ID`) are not found in environment variables or are set to placeholder values:
    - The node bypasses the API call.
    - It generates a predefined list of simulated search results relevant to the topic.
    - This allows the workflow to proceed for testing or development without live search capabilities. A warning is logged.

### 5.3. Human-in-the-Loop (HITL) Process
1.  **Flagging:** A node (e.g., `verify_node`, though currently passive) can identify data needing human review. It sets `human_in_loop_needed = True` and populates `current_verification_request` in `KnowledgeNexusState` with details of the item to be verified.
2.  **Pausing:** The LangGraph workflow, via a conditional edge, transitions to `await_human_input_node`. If no `human_feedback` is present in the state, this node sets `current_stage` to `awaiting_human_verification`. The `run_research_workflow_async` function for this specific `task_id` then finishes its current execution, effectively pausing the workflow for that task.
3.  **Frontend Notification:** The frontend polls `/status/{task_id}`. The response includes `status: "awaiting_human_verification"` and the `verification_request` data. The UI uses this to display the necessary information to the user.
4.  **User Submission:** The user reviews the data and submits their decision (approve/reject, notes, corrections) via the frontend. This triggers a `POST` request to `/submit-verification/{task_id}` with `HumanApproval` data.
5.  **Backend Processing:** The `/submit-verification` endpoint in `main.py`:
    - Retrieves the task's current `KnowledgeNexusState` from `active_tasks`.
    - Injects the received `HumanApproval` data into `state['human_feedback']`.
    - Updates the task's overall status to "resuming_after_verification".
    - Schedules `run_research_workflow_async` to run again in the background, passing in the modified `KnowledgeNexusState`.
6.  **Workflow Resumption:** `run_research_workflow_async` restarts the LangGraph stream for the task using the updated state. The graph, now containing `human_feedback`, re-enters `await_human_input_node`.
7.  **Feedback Application:** `await_human_input_node` detects `human_feedback`, processes it (e.g., updates the data item's status or content within `verified_data`), clears `human_in_loop_needed`, `current_verification_request`, and `human_feedback`, and sets `current_stage` to "processing_human_feedback".
8.  **Continuation:** The workflow then transitions from `await_human_input_node` to the next appropriate node (e.g., `synthesize_node`).

### 5.4. ChromaDB Embedding Strategy
- `ChromaService` is hardcoded to use `AzureOpenAIEmbeddingFunction`.
- This function relies on specific Azure environment variables: `AZURE_OPENAI_EMBEDDING_API_KEY`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`, `AZURE_OPENAI_ENDPOINT`, and `OPENAI_API_VERSION`.
- If these variables are not correctly configured, `ChromaService` will fail to initialize, preventing any vector store operations. Researched data will not be embedded or stored in ChromaDB.

## 6. Deployment

### 6.1. Backend
- **Environment:** Python 3.9+ environment with dependencies from `backend/requirements.txt`.
- **Server:** Deployed as an ASGI application using a server like Uvicorn with Gunicorn workers for production (e.g., `gunicorn -k uvicorn.workers.UvicornWorker backend.main:app`).
- **Configuration:** All necessary environment variables (API keys for Google Search, Azure OpenAI LLM, Azure OpenAI Embeddings; ChromaDB path) must be set in the deployment environment.
- **Database:** ChromaDB will create and use the specified `persist_directory` (e.g., `./chroma_db_store`) on the server's filesystem. Ensure this path is writable and persistent if needed across deployments. For more robust deployments, a managed ChromaDB instance or alternative vector DB could be considered.

### 6.2. Frontend
- **Build:** Build the React application into static assets using `npm run build` in the `frontend/` directory.
- **Serving:** Serve the generated static files (from `frontend/build/`) using a web server like Nginx, Apache, or a cloud storage service with static website hosting capabilities (e.g., AWS S3, Azure Blob Storage).
- **Configuration:** The frontend needs to know the backend API URL. This is typically configured via `REACT_APP_API_BASE_URL` in a `.env` file at build time or through runtime configuration if the serving platform allows.

### 6.3. Infrastructure Requirements
- Server(s) or container platform for hosting the backend Python application.
- Web server or static hosting solution for the frontend.
- Network access for the backend to:
    - Google Custom Search API.
    - Azure OpenAI API endpoints (for LLM and embeddings).
    - Standard OpenAI API endpoint (if used as fallback).
- Persistent storage for ChromaDB data if local persistence is used.

### 6.4. Scalability Considerations
- **Task Management:** The current in-memory task store (`active_tasks` in `main.py`) is not suitable for production scaling or persistence across restarts. For a scalable solution, a distributed task queue (e.g., Celery with Redis/RabbitMQ) should be implemented to manage background LangGraph workflows.
- **LangGraph State Persistence:** For long-running or critical tasks, LangGraph's state should be persisted using a more robust checkpointing mechanism than the in-memory `active_tasks` dictionary (e.g., LangGraph's built-in SQLite or Redis checkpointers).
- **Stateless Backend Instances:** If scaling the backend horizontally (multiple instances), task management and state persistence must be handled by external services to allow any instance to pick up or continue work.
- **ChromaDB:** For high query loads or large datasets, consider a managed ChromaDB deployment or alternative scalable vector database solutions.

## 7. Development Practices

### 7.1. Backend
- **Virtual Environments:** Python virtual environments (e.g., `venv`) are used to manage project dependencies and isolate them from the global Python installation. Dependencies are listed in `backend/requirements.txt`.
- **Configuration:** Sensitive information and environment-specific settings (API keys, database paths) are managed using a `.env` file in the `backend/` directory, loaded by `python-dotenv`. An example file `backend/.env.example` is provided.
- **Modularity:** Code is organized into modules: `agents/` for LangGraph workflow logic, `services/` for external service integrations (like ChromaDB), `models/` for Pydantic data schemas, and `main.py` for the FastAPI application.
- **Testing:** Basic unit/integration tests exist (e.g., `backend/tests/test_research_workflow.py`, `backend/test_main.py`), suggesting pytest or a similar framework is used.

### 7.2. Frontend
- **Package Management:** `npm` is used for managing frontend dependencies, listed in `frontend/package.json`.
- **Development Server:** `npm start` runs a local development server with hot reloading.
- **Configuration:** Environment variables for the frontend (like `REACT_APP_API_BASE_URL`) are managed via `.env` files in the `frontend/` directory, following Create React App conventions.
- **Component-Based Architecture:** React components are organized within `frontend/src/components/`.

### 7.3. General
- **Version Control:** Git is used for version control (implied by `.gitignore` files).
- **Code Style & Linting:** (Not explicitly specified, but common practice) Linters like Flake8 (Python) and ESLint/Prettier (JavaScript/React) would typically be used.
