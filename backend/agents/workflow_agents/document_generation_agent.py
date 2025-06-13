from typing import List, Dict, Any, Optional

try:
    from ..llm_service import LLMService
    # from ..research_workflow import KnowledgeNexusState # Placeholder
except ImportError:
    print("DocumentGenerationAgent: Could not import LLMService. Using placeholder logic for LLM.")
    class LLMService: # type: ignore
        def is_initialized(self) -> bool: return False
        def invoke(self, prompt: str) -> tuple[None | str, None | str]:
            print(f"Dummy LLMService: Simulating LLM invoke for document formatting: {prompt[:50]}...")
            return f"Simulated formatted document based on prompt: {prompt[:50]}", None

# If KnowledgeNexusState is not imported, provide a basic structure for type hinting.
from ..types import KnowledgeNexusState

class DocumentGenerationAgent:
    """
    Agent responsible for generating the final document from synthesized content.
    It can optionally use an LLM for advanced formatting.
    """
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initializes the DocumentGenerationAgent.

        Args:
            llm_service: An optional instance of LLMService for advanced formatting.
        """
        self.llm_service = llm_service
        llm_status = "available" if self.llm_service and self.llm_service.is_initialized() else "not available or not initialized"
        print(f"DocumentGenerationAgent initialized (LLM Service {llm_status}).")

    def _format_basic_document(self, topic: Optional[str], synthesized_content: str, detected_conflicts: List[Dict[str, Any]]) -> str:
        """
        Creates a basic formatted document string without using an LLM.
        """
        conflict_section = ""
        if detected_conflicts:
            conflict_details = "\n".join([f"- {c.get('type', 'Conflict')}: {c.get('details', 'No details')}" for c in detected_conflicts])
            conflict_section = f"\n\n### Detected Conflicts:\n{len(detected_conflicts)} conflicts found:\n{conflict_details}"
        else:
            conflict_section = "\n\nNo conflicts were detected during this process."

        return f"## Final Report on: {topic or 'N/A'}\n\n{synthesized_content}{conflict_section}"

    def _format_document_with_llm(self, topic: Optional[str], synthesized_content: str, detected_conflicts: List[Dict[str, Any]]) -> tuple[str | None, str | None]:
        """
        Uses the LLM to format the document.
        Returns the formatted document and an optional error message.
        """
        if not self.llm_service or not self.llm_service.is_initialized():
            return None, "LLM service not available for advanced formatting."

        conflict_text = "No conflicts detected."
        if detected_conflicts:
            conflict_items = [f"- Type: {c.get('type', 'N/A')}, Details: {c.get('details', 'N/A')}" for c in detected_conflicts]
            conflict_text = f"The following conflicts or points of attention were noted:\n" + "\n".join(conflict_items)

        prompt = (
            f"You are a document formatting expert. Based on the following synthesized content and detected conflicts "
            f"for the topic '{topic or 'N/A'}', generate a well-structured final report. "
            f"Ensure the report is clear, professional, and presents the information logically. "
            f"Incorporate the synthesized content as the main body and append a section for detected conflicts if any.\n\n"
            f"Synthesized Content:\n{synthesized_content}\n\n"
            f"Detected Conflicts:\n{conflict_text}\n\n"
            f"Formatted Final Report:"
        )

        print(f"DocumentGenerationAgent: Invoking LLM for document formatting (prompt length: {len(prompt)} chars).")
        formatted_doc, error = self.llm_service.invoke(prompt)
        if error:
            return None, f"LLM formatting error: {error}"
        return formatted_doc, None

    def execute(self, state: KnowledgeNexusState) -> KnowledgeNexusState:
        """
        Executes the document generation process.

        Args:
            state: The current KnowledgeNexusState of the workflow.

        Returns:
            The updated KnowledgeNexusState.
        """
        print(f"--- DocumentGenerationAgent: Executing --- Task ID: {state.get('task_id')}, Current Stage: {state.get('current_stage')}")
        state['current_stage'] = "generating_document"
        state['error_message'] = None # Clear previous document generation errors

        topic = state.get('topic')
        synthesized_content = state.get('synthesized_content', "")
        detected_conflicts = state.get('detected_conflicts', [])

        is_placeholder_synthesis = (
            not synthesized_content or
            synthesized_content.startswith("No verified data") or
            "Simulated synthesis" in synthesized_content or
            synthesized_content.startswith("Error during content synthesis")
        )

        if is_placeholder_synthesis:
            warning_msg = "Synthesized content is empty, placeholder, or indicates a prior error. Basic document will reflect this."
            print(f"DocumentGenerationAgent Warning: {warning_msg}")
            state['final_document'] = self._format_basic_document(topic, "Content synthesis was skipped, incomplete, or failed.", detected_conflicts)
            # state['error_message'] = warning_msg # Decided against setting error for this, as it's more of a status.
            return state

        formatted_document = None
        llm_formatting_error = None

        if self.llm_service and self.llm_service.is_initialized():
            print("DocumentGenerationAgent: Attempting LLM-based document formatting.")
            formatted_document, llm_formatting_error = self._format_document_with_llm(topic, synthesized_content, detected_conflicts)
            if llm_formatting_error:
                print(f"DocumentGenerationAgent: LLM formatting failed: {llm_formatting_error}. Falling back to basic formatting.")
                state['error_message'] = llm_formatting_error
        else:
            print("DocumentGenerationAgent: LLM service not available or not initialized. Using basic formatting.")

        if formatted_document:
            state['final_document'] = formatted_document
            print("DocumentGenerationAgent: Document generated successfully using LLM.")
        else:
            state['final_document'] = self._format_basic_document(topic, synthesized_content, detected_conflicts)
            print("DocumentGenerationAgent: Document generated using basic formatting.")

        return state

if __name__ == '__main__':
    print("Testing DocumentGenerationAgent...")

    class MockLLMService(LLMService):
        def __init__(self, initialized: bool = True, simulate_error: bool = False):
            self._initialized = initialized
            self._simulate_error = simulate_error
            print(f"MockLLMService for DocGen initialized (Simulating initialized: {initialized}, error: {simulate_error})")

        def is_initialized(self) -> bool:
            return self._initialized

        def invoke(self, prompt: str) -> tuple[str | None, str | None]:
            if not self._initialized:
                return None, "LLM not initialized for DocGen"
            if self._simulate_error:
                return None, "Simulated LLM error during DocGen invoke"

            # Extract topic for more dynamic mock response
            topic_marker = "topic '"
            topic_end_marker = "'"
            start_idx = prompt.find(topic_marker)
            topic = "Unknown Topic"
            if start_idx != -1:
                topic_content_start = start_idx + len(topic_marker)
                end_idx = prompt.find(topic_end_marker, topic_content_start)
                if end_idx != -1:
                    topic = prompt[topic_content_start:end_idx]

            return f"LLM Formatted Document for topic '{topic}': Based on prompt starting with... {prompt[prompt.find('Synthesized Content:'):prompt.find('Synthesized Content:')+100]}...", None

    print("\n--- Test Case 1: Successful Generation with LLM ---")
    llm_success_docgen = MockLLMService(initialized=True, simulate_error=False)
    docgen_agent_llm = DocumentGenerationAgent(llm_service=llm_success_docgen)
    state_llm_success = KnowledgeNexusState({
        "task_id": "task_docgen_1", "topic": "Space Exploration", "current_stage": "conflict_detection_complete",
        "synthesized_content": "This is the synthesized summary about space exploration.",
        "detected_conflicts": [{"type": "data_gap", "details": "Launch dates for mission X vary."}],
        "final_document": ""
    })
    updated_state_1 = docgen_agent_llm.execute(state_llm_success)
    print(f"State after LLM DocGen: Error: {updated_state_1.get('error_message')}, Final Doc: '{updated_state_1.get('final_document', '')[:150]}...'")
    assert updated_state_1.get('error_message') is None
    assert "LLM Formatted Document for topic 'Space Exploration'" in updated_state_1.get('final_document', "")
    assert "Launch dates for mission X vary" in updated_state_1.get('final_document', "")

    print("\n--- Test Case 2: LLM Not Initialized ---")
    llm_not_init_docgen = MockLLMService(initialized=False)
    docgen_agent_no_llm = DocumentGenerationAgent(llm_service=llm_not_init_docgen)
    state_no_llm = KnowledgeNexusState({
        "task_id": "task_docgen_2", "topic": "Marine Biology", "current_stage": "conflict_detection_complete",
        "synthesized_content": "Summary of marine life.", "detected_conflicts": [], "final_document": ""
    })
    updated_state_2 = docgen_agent_no_llm.execute(state_no_llm)
    print(f"State after No LLM DocGen: Error: {updated_state_2.get('error_message')}, Final Doc: '{updated_state_2.get('final_document', '')[:100]}...'")
    assert updated_state_2.get('error_message') is None
    assert "## Final Report on: Marine Biology" in updated_state_2.get('final_document', "")
    assert "No conflicts were detected" in updated_state_2.get('final_document', "")

    print("\n--- Test Case 3: LLM Invocation Error ---")
    llm_error_docgen = MockLLMService(initialized=True, simulate_error=True)
    docgen_agent_llm_error = DocumentGenerationAgent(llm_service=llm_error_docgen)
    state_llm_error = KnowledgeNexusState({
        "task_id": "task_docgen_3", "topic": "Artificial Intelligence", "current_stage": "conflict_detection_complete",
        "synthesized_content": "The state of AI in 2024.", "detected_conflicts": [], "final_document": ""
    })
    updated_state_3 = docgen_agent_llm_error.execute(state_llm_error)
    print(f"State after LLM Error DocGen: Error: {updated_state_3.get('error_message')}, Final Doc: '{updated_state_3.get('final_document', '')[:100]}...'")
    assert "Simulated LLM error during DocGen invoke" in updated_state_3.get('error_message', "")
    assert "## Final Report on: Artificial Intelligence" in updated_state_3.get('final_document', "")

    print("\n--- Test Case 4: Placeholder Synthesized Content ---")
    docgen_agent_placeholder_content = DocumentGenerationAgent(llm_service=llm_success_docgen)
    state_placeholder_content = KnowledgeNexusState({
        "task_id": "task_docgen_4", "topic": "History of Computing", "current_stage": "conflict_detection_complete",
        "synthesized_content": "No verified data available to synthesize.",
        "detected_conflicts": [], "final_document": ""
    })
    updated_state_4 = docgen_agent_placeholder_content.execute(state_placeholder_content)
    print(f"State after Placeholder Content DocGen: Error: {updated_state_4.get('error_message')}, Final Doc: '{updated_state_4.get('final_document', '')[:120]}...'")
    assert "Content synthesis was skipped, incomplete, or failed." in updated_state_4.get('final_document', "")

    print("\n--- Test Case 5: No LLM Service Provided (llm_service=None) ---")
    docgen_agent_no_service = DocumentGenerationAgent(llm_service=None)
    state_no_service = KnowledgeNexusState({
        "task_id": "task_docgen_5", "topic": "Renewable Energy Sources", "current_stage": "conflict_detection_complete",
        "synthesized_content": "Solar and wind power are leading renewable energy sources.",
        "detected_conflicts": [], "final_document": ""
    })
    updated_state_5 = docgen_agent_no_service.execute(state_no_service)
    print(f"State after No LLM Service DocGen: Final Doc: '{updated_state_5.get('final_document', '')[:100]}...'")
    assert "## Final Report on: Renewable Energy Sources" in updated_state_5.get('final_document', "")
    assert "Solar and wind power" in updated_state_5.get('final_document', "")

    print("\nDocumentGenerationAgent tests finished.")
