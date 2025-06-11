import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime # Added for ResearchStatus timestamp

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Project-specific imports
try:
    # Added HumanApproval and DataVerificationRequest for HITL
    from .models.schemas import ResearchRequest, ResearchStatus, DocumentOutput, HumanApproval, DataVerificationRequest
    from .agents.research_workflow import build_knowledge_nexus_workflow, KnowledgeNexusState
    from .services.chroma_service import ChromaService
except ImportError as e:
    # This block is a fallback for local development if 'backend' is not in PYTHONPATH
    # or if running main.py directly from within the 'backend' directory.
    print(f"Relative import failed: {e}. Attempting sys.path modification for local development.")
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"Added '{project_root}' to sys.path for package resolution.")

    try:
        from backend.models.schemas import ResearchRequest, ResearchStatus, DocumentOutput, HumanApproval, DataVerificationRequest
        from backend.agents.research_workflow import build_knowledge_nexus_workflow, KnowledgeNexusState
        from backend.services.chroma_service import ChromaService
    except ImportError as final_e:
        print(f"Fallback imports also failed: {final_e}. Critical service or model definitions might be missing.")
        class ResearchRequest: pass
        class ResearchStatus: pass
        class DocumentOutput: pass
        class HumanApproval: pass # Added dummy
        class DataVerificationRequest: pass # Added dummy
        class KnowledgeNexusState(dict): pass
        class ChromaService: pass
        def build_knowledge_nexus_workflow(chroma_service):
            print("Dummy build_knowledge_nexus_workflow called. Real workflow could not be loaded.")
            return None

# --- Application Initialization ---
app = FastAPI(
    title="Knowledge Nexus API",
    description="API for orchestrating research and knowledge synthesis agents.",
    version="0.1.0"
)

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Services Initialization ---
chroma_service_instance: Optional[ChromaService] = None
knowledge_nexus_graph: Optional[Any] = None
try:
    chroma_service_instance = ChromaService(persist_directory="./chroma_db_store")
    knowledge_nexus_graph = build_knowledge_nexus_workflow(chroma_service=chroma_service_instance)
    if not knowledge_nexus_graph:
        print("Warning: Knowledge Nexus workflow graph failed to initialize properly but no exception was raised.")
except Exception as e:
    print(f"Critical Error: Failed to initialize ChromaService or Knowledge Nexus workflow: {e}")

# --- In-Memory Task Store ---
active_tasks: Dict[str, Dict[str, Any]] = {}

# --- Background Workflow Execution ---
async def run_research_workflow_async(task_id: str, topic: str, initial_graph_input: KnowledgeNexusState):
    if not knowledge_nexus_graph:
        active_tasks[task_id].update({"status": "failed", "error_message": "Workflow engine not available."})
        print(f"Task {task_id}: Failed - Workflow engine not initialized.")
        return

    print(f"Task {task_id}: Background research process evaluation for topic '{topic}'.")

    # Determine the input state for the workflow
    # If resuming, use the already modified state from active_tasks which includes human_feedback
    if active_tasks[task_id].get("status") == "resuming_after_verification":
        print(f"Task {task_id}: Attempting to resume workflow with stored state.")
        current_input_state = active_tasks[task_id].get('graph_state', initial_graph_input)
        # Ensure human_feedback is correctly placed in current_input_state if not already
        # (it should have been placed there by /submit-verification)
    else: # Starting fresh
        print(f"Task {task_id}: Starting fresh workflow run.")
        current_input_state = initial_graph_input

    active_tasks[task_id]["status"] = "running" # Set status to running (either fresh or resuming)


    try:
        config = {"configurable": {"thread_id": task_id}}
        final_event_state = None # Keep track of the very last state from the stream

        async for event in knowledge_nexus_graph.astream(current_input_state, config=config):
            if not event: continue

            latest_node_name = list(event.keys())[-1]
            current_state_after_node = event[latest_node_name]
            final_event_state = current_state_after_node # Update with the latest state

            # Persist the full state after each node
            active_tasks[task_id]['graph_state'] = current_state_after_node
            active_tasks[task_id]['last_event_node'] = latest_node_name

            print(f"Task {task_id}: Processed node '{latest_node_name}'.")

            if current_state_after_node.get('error_message'):
                active_tasks[task_id].update({"status": "error_in_workflow", "error_message": current_state_after_node['error_message']})
                print(f"Task {task_id}: Error reported by workflow: {current_state_after_node['error_message']}")
                return # Stop processing on error

            # Check if the workflow is pausing for human input
            if current_state_after_node.get('human_in_loop_needed') and \
               current_state_after_node.get('current_verification_request'):
                print(f"Task {task_id}: Pausing for human input at node '{latest_node_name}'. Verification request for data ID: {current_state_after_node['current_verification_request']['data_id']}")
                active_tasks[task_id]['status'] = "awaiting_human_verification"
                # Workflow effectively pauses here for this task_id.
                # The current run_research_workflow_async will exit.
                # The /submit-verification endpoint will update the state in active_tasks
                # and then re-trigger run_research_workflow_async.
                return # Exit this execution of run_research_workflow_async

        # If the stream completes without pausing for human input or erroring out:
        # This means the graph ran to an END node.
        if final_event_state:
             active_tasks[task_id].update({
                "status": "completed",
                # Use final_event_state which is the state after the last node that led to END
                "final_document_preview": final_event_state.get('final_document', '')[:250] + "...",
                "final_graph_state": final_event_state
            })
             print(f"Task {task_id}: Workflow completed successfully.")
        else:
            # This case might occur if the stream somehow ends without any event after resumption,
            # or if initial_graph_input was already a terminal state.
            if active_tasks[task_id]["status"] == "running": # If it was running and just finished without specific end state
                 active_tasks[task_id].update({"status": "unknown_completion", "error_message": "Workflow stream ended without a definitive final state but was running."})
                 print(f"Task {task_id}: Workflow stream ended without explicit completion or error, after being in 'running' state.")


    except Exception as e:
        print(f"Task {task_id}: Critical error during workflow execution: {e}", exc_info=True)
        active_tasks[task_id].update({"status": "failed", "error_message": str(e)})

