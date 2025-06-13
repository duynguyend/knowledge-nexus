from typing import List, Dict, Any, Optional

# Assuming KnowledgeNexusState, HumanApproval, and DataVerificationRequest
# would ideally be imported from a shared types module.
# For now, defining basic structures for type hinting.

from ..types import KnowledgeNexusState, HumanApproval, DataVerificationRequest

class HumanInputAgent:
    """
    Agent responsible for managing the human-in-the-loop (HITL) process.
    It handles pausing the workflow for human input and processing the received feedback.
    """
    def __init__(self):
        """
        Initializes the HumanInputAgent.
        """
        print("HumanInputAgent initialized.")

    def execute(self, state: KnowledgeNexusState) -> KnowledgeNexusState:
        """
        Executes the logic for awaiting and processing human input.

        Args:
            state: The current KnowledgeNexusState of the workflow.

        Returns:
            The updated KnowledgeNexusState.
        """
        task_id = state.get('task_id', 'N/A')
        current_stage = state.get('current_stage', 'unknown')
        human_in_loop_needed = state.get('human_in_loop_needed', False)
        human_feedback_provided = state.get('human_feedback') is not None

        print(f"--- HumanInputAgent: Executing --- Task ID: {task_id}, Current Stage: {current_stage}, HITL Needed: {human_in_loop_needed}, Feedback Provided: {human_feedback_provided}")

        feedback: Optional[HumanApproval] = state.get('human_feedback')

        if feedback:
            state['current_stage'] = "processing_human_feedback"
            print(f"HumanInputAgent: Human feedback received for data ID: {feedback.get('data_id')}. Approved: {feedback.get('approved')}")

            item_updated = False
            data_id_to_update = feedback.get('data_id')

            verified_data_list: Optional[List[Dict[str, Any]]] = state.get('verified_data')
            if verified_data_list is not None:
                for i, item in enumerate(verified_data_list):
                    if item.get("id") == data_id_to_update:
                        if feedback.get('approved'):
                            item['status'] = 'verified_by_human'
                            item['verified_notes'] = feedback.get('notes')
                            if feedback.get('corrected_content'):
                                item['content'] = feedback['corrected_content']
                                item['snippet'] = feedback['corrected_content']
                                item['raw_content'] = feedback['corrected_content']
                                item['corrected_by_human'] = True
                            print(f"HumanInputAgent: Item '{data_id_to_update}' updated with human approval.")
                        else:
                            item['status'] = 'rejected_by_human'
                            item['rejection_notes'] = feedback.get('notes')
                            print(f"HumanInputAgent: Item '{data_id_to_update}' marked as rejected by human.")
                        item_updated = True
                        break

            if not item_updated:
                print(f"HumanInputAgent Warning: Could not find item with ID '{data_id_to_update}' in verified_data to apply human feedback.")

            state['human_in_loop_needed'] = False
            state['current_verification_request'] = None
            state['human_feedback'] = None

            print("HumanInputAgent: Human feedback processed. Workflow will now proceed.")

        elif human_in_loop_needed:
            state['current_stage'] = "awaiting_human_verification"
            pending_data_id = "unknown"
            current_req: Optional[DataVerificationRequest] = state.get('current_verification_request')
            if current_req:
                pending_data_id = current_req.get('data_id', 'unknown')

            print(f"HumanInputAgent: Task '{task_id}' is PAUSED (Stage: {state['current_stage']}). Waiting for human verification on data ID: '{pending_data_id}'.")

        else:
            state['current_stage'] = "human_input_not_required"
            print("HumanInputAgent: No human input currently required or provided. Proceeding.")
            state['human_in_loop_needed'] = False
            state['current_verification_request'] = None

        return state

