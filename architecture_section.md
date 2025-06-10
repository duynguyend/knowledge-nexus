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