# --- API Endpoints ---
@app.get("/health", summary="Health Check", tags=["General"])
async def health_check():
    return {
        "status": "ok",
        "services": {
            "chroma_service": "initialized" if chroma_service_instance else "failed",
            "knowledge_nexus_graph": "initialized" if knowledge_nexus_graph else "failed"
        }
    }

@app.post("/research", response_model=ResearchStatus, status_code=202, summary="Start Research Task", tags=["Research"])
async def start_research_task_endpoint(request: ResearchRequest, background_tasks: BackgroundTasks):
    if not knowledge_nexus_graph or not chroma_service_instance:
        raise HTTPException(status_code=503, detail="Research service is currently unavailable.")

    task_id = str(uuid.uuid4())

    initial_graph_input = KnowledgeNexusState(
        topic=request.topic,
        task_id=task_id,
        research_data=[], verified_data=[], synthesized_content="",
        detected_conflicts=[], final_document="",
        human_in_loop_needed=False, current_verification_request=None,
        messages=[], error_message=None, human_feedback=None # Ensure all fields are initialized
    )

    active_tasks[task_id] = {
        "task_id": task_id, "topic": request.topic, "status": "queued",
        "graph_state": initial_graph_input, # Store the whole initial state
        "resuming_after_verification": False
    }

    background_tasks.add_task(run_research_workflow_async, task_id, request.topic, initial_graph_input)

    return ResearchStatus(
        task_id=task_id, status="queued",
        message=f"Research task for topic '{request.topic}' has been queued.",
        timestamp=datetime.utcnow()
    )

