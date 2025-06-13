import os
import uuid
from typing import List, Dict, Any, Tuple, Optional

from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

class SearchService:
    """
    Service for conducting internet research using Google Custom Search API.
    Provides simulated results if API keys are not configured.
    """
    def __init__(self):
        """Initializes the SearchService and checks for API key configuration."""
        self.service = None
        self.simulated_search = False

        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY" or \
           not GOOGLE_CSE_ID or GOOGLE_CSE_ID == "YOUR_GOOGLE_CSE_ID":
            print("SearchService Warning: GOOGLE_API_KEY or GOOGLE_CSE_ID is not set or is a placeholder.")
            print("SearchService: Using simulated Google Search data.")
            self.simulated_search = True
        else:
            try:
                self.service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
                print("SearchService: Google Custom Search service initialized successfully.")
            except Exception as e:
                print(f"SearchService Error: Failed to initialize Google Custom Search service: {e}")
                print("SearchService: Falling back to simulated Google Search data.")
                self.simulated_search = True

    def search(self, topic: str, num_results: int = 10) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Performs a search for the given topic.

        Args:
            topic (str): The topic to search for.
            num_results (int): The desired number of search results (max 10 for free API, up to 20).

        Returns:
            Tuple[List[Dict[str, Any]], Optional[str]]: A list of processed search results
                                                       and an optional error message string.
        """
        if not topic:
            return [], "Search topic cannot be empty."

        processed_results: List[Dict[str, Any]] = []
        error_message: Optional[str] = None

        if self.simulated_search:
            print(f"SearchService: Performing simulated search for topic: {topic}")
            processed_results = [
                {"id": f"sim_gs_{uuid.uuid4()}", "url": f"http://example.com/simulated_gs_source1_for_{topic.replace(' ','_')}", "title": f"Simulated Google: Overview of {topic}", "snippet": f"This is simulated Google Search content about {topic} because API keys are missing.", "raw_content": f"Simulated raw content for {topic} from Google Search.", "score": 0.8, "source_name": "Google Search Simulator"},
                {"id": f"sim_gs_{uuid.uuid4()}", "url": f"http://example.com/simulated_gs_source2_for_{topic.replace(' ','_')}", "title": f"Simulated Google: Details on {topic}", "snippet": f"Further simulated Google Search details regarding {topic}.", "raw_content": f"Further simulated raw content for {topic} from Google Search.", "score": 0.75, "source_name": "Google Search Simulator"}
            ]
            if num_results == 1: # for specific test cases
                 processed_results = [processed_results[0]]
            elif num_results > 2: # adjust if more simulated data is needed
                 processed_results = processed_results * (num_results // 2) + processed_results[:num_results % 2]

        elif self.service:
            try:
                print(f"SearchService: Attempting Google Custom Search for query: '{topic}', num_results: {num_results}")
                # Ensure num_results is within API limits (typically 1-10 per request, CSE can be configured for more)
                # The API's 'num' parameter can go up to 10 for the free version.
                # If you need more, you might need to make multiple requests or ensure your CSE is configured for more.
                # For this implementation, we'll cap it at 20 as per original code, but be mindful of API limits.
                actual_num_to_fetch = min(num_results, 10) # Adhering to typical free tier limit per call

                result = self.service.cse().list(q=topic, cx=GOOGLE_CSE_ID, num=actual_num_to_fetch).execute()

                google_search_items = result.get("items", [])
                print(f"SearchService: Google Search returned {len(google_search_items)} items.")

                for item in google_search_items:
                    item_id = str(uuid.uuid4())
                    processed_results.append({
                        "id": item_id,
                        "url": item.get("link"),
                        "title": item.get("title"),
                        "snippet": item.get("snippet"),
                        "raw_content": item.get("snippet"), # Using snippet as raw_content for consistency
                        "score": 0.8, # Placeholder score
                        "source_name": "Google Search"
                    })
            except Exception as e:
                error_message = f"Error during Google Custom Search for topic '{topic}': {e}"
                print(f"SearchService: {error_message}")
                # Optionally, fall back to simulated search here as well if a runtime API error occurs
                # For now, just returns empty list and error
        else:
            error_message = "Search service not initialized and not in simulated mode. This state should not be reached."
            print(f"SearchService: {error_message}")


        return processed_results, error_message

# Example usage (for testing this module directly)
if __name__ == '__main__':
    print("Testing SearchService...")
    search_service = SearchService()

    test_topic = "Quantum Computing applications"
    results, error = search_service.search(test_topic, num_results=3)

    if error:
        print(f"Search Test Error: {error}")

    if results:
        print(f"Search Test Results for '{test_topic}':")
        for i, res in enumerate(results):
            print(f"  Result {i+1}:")
            print(f"    ID: {res['id']}")
            print(f"    Title: {res['title']}")
            print(f"    URL: {res['url']}")
            print(f"    Snippet: {res['snippet'][:60]}...")
            print(f"    Source: {res['source_name']}")
    else:
        print(f"No results returned for '{test_topic}'.")

    print("\nNote: If API keys (GOOGLE_API_KEY, GOOGLE_CSE_ID) are not in .env or are placeholders, results will be simulated.")
