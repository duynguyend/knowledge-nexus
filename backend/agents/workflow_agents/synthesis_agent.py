from typing import List, Dict, Any, Optional

try:
    from ..llm_service import LLMService
    # from ..research_workflow import KnowledgeNexusState # Placeholder
except ImportError:
    print("SynthesisAgent: Could not import LLMService. Using placeholder logic.")
    class LLMService: # type: ignore
        def is_initialized(self) -> bool: return False
        def invoke(self, prompt: str) -> tuple[None | str, None | str]:
            print(f"Dummy LLMService: Simulating LLM invoke for prompt starting with: {prompt[:50]}...")
            return f"Simulated LLM synthesis for prompt: {prompt[:50]}", None

# If KnowledgeNexusState is not imported, provide a basic structure for type hinting.
from ..types import KnowledgeNexusState

class SynthesisAgent:
    """
    Agent responsible for synthesizing content from verified data using an LLM.
    """
    def __init__(self, llm_service: LLMService):
        """
        Initializes the SynthesisAgent.

        Args:
            llm_service: An instance of LLMService for interacting with language models.
        """
        self.llm_service = llm_service
        print(f"SynthesisAgent initialized (LLM Service available: {self.llm_service.is_initialized()}).")

    def _format_data_for_llm(self, verified_data: List[Dict[str, Any]], topic: Optional[str]) -> str:
        """
        Formats the verified data into a string prompt for the LLM.
        """
        context_parts = []
        for i, item in enumerate(verified_data):
            title = item.get('title', f"Source {i+1}")
            snippet = item.get('snippet', item.get('raw_content', item.get('content', 'No content available'))) # More fallbacks for content
            url = item.get('url', 'N/A')
            context_parts.append(f"Source {i+1} (Title: {title}, URL: {url}):\n{snippet}\n---")

        context_string = "\n\n".join(context_parts)

        prompt_text = (
            f"You are an expert research synthesizer. Your task is to create a concise, coherent summary "
            f"from the following verified data sources related to the topic: '{topic or 'Not specified'}'. "
            f"Focus on extracting key facts, insights, and figures. Avoid speculation or information not present in the sources. "
            f"If there are conflicting pieces of information, note them if significant, but prioritize common themes. "
            f"The output should be a well-structured summary.\n\n"
            f"Verified Data Sources:\n{context_string}\n\n"
            f"Comprehensive Summary:"
        )
        return prompt_text

    def execute(self, state: KnowledgeNexusState) -> KnowledgeNexusState:
        """
        Executes the content synthesis process.

        Args:
            state: The current KnowledgeNexusState of the workflow.

        Returns:
            The updated KnowledgeNexusState.
        """
        print(f"--- SynthesisAgent: Executing --- Task ID: {state.get('task_id')}, Current Stage: {state.get('current_stage')}")
        state['current_stage'] = "synthesizing"
        state['error_message'] = None  # Clear previous synthesis errors

        verified_data = state.get('verified_data', [])
        topic = state.get('topic')

        if not verified_data:
            print("SynthesisAgent: No verified data to synthesize.")
            state['synthesized_content'] = "No verified data available to synthesize."
            state['error_message'] = "Synthesis skipped: No verified data."
            return state

        print(f"SynthesisAgent: Synthesizing content from {len(verified_data)} verified items for topic '{topic}'.")

        if not self.llm_service.is_initialized():
            print("SynthesisAgent Warning: LLMService not available or not initialized. Using simulated synthesis.")
            content_summary = ", ".join([item.get('snippet', 'N/A')[:30] + "..." for item in verified_data])
            state['synthesized_content'] = f"Simulated synthesis for topic '{topic}': Based on {len(verified_data)} sources. Key points might include: {content_summary}"
            state['error_message'] = "LLM not initialized; used simulated synthesis."
            return state

        prompt = self._format_data_for_llm(verified_data, topic)

        print(f"SynthesisAgent: Invoking LLM for synthesis (prompt length: {len(prompt)} chars).")
        synthesized_text, llm_error = self.llm_service.invoke(prompt)

        if llm_error:
            print(f"SynthesisAgent Error: LLM invocation failed: {llm_error}")
            state['error_message'] = f"LLM synthesis failed: {llm_error}"
            content_summary = ", ".join([item.get('snippet', 'N/A')[:30] + "..." for item in verified_data])
            state['synthesized_content'] = f"Simulated synthesis (LLM error) for topic '{topic}'. Based on {len(verified_data)} sources."
        else:
            state['synthesized_content'] = synthesized_text
            print("SynthesisAgent: Content synthesized successfully using LLM.")

        return state

