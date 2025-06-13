import uuid
from typing import List, Dict, Any, Optional

try:
    from ..search_service import SearchService
    from ..storage_service import StorageService
    # Assuming KnowledgeNexusState and other shared types might be moved to a common module later
    # For now, if they are defined in research_workflow.py, this import won't work directly
    # We might need to pass them or redefine simplified versions for agent's internal use if decoupled.
    # from ..research_workflow import KnowledgeNexusState # This will cause circular dependency if not handled
except ImportError:
    # Fallback for direct execution or testing if services are not found via relative imports
    # This is simplified; real testing would require mocks or stubs.
    print("ResearchAgent: Could not import SearchService or StorageService. Using placeholder logic.")
    class SearchService: # type: ignore
        def search(self, topic: str, num_results: int = 10) -> tuple[list, None]:
            print(f"Dummy SearchService: Searching for '{topic}' (num_results: {num_results})")
            return [], None
    class StorageService: # type: ignore
        def __init__(self, persist_directory: Optional[str] = None): # Added persist_directory to match real class
            print(f"Dummy StorageService initialized (persist_directory: {persist_directory}).")

        def is_initialized(self) -> bool: # Added is_initialized to match real class
            print("Dummy StorageService: is_initialized called.")
            return True

        def add_research_data(self, task_id: str, research_items: list, topic: str) -> tuple[bool, None]:
            print(f"Dummy StorageService: Adding {len(research_items)} items for task '{task_id}' on topic '{topic}'")
            return True, None

# If KnowledgeNexusState is not imported, provide a basic structure for type hinting.
# This should ideally be imported from a shared types module.
from ..types import KnowledgeNexusState

class ResearchAgent:
    """
    Agent responsible for conducting research using a SearchService and
    storing the results via a StorageService.
    """
    def __init__(self, search_service: SearchService, storage_service: StorageService):
        """
        Initializes the ResearchAgent.

        Args:
            search_service: An instance of SearchService for performing searches.
            storage_service: An instance of StorageService for storing data.
        """
        self.search_service = search_service
        self.storage_service = storage_service

    def execute(self, state: KnowledgeNexusState) -> KnowledgeNexusState:
        """
        Executes the research process based on the current state.

        Args:
            state: The current KnowledgeNexusState of the workflow.

        Returns:
            The updated KnowledgeNexusState.
        """
        print(f"--- ResearchAgent: Executing --- Task ID: {state.get('task_id')}, Current Stage: {state.get('current_stage')}")
        state['current_stage'] = "researching"

        topic = state.get('topic')
        task_id = state.get('task_id')

        if not topic or not task_id:
            print("ResearchAgent Error: Topic or Task ID is missing in state.")
            state['error_message'] = "Topic or Task ID is missing, cannot conduct research."
            state['research_data'] = state.get('research_data', [])
            state['sources_explored'] = state.get('sources_explored', 0)
            state['data_collected'] = len(state.get('research_data', []))
            return state

        print(f"ResearchAgent: Initiating research for topic: '{topic}' (Task ID: {task_id})")
        state['error_message'] = None  # Clear previous errors

        # Perform search
        num_search_results = state.get('num_search_results', 10)
        search_results, search_error = self.search_service.search(topic, num_results=num_search_results)

        current_search_sources = len(search_results) if search_results else 0
        sources_explored_count = state.get('sources_explored', 0) + current_search_sources

        if search_error:
            print(f"ResearchAgent: Error during search: {search_error}")
            state['error_message'] = f"{state.get('error_message', '')} Search failed: {search_error}".strip()
            state['research_data'] = state.get('research_data', [])

        if state.get('research_data') is None:
            state['research_data'] = []

        valid_search_results = [item for item in search_results if item] if search_results else []
        state['research_data'].extend(valid_search_results)

        state['sources_explored'] = sources_explored_count
        state['data_collected'] = len(state['research_data'])

        print(f"ResearchAgent: Found {current_search_sources} new items. Total research data: {state['data_collected']} items. Total sources explored: {state['sources_explored']}.")

        if valid_search_results and self.storage_service.is_initialized():
            print(f"ResearchAgent: Storing {len(valid_search_results)} new items in DB for task '{task_id}'.")
            added_to_db, db_error = self.storage_service.add_research_data(
                task_id=task_id,
                research_items=valid_search_results,
                topic=topic
            )
            if db_error:
                print(f"ResearchAgent: Error storing data in DB: {db_error}")
                current_error = state.get('error_message', "")
                state['error_message'] = f"{current_error} DB storage failed: {db_error}".strip()
            elif added_to_db:
                print(f"ResearchAgent: Successfully stored {len(valid_search_results)} items in DB.")
        elif not self.storage_service.is_initialized():
            print("ResearchAgent Warning: StorageService not available or not initialized. Skipping document storage.")
            current_error = state.get('error_message', "")
            state['error_message'] = f"{current_error} StorageService not available; data not saved to DB.".strip()

        state['human_in_loop_needed'] = state.get('human_in_loop_needed', False)
        return state