@app.get("/status/{task_id}", response_model=ResearchStatus, summary="Get Task Status", tags=["Research"])
async def get_task_status_endpoint(task_id: str):
    task = active_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID '{task_id}' not found.")

    # current_graph_state is the state of the workflow, an instance of KnowledgeNexusState (as a dict)
    current_graph_state = task.get("graph_state", {})
    status = task.get("status", "unknown")
    verification_req_data = None # This will hold DataVerificationRequest model

    if status == "awaiting_human_verification" and \
       current_graph_state.get('human_in_loop_needed') and \
       current_graph_state.get('current_verification_request'):
        # current_verification_request from graph_state should be a dict
        raw_verification_request = current_graph_state['current_verification_request']
        try:
            # Attempt to parse it into the Pydantic model for ResearchStatus
            if isinstance(raw_verification_request, dict):
                 verification_req_data = DataVerificationRequest(**raw_verification_request)
            elif isinstance(raw_verification_request, DataVerificationRequest): # If already a model instance
                 verification_req_data = raw_verification_request
            # Else, it might be None or an incompatible type, verification_req_data remains None
        except Exception as e: # Broad exception for parsing issues
            print(f"Error parsing current_verification_request for task {task_id}: {e}")
            # verification_req_data remains None

    # Placeholder for progress calculation
    current_progress = 0.0
    if status == "completed": current_progress = 1.0
    elif status == "running": current_progress = 0.5 # Generic "in progress"
    elif status == "awaiting_human_verification": current_progress = 0.4 # Example, can be more granular
    elif status == "queued": current_progress = 0.1
    elif status == "resuming_after_verification": current_progress = 0.45 # Between await and running

    topic = task.get('topic', 'N/A') # Default topic if not found
    error_message = task.get("error_message")

    if status == "completed":
        message = f"Research completed for topic: {topic}"
    elif status in ["failed", "error_in_workflow"]:
        message = error_message or f"Research failed for topic: {topic}. No specific error message."
    else:
        message = f"Current status for topic: {topic}"

    return ResearchStatus(
        task_id=task_id,
        status=status,
        message=message,
        progress=current_progress,
        timestamp=datetime.utcnow(), # Consider storing task creation/update timestamp in active_tasks
        verification_request=verification_req_data # This is now correctly populated
    )

@app.post("/submit-verification/{task_id}", status_code=200, summary="Submit Human Verification for a Task", tags=["Research"])
async def submit_human_verification_endpoint(task_id: str, approval_input: HumanApproval, background_tasks: BackgroundTasks):
    """
    Allows a human to submit their verification/correction for a piece of data
    that the workflow has flagged for human review.
    """
    task = active_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID '{task_id}' not found.")

    if task.get("status") != "awaiting_human_verification":
        raise HTTPException(
            status_code=400,
            detail=f"Task '{task_id}' is not currently awaiting human verification. Current status: {task.get('status')}."
        )

    current_graph_state = task.get("graph_state")
    if not current_graph_state or not isinstance(current_graph_state, dict):
        # Log this critical issue
        print(f"Error: Task {task_id} has missing or corrupted state for graph_state.")
        raise HTTPException(status_code=500, detail="Task state is missing or corrupted. Cannot process verification.")

    # Inject human feedback into the current_graph_state.
    # The 'human_feedback' key is what await_human_input_node in the workflow expects.
    current_graph_state['human_feedback'] = approval_input.dict() # approval_input is Pydantic, convert to dict

    # Update task properties to signal resumption
    task["graph_state"] = current_graph_state # Persist the modified state (now including human_feedback)
    task["status"] = "resuming_after_verification" # Custom status to indicate it's about to be re-queued

    # Re-trigger the workflow execution by adding run_research_workflow_async to background tasks.
    # It will use the updated current_graph_state (which now contains human_feedback).
    print(f"Task {task_id}: Queuing workflow for resumption after human verification. Topic: {current_graph_state.get('topic')}")
    background_tasks.add_task(run_research_workflow_async,
                              task_id,
                              current_graph_state.get('topic', "Unknown Topic"), # Get topic from state
                              current_graph_state) # Pass the entire modified state as initial_graph_input for resumption

    return {"message": f"Verification submitted for task '{task_id}'. Workflow is scheduled to resume."}


@app.get("/results/{task_id}", response_model=Optional[DocumentOutput], summary="Get Task Results", tags=["Research"])
async def get_task_results_endpoint(task_id: str):
    task = active_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID '{task_id}' not found.")

    status = task.get("status")
    if status == "completed":
        final_graph_state = task.get("final_graph_state", task.get("graph_state", {}))
        final_document_content = final_graph_state.get("final_document")
        if final_document_content is not None:
            return DocumentOutput(
                task_id=task_id,
                document_content=final_document_content,
                format="markdown"
            )
        else:
            return None
    elif status in ["failed", "error_in_workflow", "unknown_completion"]:
        raise HTTPException(status_code=422, detail=f"Task ended inconclusively. Status: {status}. Error: {task.get('error_message', 'No specific error message.')}")
    else:
        raise HTTPException(status_code=202, detail=f"Task '{task_id}' is not yet completed. Current status: {status}.")

# --- Main Execution Guard ---
if __name__ == "__main__":
    print("Starting Knowledge Nexus API server using Uvicorn...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
