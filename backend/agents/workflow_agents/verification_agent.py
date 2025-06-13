from typing import List, Dict, Any, Optional

# Assuming KnowledgeNexusState and DataVerificationRequest might be moved to a common types module.
# For now, provide basic structures for type hinting if not imported.
# This should ideally be imported from a shared types module.

from ..types import KnowledgeNexusState, DataVerificationRequest

class VerificationAgent:
    """
    Agent responsible for verifying research data.
    Currently, this is a pass-through but can be extended for complex verification.
    It also handles the logic for determining if human-in-the-loop (HITL) is needed.
    """
    def __init__(self): # Add chroma_service: Optional[ChromaService] = None if needed in future
        """
        Initializes the VerificationAgent.
        Future extensions might include services for cross-referencing or validation.
        """
        # self.chroma_service = chroma_service # Example if it needs to query DB
        print("VerificationAgent initialized.")

    def execute(self, state: KnowledgeNexusState) -> KnowledgeNexusState:
        """
        Executes the data verification process.

        Args:
            state: The current KnowledgeNexusState of the workflow.

        Returns:
            The updated KnowledgeNexusState.
        """
        print(f"--- VerificationAgent: Executing --- Task ID: {state.get('task_id')}, Current Stage: {state.get('current_stage')}")
        state['current_stage'] = "verifying"

        research_data = state.get('research_data', [])
        if not research_data:
            print("VerificationAgent: No research data to verify.")
            state['verified_data'] = []
            # Ensure error_message is initialized if it's None
            current_error_message = state.get('error_message', "")
            state['error_message'] = (current_error_message + " Verification skipped: No research data available.").strip()
            state['human_in_loop_needed'] = False
            state['current_verification_request'] = None
            return state

        # Current pass-through implementation:
        # All research_data is considered verified for now.
        state['verified_data'] = list(research_data) # Create a copy
        print(f"VerificationAgent: Data verification pass-through complete. {len(state['verified_data'])} items processed.")

        # --- Human-in-the-loop (HITL) Simulation Logic ---

        if not state.get('human_in_loop_needed'):
            state['human_in_loop_needed'] = False
            state['current_verification_request'] = None

        if state['human_in_loop_needed']:
            print(f"VerificationAgent: Human verification is flagged as needed for task {state.get('task_id')}.")
            if not state.get('current_verification_request'):
                print("VerificationAgent Warning: human_in_loop_needed is True, but no current_verification_request found. This may indicate an issue.")
        else:
            print("VerificationAgent: No human verification explicitly triggered in this step.")

        return state

if __name__ == '__main__':
    print("Testing VerificationAgent...")
    verification_agent = VerificationAgent()

    # Test case 1: Data available, no HITL needed by default
    print("\n--- Test Case 1: Data available, no HITL ---")
    state_with_data = KnowledgeNexusState({
        "task_id": "task_verify_1",
        "current_stage": "research_complete",
        "research_data": [{"id": "doc1", "content": "Some data"}],
        "verified_data": [],
        "human_in_loop_needed": False,
        "current_verification_request": None
    })
    updated_state_1 = verification_agent.execute(state_with_data)
    print(f"State after verification (no HITL): {updated_state_1}")
    assert len(updated_state_1.get('verified_data', [])) == 1
    assert updated_state_1.get('verified_data')[0]['content'] == "Some data"
    assert updated_state_1.get('human_in_loop_needed') is False
    assert updated_state_1.get('current_verification_request') is None

    # Test case 2: No research data
    print("\n--- Test Case 2: No research data ---")
    state_no_data = KnowledgeNexusState({
        "task_id": "task_verify_2",
        "current_stage": "research_complete",
        "research_data": [],
        "verified_data": [],
        "human_in_loop_needed": False,
        "current_verification_request": None
    })
    updated_state_2 = verification_agent.execute(state_no_data)
    print(f"State after verification (no data): {updated_state_2}")
    assert len(updated_state_2.get('verified_data', [])) == 0
    assert "Verification skipped" in updated_state_2.get('error_message', "")
    assert updated_state_2.get('human_in_loop_needed') is False

    # Test case 3: HITL explicitly needed (e.g., set by a previous step or rule)
    print("\n--- Test Case 3: HITL explicitly needed ---")
    sample_verification_request = DataVerificationRequest({
        "task_id": "task_verify_3",
        "data_id": "doc_to_verify_123",
        "data_to_verify": {"preview": "Content preview..."}
    })
    state_hitl_needed = KnowledgeNexusState({
        "task_id": "task_verify_3",
        "current_stage": "research_complete",
        "research_data": [{"id": "doc_to_verify_123", "content": "Content needing verification"}],
        "verified_data": [],
        "human_in_loop_needed": True,
        "current_verification_request": sample_verification_request
    })
    updated_state_3 = verification_agent.execute(state_hitl_needed)
    print(f"State after verification (HITL needed): {updated_state_3}")
    assert len(updated_state_3.get('verified_data', [])) == 1
    assert updated_state_3.get('human_in_loop_needed') is True
    assert updated_state_3.get('current_verification_request') is not None
    assert updated_state_3.get('current_verification_request')['data_id'] == "doc_to_verify_123"

    # Test case 4: HITL needed but no verification request (warning scenario)
    print("\n--- Test Case 4: HITL needed but no verification request ---")
    state_hitl_no_req = KnowledgeNexusState({
        "task_id": "task_verify_4",
        "current_stage": "research_complete",
        "research_data": [{"id": "doc_novreq_456", "content": "Content"}],
        "verified_data": [],
        "human_in_loop_needed": True,
        "current_verification_request": None
    })
    updated_state_4 = verification_agent.execute(state_hitl_no_req)
    print(f"State after verification (HITL, no request): {updated_state_4}")
    assert updated_state_4.get('human_in_loop_needed') is True
    assert updated_state_4.get('current_verification_request') is None

    print("\nVerificationAgent tests finished.")
