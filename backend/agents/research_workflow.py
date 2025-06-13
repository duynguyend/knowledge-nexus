import os
import uuid
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from langgraph.graph import StateGraph, END
from .types import KnowledgeNexusState, DataVerificationRequest, HumanApproval
from .llm_service import LLMService
from .search_service import SearchService
from .storage_service import StorageService
from .workflow_agents.research_agent import ResearchAgent
from .workflow_agents.verification_agent import VerificationAgent
from .workflow_agents.synthesis_agent import SynthesisAgent
from .workflow_agents.conflict_detection_agent import ConflictDetectionAgent
from .workflow_agents.document_generation_agent import DocumentGenerationAgent
from .workflow_agents.human_input_agent import HumanInputAgent
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def should_request_human_verification(state: KnowledgeNexusState) -> str:
    print(f"--- Conditional Edge: SHOULD_REQUEST_HUMAN_VERIFICATION --- Task ID: {state.get('task_id')}, Current Stage: {state.get('current_stage')}, Human in loop needed: {state.get('human_in_loop_needed')}, Verification request active: {state.get('current_verification_request') is not None}")
    print(f"\n--- Workflow: Conditional Edge ---") # Existing print
    if state.get('human_in_loop_needed') and state.get('current_verification_request'):
        print("Decision: Human verification IS needed.")
        return "human_verification_needed"
    else:
        print("Decision: No human verification needed, proceeding to synthesis.")
        return "synthesize_data"


# 4. Create build_knowledge_nexus_workflow function

def build_knowledge_nexus_workflow(chroma_persist_directory: Optional[str] = None):
    print("Building Knowledge Nexus workflow graph with new agents and services...")
    # Initialize Services
    llm_service = LLMService()
    search_service = SearchService()
    storage_service = StorageService(persist_directory=chroma_persist_directory)

    # Initialize Agents with services
    research_agent = ResearchAgent(search_service=search_service, storage_service=storage_service)
    verification_agent = VerificationAgent()
    synthesis_agent = SynthesisAgent(llm_service=llm_service)
    conflict_agent = ConflictDetectionAgent()
    doc_generation_agent = DocumentGenerationAgent(llm_service=llm_service)
    human_input_agent = HumanInputAgent()

    workflow = StateGraph(KnowledgeNexusState)

    # Add nodes - using agent.execute methods
    workflow.add_node("research", research_agent.execute)
    workflow.add_node("verify", verification_agent.execute)
    workflow.add_node("synthesize", synthesis_agent.execute)
    workflow.add_node("detect_conflicts", conflict_agent.execute)
    workflow.add_node("generate_document", doc_generation_agent.execute)
    workflow.add_node("await_human_input", human_input_agent.execute)

    workflow.set_entry_point("research")

    workflow.add_edge("research", "verify")
    workflow.add_conditional_edges(
        "verify",
        should_request_human_verification,
        {
            "human_verification_needed": "await_human_input",
            "synthesize_data": "synthesize"
        }
    )
    workflow.add_edge("synthesize", "detect_conflicts")
    workflow.add_edge("detect_conflicts", "generate_document")
    workflow.add_edge("generate_document", END)
    workflow.add_edge("await_human_input", "synthesize") # Reroute to synthesize after human input

    app = workflow.compile()
    print("Knowledge Nexus workflow graph compiled successfully with new agents.")
    return app, llm_service.is_initialized()

if __name__ == '__main__':
    print("Starting test run of Knowledge Nexus workflow (refactored)...")
    test_chroma_persist_dir = "./test_chroma_db_workflow_main_refactored"
    os.makedirs(test_chroma_persist_dir, exist_ok=True)

    workflow_app, llm_was_initialized = build_knowledge_nexus_workflow(chroma_persist_directory=test_chroma_persist_dir)
    print(f"LLM Initialized Status from build function: {llm_was_initialized}")

    example_topic = "The future of decentralized finance (DeFi)"
    initial_state_input = KnowledgeNexusState(
        topic=example_topic,
        task_id=f"task_{str(uuid.uuid4()).replace('-','_')}",
        current_stage="queued",
        research_data=[],
        verified_data=[],
        synthesized_content="",
        detected_conflicts=[],
        final_document="",
        human_in_loop_needed=False,
        current_verification_request=None,
        messages=[],
        error_message=None,
        human_feedback=None,
        sources_explored=0,
        data_collected=0
    )

    print(f"
Invoking refactored workflow for task ID: {initial_state_input['task_id']} with topic: {initial_state_input['topic']}")

    print("--- First run: Potentially pausing for human input ---")
    for event in workflow_app.stream(initial_state_input):
        for node_name, output_state in event.items():
            print(f"
Output from node: {node_name}")
            print(f"  Current Stage: {output_state.get('current_stage')}")
            if output_state.get('error_message'):
                print(f"  Error: {output_state['error_message']}")

            if output_state.get('current_stage') == "awaiting_human_verification":
                print("--- WORKFLOW PAUSED FOR HUMAN INPUT ---")
                pending_request = output_state.get('current_verification_request')
                if pending_request:
                    print(f"  Verification requested for data ID: {pending_request.get('data_id')}")
                    feedback_input = HumanApproval(
                        task_id=pending_request.get('task_id'),
                        data_id=pending_request.get('data_id'),
                        approved=True,
                        notes="Human approved this item after review.",
                        corrected_content="This is the human-corrected content for the item."
                    )
                    print("  Simulating human feedback being provided...")
                    initial_state_input = output_state.copy() # type: ignore
                    initial_state_input['human_feedback'] = feedback_input
                    print("  State updated with human feedback. Workflow would be reinvoked in a real app.")
                    # For this test, we break to simulate the pause and external update.
                    break
                else:
                    print("  Warning: Awaiting human input, but no verification request found in state.")
            if node_name == END:
                print(f"
--- Workflow Execution Finished (Refactored) for Task ID: {initial_state_input['task_id']} ---")
                final_doc = output_state.get('final_document', '')
                print(f"  Final Document Preview: {str(final_doc)[:200]}...")
                break
        if output_state.get('current_stage') == "awaiting_human_verification" or node_name == END: # type: ignore
            break

    print("
Refactored test run finished.")
    print("REMINDER: Ensure API keys (GOOGLE, AZURE_OPENAI, OPENAI) are correctly set in backend/.env for full functionality.")
    print("Note: The __main__ block simulates only the first part of a potential human-in-the-loop interaction.")
    print("A full HITL cycle requires a mechanism to pause, receive external input, and reinvoke the workflow.")