if __name__ == '__main__':
    print("Testing ResearchAgent...")

    class MockSearchService(SearchService):
        def search(self, topic: str, num_results: int = 10) -> tuple[list[dict[str, str | Any]], Optional[str]]:
            print(f"MockSearchService: Simulating search for '{topic}'.")
            if topic == "error_topic":
                return [], "Simulated search error"
            return [
                {"id": str(uuid.uuid4()), "url": f"http://example.com/{topic.replace(' ','_')}_1", "title": f"Result 1 for {topic}", "snippet": f"Snippet for {topic} 1", "raw_content": f"Raw content for {topic} 1", "source_name": "Mock Search"},
                {"id": str(uuid.uuid4()), "url": f"http://example.com/{topic.replace(' ','_')}_2", "title": f"Result 2 for {topic}", "snippet": f"Snippet for {topic} 2", "raw_content": f"Raw content for {topic} 2", "source_name": "Mock Search"}
            ], None

    class MockStorageService(StorageService):
        def __init__(self, persist_directory: Optional[str] = None):
            self.db: Dict[str, List[Any]] = {}
            print("MockStorageService initialized.")

        def is_initialized(self) -> bool:
            return True

        def add_research_data(self, task_id: str, research_items: list, topic: str) -> tuple[bool, Optional[str]]:
            print(f"MockStorageService: Adding {len(research_items)} items for task '{task_id}'.")
            if task_id not in self.db:
                self.db[task_id] = []
            self.db[task_id].extend(research_items)
            if topic == "db_error_topic":
                return False, "Simulated DB error"
            return True, None

    mock_search_service = MockSearchService()
    mock_storage_service = MockStorageService()

    research_agent = ResearchAgent(search_service=mock_search_service, storage_service=mock_storage_service)

    print("\n--- Test Case 1: Successful Research ---")
    initial_state_success = KnowledgeNexusState({
        "topic": "AI in education", "task_id": f"task_{uuid.uuid4()}",
        "research_data": [], "sources_explored": 0, "data_collected": 0, "current_stage": "initial"
    })
    updated_state_success = research_agent.execute(initial_state_success)
    print(f"Updated state after success: Error: {updated_state_success.get('error_message')}, Items: {updated_state_success.get('data_collected')}")
    assert updated_state_success.get('error_message') is None
    assert updated_state_success.get('data_collected') == 2
    assert mock_storage_service.db[updated_state_success['task_id']]

    print("\n--- Test Case 2: Search Error ---")
    initial_state_search_error = KnowledgeNexusState({
        "topic": "error_topic", "task_id": f"task_{uuid.uuid4()}",
        "research_data": [], "sources_explored": 0, "data_collected": 0, "current_stage": "initial"
    })
    updated_state_search_error = research_agent.execute(initial_state_search_error)
    print(f"Updated state after search error: Error: {updated_state_search_error.get('error_message')}, Items: {updated_state_search_error.get('data_collected')}")
    assert "Simulated search error" in updated_state_search_error.get('error_message', "")
    assert updated_state_search_error.get('data_collected') == 0

    print("\n--- Test Case 3: DB Error ---")
    initial_state_db_error = KnowledgeNexusState({
        "topic": "db_error_topic", "task_id": f"task_{uuid.uuid4()}",
        "research_data": [], "sources_explored": 0, "data_collected": 0, "current_stage": "initial"
    })
    updated_state_db_error = research_agent.execute(initial_state_db_error)
    print(f"Updated state after DB error: Error: {updated_state_db_error.get('error_message')}, Items: {updated_state_db_error.get('data_collected')}")
    assert "Simulated DB error" in updated_state_db_error.get('error_message', "")
    assert updated_state_db_error.get('data_collected') == 2

    print("\n--- Test Case 4: Missing Topic ---")
    initial_state_no_topic = KnowledgeNexusState({
        "topic": None, "task_id": f"task_{uuid.uuid4()}", "current_stage": "initial"
    })
    updated_state_no_topic = research_agent.execute(initial_state_no_topic)
    print(f"Updated state after missing topic: Error: {updated_state_no_topic.get('error_message')}")
    assert "Topic or Task ID is missing" in updated_state_no_topic.get('error_message', "")

    print("\nResearchAgent tests finished.")