if __name__ == '__main__':
    print("Testing HumanInputAgent...")
    human_input_agent = HumanInputAgent()

    print("\n--- Test Case 1: Human Input Provided - Approved ---")
    state_feedback_approved = KnowledgeNexusState({
        "task_id": "task_hitl_1", "current_stage": "awaiting_human_verification",
        "human_in_loop_needed": True,
        "current_verification_request": DataVerificationRequest({"task_id": "task_hitl_1", "data_id": "doc_abc", "data_to_verify": {}}),
        "human_feedback": HumanApproval({"task_id": "task_hitl_1", "data_id": "doc_abc", "approved": True, "notes": "Looks good.", "corrected_content": "Updated content."}),
        "verified_data": [{"id": "doc_abc", "content": "Old content"}, {"id": "doc_xyz", "content": "Other data"}]
    })
    updated_state_1 = human_input_agent.execute(state_feedback_approved)
    print(f"State after approved feedback: {updated_state_1}")
    assert updated_state_1.get('human_in_loop_needed') is False
    assert updated_state_1.get('current_verification_request') is None
    assert updated_state_1.get('human_feedback') is None
    assert updated_state_1.get('verified_data')[0]['content'] == "Updated content."
    assert updated_state_1.get('verified_data')[0]['status'] == 'verified_by_human'

    print("\n--- Test Case 2: Human Input Provided - Rejected ---")
    state_feedback_rejected = KnowledgeNexusState({
        "task_id": "task_hitl_2", "current_stage": "awaiting_human_verification",
        "human_in_loop_needed": True,
        "current_verification_request": DataVerificationRequest({"task_id": "task_hitl_2", "data_id": "doc_def", "data_to_verify": {}}),
        "human_feedback": HumanApproval({"task_id": "task_hitl_2", "data_id": "doc_def", "approved": False, "notes": "Incorrect data."}),
        "verified_data": [{"id": "doc_def", "content": "Content to be rejected"}]
    })
    updated_state_2 = human_input_agent.execute(state_feedback_rejected)
    print(f"State after rejected feedback: {updated_state_2}")
    assert updated_state_2.get('human_in_loop_needed') is False
    assert updated_state_2.get('verified_data')[0]['status'] == 'rejected_by_human'

    print("\n--- Test Case 3: HITL Needed, No Feedback (Pause) ---")
    state_pause = KnowledgeNexusState({
        "task_id": "task_hitl_3", "current_stage": "verifying_complete",
        "human_in_loop_needed": True,
        "current_verification_request": DataVerificationRequest({"task_id": "task_hitl_3", "data_id": "doc_ghi", "data_to_verify": {"preview": "Preview..."}}),
        "human_feedback": None,
        "verified_data": [{"id": "doc_ghi", "content": "Data awaiting verification"}]
    })
    updated_state_3 = human_input_agent.execute(state_pause)
    print(f"State after pause: {updated_state_3}")
    assert updated_state_3.get('current_stage') == "awaiting_human_verification"
    assert updated_state_3.get('human_in_loop_needed') is True
    assert updated_state_3.get('current_verification_request') is not None

    print("\n--- Test Case 4: No HITL, No Feedback (Pass Through) ---")
    state_pass_through = KnowledgeNexusState({
        "task_id": "task_hitl_4", "current_stage": "verifying_complete",
        "human_in_loop_needed": False,
        "current_verification_request": None, "human_feedback": None,
        "verified_data": [{"id": "doc_jkl", "content": "Data that doesn't need HITL"}]
    })
    updated_state_4 = human_input_agent.execute(state_pass_through)
    print(f"State after pass-through: {updated_state_4}")
    assert updated_state_4.get('current_stage') == "human_input_not_required"
    assert updated_state_4.get('human_in_loop_needed') is False

    print("\n--- Test Case 5: Feedback for non-existent data_id ---")
    state_feedback_non_existent_id = KnowledgeNexusState({
        "task_id": "task_hitl_5", "current_stage": "awaiting_human_verification",
        "human_in_loop_needed": True,
        "current_verification_request": DataVerificationRequest({"task_id": "task_hitl_5", "data_id": "doc_mno_original_request", "data_to_verify": {}}),
        "human_feedback": HumanApproval({"task_id": "task_hitl_5", "data_id": "doc_stq_wrong_id", "approved": True}),
        "verified_data": [{"id": "doc_mno_original_request", "content": "Some content"}]
    })
    updated_state_5 = human_input_agent.execute(state_feedback_non_existent_id)
    print(f"State after feedback for non-existent ID: {updated_state_5}")
    assert updated_state_5.get('human_in_loop_needed') is False
    assert updated_state_5.get('verified_data')[0].get('status') is None

    print("\nHumanInputAgent tests finished.")