if __name__ == '__main__':
    print("Testing SynthesisAgent...")

    class MockLLMService(LLMService):
        def __init__(self, initialized: bool = True, simulate_error: bool = False):
            self._initialized = initialized
            self._simulate_error = simulate_error
            print(f"MockLLMService initialized (Simulating initialized: {initialized}, error: {simulate_error})")

        def is_initialized(self) -> bool:
            return self._initialized

        def invoke(self, prompt: str) -> tuple[str | None, str | None]:
            if not self._initialized:
                return None, "LLM not initialized"
            if self._simulate_error:
                return None, "Simulated LLM error during invoke"

            topic_search = "topic: '"
            topic_end_search = "'." # Corrected from original to match prompt format
            start_index = prompt.find(topic_search)
            end_index = prompt.find(topic_end_search, start_index + len(topic_search))
            topic_name = "unknown_topic"
            if start_index != -1 and end_index != -1:
                topic_name = prompt[start_index + len(topic_search) : end_index]

            # Handle case where topic might be 'Not specified'
            if topic_name == "Not specified": # from "topic: 'Not specified'."
                 # Try to find a snippet to make the mock more dynamic if topic is generic
                snippet_start_marker = "Source 1 (Title: Source 1, URL: N/A):\n"
                snippet_end_marker = "\n---"
                snippet_start_idx = prompt.find(snippet_start_marker)
                if snippet_start_idx != -1:
                    snippet_content_start = snippet_start_idx + len(snippet_start_marker)
                    snippet_content_end = prompt.find(snippet_end_marker, snippet_content_start)
                    if snippet_content_end != -1:
                        snippet_preview = prompt[snippet_content_start:snippet_content_end][:50]
                        return f"Mock synthesized content for 'Not specified' topic, based on data like '{snippet_preview}...'", None

            return f"Mock synthesized content for topic '{topic_name}' based on prompt: {prompt[:100]}...", None

    print("\n--- Test Case 1: Successful Synthesis ---")
    llm_success = MockLLMService(initialized=True, simulate_error=False)
    synthesis_agent_success = SynthesisAgent(llm_service=llm_success)
    state_success = KnowledgeNexusState({
        "task_id": "task_synth_1", "topic": "AI Ethics", "current_stage": "verifying_complete",
        "verified_data": [{"id": "doc1", "snippet": "Ethical AI is important."}], "synthesized_content": ""
    })
    updated_state_1 = synthesis_agent_success.execute(state_success)
    print(f"State after successful synthesis: Error: {updated_state_1.get('error_message')}, Content: '{updated_state_1.get('synthesized_content', '')[:100]}...'")
    assert updated_state_1.get('error_message') is None
    assert "Mock synthesized content for topic 'AI Ethics'" in updated_state_1.get('synthesized_content', "")

    print("\n--- Test Case 2: LLM Not Initialized ---")
    llm_not_init = MockLLMService(initialized=False)
    synthesis_agent_no_llm = SynthesisAgent(llm_service=llm_not_init)
    state_no_llm = KnowledgeNexusState({
        "task_id": "task_synth_2", "topic": "Quantum Physics", "current_stage": "verifying_complete",
        "verified_data": [{"id": "doc2", "snippet": "Quantum entanglement is fascinating."}], "synthesized_content": ""
    })
    updated_state_2 = synthesis_agent_no_llm.execute(state_no_llm)
    print(f"State after LLM not init: Error: {updated_state_2.get('error_message')}, Content: '{updated_state_2.get('synthesized_content', '')[:100]}...'")
    assert "LLM not initialized" in updated_state_2.get('error_message', "")
    assert "Simulated synthesis for topic 'Quantum Physics'" in updated_state_2.get('synthesized_content', "")

    print("\n--- Test Case 3: LLM Invocation Error ---")
    llm_invoke_error = MockLLMService(initialized=True, simulate_error=True)
    synthesis_agent_invoke_error = SynthesisAgent(llm_service=llm_invoke_error)
    state_invoke_error = KnowledgeNexusState({
        "task_id": "task_synth_3", "topic": "Renewable Energy", "current_stage": "verifying_complete",
        "verified_data": [{"id": "doc3", "snippet": "Solar power is a key renewable source."}], "synthesized_content": ""
    })
    updated_state_3 = synthesis_agent_invoke_error.execute(state_invoke_error)
    print(f"State after LLM invoke error: Error: {updated_state_3.get('error_message')}, Content: '{updated_state_3.get('synthesized_content', '')[:100]}...'")
    assert "Simulated LLM error during invoke" in updated_state_3.get('error_message', "")
    assert "Simulated synthesis (LLM error) for topic 'Renewable Energy'" in updated_state_3.get('synthesized_content', "")

    print("\n--- Test Case 4: No Verified Data ---")
    synthesis_agent_no_data = SynthesisAgent(llm_service=llm_success)
    state_no_data = KnowledgeNexusState({
        "task_id": "task_synth_4", "topic": "Ancient Civilizations", "current_stage": "verifying_complete",
        "verified_data": [], "synthesized_content": ""
    })
    updated_state_4 = synthesis_agent_no_data.execute(state_no_data)
    print(f"State after no data: Error: {updated_state_4.get('error_message')}, Content: '{updated_state_4.get('synthesized_content', '')[:100]}...'")
    assert "No verified data" in updated_state_4.get('error_message', "")
    assert "No verified data available to synthesize" in updated_state_4.get('synthesized_content', "")

    # Test case 5: Topic is None/Not specified
    print("\n--- Test Case 5: Topic Not Specified ---")
    state_no_topic = KnowledgeNexusState({
        "task_id": "task_synth_5", "topic": None, "current_stage": "verifying_complete",
        "verified_data": [{"id": "doc5", "snippet": "Data for an unspecified topic."}], "synthesized_content": ""
    })
    updated_state_5 = synthesis_agent_success.execute(state_no_topic)
    print(f"State after no topic: Error: {updated_state_5.get('error_message')}, Content: '{updated_state_5.get('synthesized_content', '')[:100]}...'")
    assert updated_state_5.get('error_message') is None
    assert "Mock synthesized content for 'Not specified' topic" in updated_state_5.get('synthesized_content', "")

    print("\nSynthesisAgent tests finished.")
