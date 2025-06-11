import uuid
import os
import functools # Added for partial
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Optional, Any
from langchain_core.messages import BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel # Added for type hinting
from langgraph.graph import StateGraph, END
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI, AzureChatOpenAI # Added for LLM

# Attempt to import from sibling directories for services and models
try:
    from ..services.chroma_service import ChromaService
    from ..models.schemas import DataVerificationRequest, HumanApproval
except ImportError:
    print("Could not perform relative imports for ChromaService, DataVerificationRequest, or HumanApproval. Using dummy classes for now.")
    class ChromaService: # type: ignore
        def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
            print(f"Dummy ChromaService: Add {len(documents)} documents to {collection_name}.")
            return True
    class DataVerificationRequest(TypedDict): task_id: str; data_id: str; data_to_verify: Dict # type: ignore
    class HumanApproval(TypedDict): task_id: str; data_id: str; approved: bool; notes: Optional[str]; corrected_content: Optional[str] # type: ignore

# Load environment variables from .env file
# This should ideally be called once when the application starts,
# but for modularity, calling it here ensures TAVILY_API_KEY is loaded for this module.
# Ensure backend/.env file exists with TAVILY_API_KEY="YOUR_KEY"
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env')) # Assuming .env is in backend directory

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    print("Warning: TAVILY_API_KEY not found in environment variables. Research node will fail if Tavily is used.")
    # You could raise an error here or allow the app to run with research functionality disabled.
    # raise ValueError("TAVILY_API_KEY not found. Please set it in your .env file or environment.")

# Load OpenAI and Azure OpenAI environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION") # This is often a fixed string like "2023-07-01-preview"
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") # Name of your deployment in Azure AI Studio
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Keep this for fallback or other uses if necessary


# 1. Define KnowledgeNexusState
class KnowledgeNexusState(TypedDict): # type: ignore
    topic: str
    task_id: str  # Unique ID for the entire research task
    research_data: List[Dict[str, Any]]  # Raw data from internet research
    verified_data: List[Dict[str, Any]]  # Verified data
    synthesized_content: str
    detected_conflicts: List[Dict[str, Any]]  # List of conflict details
    final_document: str
    human_in_loop_needed: bool
    current_verification_request: Optional[DataVerificationRequest]
    messages: List[BaseMessage]  # For conversation history with LLMs
    error_message: Optional[str]
    human_feedback: Optional[HumanApproval] = None # Added for HITL


# 2. Implement Agent Nodes
# Updated research_node to include chroma_service and use it
def research_node(state: KnowledgeNexusState, chroma_service: ChromaService) -> KnowledgeNexusState:
    print(f"\n--- Agent: Researcher ---")
    topic = state.get('topic')
    task_id = state.get('task_id') # Get task_id for ChromaDB collection name

    if not topic or not task_id:
        print("Error: Topic or Task ID is missing in state for research_node.")
        state['error_message'] = "Topic or Task ID is missing, cannot conduct research."
        state['research_data'] = []
        return state

    print(f"Initiating internet research for topic: {topic} (Task ID: {task_id})")
    state['error_message'] = None # Clear previous errors

    if not TAVILY_API_KEY or TAVILY_API_KEY == "YOUR_ACTUAL_TAVILY_API_KEY_REPLACE_ME":
        print("Warning: TAVILY_API_KEY is not set or is a placeholder. Skipping actual internet search.")
        print("Please set your TAVILY_API_KEY in the backend/.env file.")
        simulated_data = [
            {"id": f"sim_{uuid.uuid4()}", "url": "http://example.com/simulated_source1", "title": f"Simulated: Overview of {topic}", "content": f"This is simulated content about {topic} because Tavily API key is missing.", "score": 0.85, "source_name": "Simulator", "snippet": f"Simulated snippet for {topic} 1."},
            {"id": f"sim_{uuid.uuid4()}", "url": "http://example.com/simulated_source2", "title": f"Simulated: Details on {topic}", "content": f"Further simulated details regarding {topic} for demonstration purposes.", "score": 0.80, "source_name": "Simulator", "snippet": f"Simulated snippet for {topic} 2."}
        ]
        # Ensure 'research_data' is initialized if it's None
        if state.get('research_data') is None:
            state['research_data'] = []
        state['research_data'].extend(simulated_data)
        print(f"Research (simulated) completed. Found {len(simulated_data)} pieces of information.")
        # Add simulated data to ChromaDB as well, if chroma_service is available
        if chroma_service:
            documents = [item['snippet'] for item in simulated_data if item.get('snippet')]
            metadatas = [
                {"source_url": item.get('url', ''), "title": item.get('title', ''), "research_topic": topic, "original_id_from_source": item.get('id')}
                for item in simulated_data if item.get('snippet')
            ]
            ids = [item['id'] for item in simulated_data if item.get('snippet')]
            if documents and metadatas and ids:
                try:
                    chroma_service.add_documents(collection_name=task_id, documents=documents, metadatas=metadatas, ids=ids)
                    print(f"Researcher: Added {len(documents)} SIMULATED documents to ChromaDB for task '{task_id}'.")
                except Exception as chroma_e:
                    print(f"Error interacting with ChromaDB for simulated data: {chroma_e}")
                    state['error_message'] = f"Failed to store simulated research data in ChromaDB: {str(chroma_e)}"
        state['human_in_loop_needed'] = False
        return state

    try:
        # Using TavilySearchResults LangChain tool wrapper
        # You can customize max_results, include_domains, exclude_domains etc.
        # tavily_search = TavilySearchResults(api_key=TAVILY_API_KEY, max_results=5, search_depth="advanced")
        # results = tavily_search.invoke(topic) # Input is just the topic string for this wrapper

        # Using Tavily Python client directly for more control (as per Tavily docs)
        # from tavily import TavilyClient
        # tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        # results = tavily_client.search(query=topic, search_depth="advanced", max_results=7)
        # raw_search_results = results.get("results", [])


        # Using TavilySearchResults Tool (consistent with LangChain ecosystem)
        # The tool's invoke method expects a dictionary with a "query" key.
        tool = TavilySearchResults(max_results=5, api_key=TAVILY_API_KEY)
        print(f"Invoking Tavily search for query: '{topic}'")
        # The direct output of tool.invoke is a list of strings by default (concatenated snippets).
        # To get structured results (list of dicts), you might need to use it within an agent
        # or access a different method/property if available, or parse the string output.
        # Let's assume the standard LangChain tool behavior where it might return string snippets.
        # For more structured output, TavilyClient.search is often better.
        # However, the prompt implies using the LangChain wrapper.
        # The TavilySearchResults.invoke method, when called directly with a string,
        # returns a string of concatenated results.
        # If it's used as part of a LangChain agent or sequence, the output format might differ.
        # Let's try to get structured output if possible or adapt.
        # A common pattern for tools is tool.run(query) or tool._run(query) for direct execution.

        # The Tavily documentation suggests `client.search(query=...)` for structured results.
        # Let's use the `TavilySearchResults` but aim for its underlying client logic if simple invoke isn't structured.
        # `TavilySearchResults` has a `_results_converter` which implies it can get structured data.
        # The default behavior of `invoke` on `TavilySearchResults` might be a string.
        # Let's use a method that's more likely to give us list of dicts.
        # The `_raw_search` method on the Tavily client (which TavilySearchResults wraps) is what we want.
        # TavilySearchResults(api_key=...)._raw_search(query=topic) is not public API.

        # Let's try with the assumption that results = tool.invoke({"query": topic}) gives structured data
        # or that we adapt. The Tavily documentation for LangChain tools suggests it can return structured data.
        # Okay, the `TavilySearchResults` tool, when its `search_kwargs` (like `search_depth`) are set,
        # and when called via an agent or directly, should provide a list of document-like objects or dicts.
        # If `tool.invoke(topic)` returns a string, we'll need to adjust.
        # A quick check of TavilySearchResults source: it returns a list of dicts if used correctly.
        # The input to invoke should be a dict: `{"query": "your query"}`

        raw_results = tool.invoke({"query": topic}) # This should return List[Dict]

        processed_results = []
        if isinstance(raw_results, list): # Expecting a list of dictionaries
            for res in raw_results:
                # Adapt this based on actual keys in `res` from TavilySearchResults
                # Common keys: 'url', 'content', 'title', 'score', 'raw_content'
                item_id = str(uuid.uuid4())
                processed_results.append({
                    "id": item_id,
                    "url": res.get("url"),
                    "title": res.get("title", topic), # Use topic as fallback title
                    "snippet": res.get("content"), # 'content' usually holds the snippet
                    "raw_content": res.get("raw_content", res.get("content")), # Store more if available
                    "score": res.get("score", 0.0), # Relevance score if provided
                    "source_name": "Tavily Search"
                })
        elif isinstance(raw_results, str): # Fallback if it returns a single string
             print("Warning: Tavily search returned a single string, expected structured data. Processing as single item.")
             processed_results.append({
                 "id": str(uuid.uuid4()),
                 "url": None, "title": topic, "snippet": raw_results,
                 "raw_content": raw_results, "score": 0.0, "source_name": "Tavily Search (string output)"
             })

        state['research_data'] = (state.get('research_data') or []) + processed_results
        print(f"Researcher: Found {len(processed_results)} results for topic '{topic}'.")

        # Store results in ChromaDB
        if processed_results and chroma_service:
            documents = [item['snippet'] for item in processed_results if item.get('snippet')]
            metadatas = [
                {
                    "source_url": item.get('url', ''),
                    "title": item.get('title', ''),
                    "research_topic": topic,
                    "original_id_from_source": item.get('id')
                }
                for item in processed_results if item.get('snippet')
            ]
            ids = [item['id'] for item in processed_results if item.get('snippet')]

            if documents and metadatas and ids:
                collection_name = task_id
                print(f"Attempting to add {len(documents)} documents to ChromaDB collection: {collection_name}")
                try:
                    added_successfully = chroma_service.add_documents(
                        collection_name=collection_name,
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    if added_successfully:
                        print(f"Researcher: Added {len(documents)} documents to ChromaDB for task '{task_id}'.")
                    else:
                        print(f"Researcher: Failed to add documents to ChromaDB for task '{task_id}'.")
                except Exception as chroma_e:
                    print(f"Error interacting with ChromaDB: {chroma_e}")
                    state['error_message'] = f"Failed to store research data in ChromaDB: {str(chroma_e)}"
            else:
                print("No valid documents, metadatas, or IDs to add to ChromaDB.")
        elif not chroma_service:
             print("Warning: ChromaService not available. Skipping document storage.")

    except Exception as e:
        print(f"Error during Tavily search for topic '{topic}': {e}")
        state['error_message'] = f"Failed to conduct research using Tavily: {str(e)}"
        state['research_data'] = state.get('research_data', [])

    state['human_in_loop_needed'] = False
    return state

# Updated verify_node to include chroma_service in signature
def verify_node(state: KnowledgeNexusState, chroma_service: ChromaService) -> KnowledgeNexusState:
    print(f"\n--- Agent: Verifier ---")
    if chroma_service:
        print("Verifier: ChromaService available.")
    else:
        print("Verifier: ChromaService NOT available.")
    print("Verifying data...")
    if not state.get('research_data'):
        print("No research data to verify.")
        state['verified_data'] = []
        state['error_message'] = "Verification skipped: No research data available."
        return state

    # Simple pass-through for now
    state['verified_data'] = list(state['research_data']) # Make a copy
    print(f"Data verification pass-through complete. {len(state['verified_data'])} items processed.")

    # Simulate needing human input for a piece of data
    if state['verified_data']: # If there's data, pretend one item needs verification
        item_to_verify = state['verified_data'][0]
        # Ensure data_to_verify has the expected structure for DataVerificationRequest's DataSource
        # For this placeholder, we'll simplify. In reality, DataSource would be created from item_to_verify
        dummy_data_source_for_request = {
            "id": item_to_verify.get("source_id", "unknown_id"),
            "url": item_to_verify.get("url"),
            "content_preview": item_to_verify.get("content", "")[:100] # Preview
        }

        # Check if DataVerificationRequest is the real one or the dummy
        if "task_id" in DataVerificationRequest.__annotations__: # Check if it's the Pydantic model
             verification_request = DataVerificationRequest(
                task_id=state['task_id'],
                data_id=item_to_verify.get("source_id", "unknown_id"),
                data_to_verify=dummy_data_source_for_request, # This should match DataSource schema
                conflicting_sources=[]
            )
        else: # It's the dummy TypedDict
            verification_request = {
                "task_id":state['task_id'],
                "data_id": item_to_verify.get("source_id", "unknown_id"),
                "data_to_verify": dummy_data_source_for_request
            }

        state['current_verification_request'] = verification_request
        state['human_in_loop_needed'] = True
        print(f"Simulating human verification needed for item: {item_to_verify.get('source_id')}")
    else:
        state['human_in_loop_needed'] = False
        state['current_verification_request'] = None

    return state

def synthesize_node(state: KnowledgeNexusState, llm: Optional[BaseChatModel]) -> KnowledgeNexusState:
    print(f"\n--- Agent: Synthesizer ---")
    state['error_message'] = None # Clear previous errors
    verified_data = state.get('verified_data', [])

    if not verified_data:
        print("No verified data to synthesize.")
        state['synthesized_content'] = "No verified data available to synthesize."
        return state

    print(f"Synthesizing content from {len(verified_data)} verified items...")

    # Format data for LLM
    context_parts = []
    for i, item in enumerate(verified_data):
        title = item.get('title', f"Source {i+1}")
        snippet = item.get('snippet', item.get('content', 'No content available'))
        url = item.get('url', 'N/A')
        context_parts.append(f"Source {i+1} (Title: {title}, URL: {url}):\n{snippet}\n---")

    context_string = "\n\n".join(context_parts)

    prompt_text = (
        f"You are an expert research synthesizer. Your task is to create a concise, coherent summary "
        f"from the following verified data sources related to the topic: '{state.get('topic', 'Not specified')}'. "
        f"Focus on extracting key facts, insights, and figures. Avoid speculation or information not present in the sources. "
        f"If there are conflicting pieces of information, note them if significant, but prioritize common themes. "
        f"The output should be a well-structured summary.\n\n"
        f"Verified Data Sources:\n{context_string}\n\n"
        f"Comprehensive Summary:"
    )

    if llm:
        try:
            print("Invoking LLM for synthesis...")
            response = llm.invoke(prompt_text)
            synthesized_text = response.content if hasattr(response, 'content') else str(response)
            state['synthesized_content'] = synthesized_text
            print("Synthesizer: Content synthesized successfully using LLM.")
        except Exception as e:
            print(f"Error during LLM invocation in synthesize_node: {e}")
            state['error_message'] = f"LLM synthesis failed: {str(e)}"
            state['synthesized_content'] = "Error during content synthesis. LLM call failed."
            # Fallback to simulated synthesis if LLM fails
            state['synthesized_content'] = f"Simulated synthesis (LLM error) for topic '{state['topic']}'. Based on {len(verified_data)} sources."
            print("Synthesizer: Used simulated synthesis due to LLM error.")
    else:
        print("Warning: LLM instance not available (OpenAI API key likely missing or invalid). Using simulated synthesis.")
        # Placeholder synthesis if LLM is not available
        content_summary = ", ".join([item.get('snippet', 'N/A')[:50] + "..." for item in verified_data])
        state['synthesized_content'] = f"Simulated synthesis for topic '{state['topic']}': Based on {len(verified_data)} sources. Key points might include: {content_summary}"
        print("Synthesizer: Used simulated synthesis as LLM was not configured.")

    return state

def conflict_detection_node(state: KnowledgeNexusState) -> KnowledgeNexusState:
    print(f"\n--- Agent: Conflict Detector ---")
    print("Checking for conflicts...")
    # Placeholder: No conflicts detected for now
    state['detected_conflicts'] = []
    print("Conflict detection complete. No conflicts (simulated).")
    return state

def document_generation_node(state: KnowledgeNexusState, llm: Optional[BaseChatModel]) -> KnowledgeNexusState:
    print(f"\n--- Agent: Document Generator ---")
    state['error_message'] = None # Clear previous errors
    synthesized_content = state.get('synthesized_content', "")

    if not synthesized_content or synthesized_content.startswith("No verified data") or synthesized_content.startswith("Simulated synthesis") or synthesized_content.startswith("Error during content synthesis"):
        print("Warning: Synthesized content is empty, placeholder, or indicates a prior error. Using simulated final document.")
        state['final_document'] = f"Simulated final document for topic '{state.get('topic', 'N/A')}'. Content synthesis was skipped or failed."
        if not synthesized_content: # If it's truly empty
             state['error_message'] = "Document generation skipped: No synthesized content available."
    elif llm is None:
        print("Warning: LLM not available for document generation. Using synthesized content directly as final document (simulation).")
        state['final_document'] = f"## Final Report (Simulated - LLM N/A for formatting) on: {state.get('topic', 'N/A')}\n\n{synthesized_content}"
        if state.get('detected_conflicts'):
            state['final_document'] += f"\n\n### Detected Conflicts:\n{len(state['detected_conflicts'])} conflicts found (details to be implemented)."
        else:
            state['final_document'] += f"\n\nNo conflicts were detected during this process."
    else:
        # For now, just pass through. LLM will be used for formatting in a later step.
        print("Document Generator: Passing synthesized content through. LLM formatting to be added later.")
        state['final_document'] = f"## Final Report on: {state.get('topic', 'N/A')}\n\n{synthesized_content}"
        if state.get('detected_conflicts'):
            state['final_document'] += f"\n\n### Detected Conflicts:\n{len(state['detected_conflicts'])} conflicts found (details to be implemented)."
        else:
            state['final_document'] += f"\n\nNo conflicts were detected during this process."

    print("Document generation node complete.")
    return state

def await_human_input_node(state: KnowledgeNexusState) -> KnowledgeNexusState:
    print(f"\n--- Workflow: Awaiting Human Input ---")
    feedback = state.get('human_feedback')

    if feedback:
        print(f"Human feedback received for data ID: {feedback['data_id']}. Approved: {feedback['approved']}")
        # Process the feedback
        # This is a simplified example. You'd need to find the specific item in verified_data
        # or research_data that corresponds to feedback['data_id'] and update it.
        # For now, we'll assume it applies to the item that triggered the verification.

        # Example: If there's an item in verified_data that matches feedback['data_id']
        # (This requires items in verified_data to have an 'id' or 'source_id' that matches)
        item_updated = False
        if state.get('verified_data'):
            for i, item in enumerate(state['verified_data']):
                # Assuming current_verification_request's data_id corresponds to an item's ID
                # And this ID is present in the items within verified_data
                # This logic might need to be more robust based on actual data structure
                if item.get("source_id") == feedback['data_id']: # Or whatever the ID field is named
                    if feedback['approved']:
                        item['status'] = 'verified_by_human'
                        item['verified_notes'] = feedback.get('notes')
                        if feedback.get('corrected_content'):
                            item['content'] = feedback['corrected_content'] # Update content if corrected
                            item['corrected_by_human'] = True
                        print(f"Item {feedback['data_id']} updated with human approval.")
                    else:
                        # Item was rejected. Remove it or mark it as rejected.
                        # For this example, let's mark it.
                        item['status'] = 'rejected_by_human'
                        item['rejection_notes'] = feedback.get('notes')
                        print(f"Item {feedback['data_id']} marked as rejected by human.")
                    item_updated = True
                    break # Assuming one item per verification request for now

        if not item_updated:
            print(f"Warning: Could not find item with ID {feedback['data_id']} in verified_data to apply human feedback.")

        state['human_in_loop_needed'] = False
        state['current_verification_request'] = None # Clear the request
        state['human_feedback'] = None  # Consume the feedback
        print("Human feedback processed. Workflow will now proceed.")
    elif state.get('human_in_loop_needed'):
        # This case means the node is entered because human_in_loop_needed was true,
        # but no feedback is yet available in the state. This is the "pause" state.
        print(f"Task '{state['task_id']}' is paused, waiting for human verification on data ID: {state.get('current_verification_request', {}).get('data_id')}")
        # The graph will effectively pause here if this node doesn't transition out.
        # An external mechanism (API endpoint) will need to inject 'human_feedback' into the state
        # and re-trigger the graph execution from this point.
    else:
        # This case should ideally not be reached if routing is correct
        # (i.e., only come to this node if human_in_loop_needed is true).
        print("Awaiting human input, but no specific request found and human_in_loop_needed is false. Proceeding cautiously.")
        state['human_in_loop_needed'] = False # Ensure it's false before proceeding

    return state


# 3. Implement Conditional Edges
def should_request_human_verification(state: KnowledgeNexusState) -> str:
    print(f"\n--- Workflow: Conditional Edge ---")
    if state.get('human_in_loop_needed') and state.get('current_verification_request'):
        print("Decision: Human verification IS needed.")
        return "human_verification_needed"
    else:
        print("Decision: No human verification needed, proceeding to synthesis.")
        return "synthesize_data"


# 4. Create build_knowledge_nexus_workflow function
def build_knowledge_nexus_workflow(chroma_service: Optional[ChromaService] = None):
    print("Building Knowledge Nexus workflow graph...")
    if not chroma_service:
        print("Warning: ChromaService instance is not provided to build_knowledge_nexus_workflow. Using dummy for now.")
        # Define a dummy ChromaService if not provided, so partial doesn't fail
        class DummyChromaService:
             def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
                print(f"DummyChromaService: Add {len(documents)} documents to {collection_name}.")
                return True
        chroma_service = DummyChromaService() # type: ignore

    workflow = StateGraph(KnowledgeNexusState)

    # Use functools.partial to pass chroma_service to nodes that need it
    research_node_with_service = functools.partial(research_node, chroma_service=chroma_service)
    verify_node_with_service = functools.partial(verify_node, chroma_service=chroma_service)

    # Initialize LLM instance
    llm_instance: Optional[BaseChatModel] = None
    if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT and OPENAI_API_VERSION and AZURE_OPENAI_DEPLOYMENT_NAME:
        try:
            llm_instance = AzureChatOpenAI(
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_API_KEY,
                api_version=OPENAI_API_VERSION,
                azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
                temperature=0.2,
                # model_name="gpt-3.5-turbo" # model_name is often not needed if azure_deployment is specified
            )
            print("AzureChatOpenAI LLM initialized successfully.")
        except Exception as e:
            print(f"Error initializing AzureChatOpenAI: {e}. LLM will be None.")
            llm_instance = None # Ensure it's None on failure
    else:
        print("WARNING: Azure OpenAI environment variables (AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME) not fully set. Azure LLM not initialized.")
        # Optional: Fallback to ChatOpenAI if desired, or just leave llm_instance as None
        # For now, let's not fallback to maintain clarity on which LLM is active.
        # If you want a fallback:
        # print("Attempting to fall back to standard OpenAI...")
        # if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_ACTUAL_OPENAI_API_KEY_REPLACE_ME":
        #     try:
        #         llm_instance = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo", temperature=0.2)
        #         print("ChatOpenAI LLM initialized successfully as a fallback.")
        #     except Exception as e_std:
        #         print(f"Error initializing standard ChatOpenAI as fallback: {e_std}. LLM will be None.")
        # else:
        #     print("Standard OPENAI_API_KEY not found or is a placeholder. No LLM will be initialized.")

    synthesize_node_with_llm = functools.partial(synthesize_node, llm=llm_instance)
    document_generation_node_with_llm = functools.partial(document_generation_node, llm=llm_instance)

    # Add nodes
    workflow.add_node("research", research_node_with_service)
    workflow.add_node("verify", verify_node_with_service)
    workflow.add_node("synthesize", synthesize_node_with_llm)
    workflow.add_node("detect_conflicts", conflict_detection_node) # No LLM or Chroma needed yet
    workflow.add_node("generate_document", document_generation_node_with_llm)
    workflow.add_node("await_human_input", await_human_input_node) # No LLM or Chroma needed

    # Set entry point
    workflow.set_entry_point("research")

    # Define edges
    workflow.add_edge("research", "verify")

    workflow.add_conditional_edges(
        "verify",
        should_request_human_verification,
        {
            "human_verification_needed": "await_human_input", # This path will pause here
            "synthesize_data": "synthesize"
        }
    )

    workflow.add_edge("synthesize", "detect_conflicts")
    workflow.add_edge("detect_conflicts", "generate_document")
    workflow.add_edge("generate_document", END)

    # Edge from await_human_input: after human input is processed (or if not needed), proceed to synthesize
    workflow.add_edge("await_human_input", "synthesize")

    # Compile the graph
    app = workflow.compile()
    print("Knowledge Nexus workflow graph compiled successfully.")
    return app

# Example of how to run (for testing purposes)
if __name__ == '__main__':
    print("Starting test run of Knowledge Nexus workflow...")
    # Initialize ChromaService for testing
    try:
        test_chroma_service = ChromaService(persist_directory="./test_chroma_db_workflow_main")
        print("Test ChromaService initialized.")
    except Exception as e:
        print(f"Could not init real ChromaService for test run in main: {e}. Using dummy ChromaService.")
        class DummyChromaService:
            def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
                print(f"DummyChroma (main): Add {len(documents)} docs to {collection_name}.")
                return True
        test_chroma_service = DummyChromaService() # type: ignore

    # LLM instance is now created within build_knowledge_nexus_workflow based on env vars
    # So, no need to create/pass it separately here for the main test block.
    # build_knowledge_nexus_workflow will handle printing warnings if keys are missing.

    workflow_app = build_knowledge_nexus_workflow(chroma_service=test_chroma_service)

    # Initial state for a run
    # Example topic that might yield varied results
    example_topic = "The role of quantum computing in drug discovery"
    initial_state = {
        "topic": example_topic,
        "topic": "Artificial Intelligence in Healthcare",
        "task_id": f"task_{uuid.uuid4()}",
        "research_data": [],
        "verified_data": [],
        "synthesized_content": "",
        "detected_conflicts": [],
        "final_document": "",
        "human_in_loop_needed": False,
        "current_verification_request": None,
        "messages": [],
        "error_message": None,
        "human_feedback": None # Initialize new state field
    }

    # To test the human input path, you would need to:
    # 1. Run the graph until it reaches 'await_human_input'.
    # 2. Externally update the state (e.g., via a simulated API call that populates 'human_feedback').
    # 3. Resume the graph execution with the updated state.
    # LangGraph's `checkpoint` and `config` features are essential for robustly managing this.
    # For this basic `if __name__ == '__main__'` test, we'll mostly see the path that doesn't require human input
    # or the path that pauses, or simulated research if TAVILY_API_KEY is not set.

    print(f"\nInvoking workflow for task ID: {initial_state['task_id']}...")
    # Stream events from the graph
    for event in workflow_app.stream(initial_state):
        # The event will be a dictionary where keys are node names
        # and values are the output of that node (the state).
        for node_name, output_state in event.items():
            print(f"\nOutput from node: {node_name}")
            # print(f"Current state keys: {output_state.keys()}") # Can be very verbose
            print(f"  Topic: {output_state.get('topic')}")
            if output_state.get('final_document'):
                print(f"  Final Document Preview: {output_state['final_document'][:100]}...")
            if output_state.get('error_message'):
                print(f"  Error: {output_state['error_message']}")
            if node_name == END:
                print(f"\n--- Workflow Execution Finished for Task ID: {initial_state['task_id']} ---")
                print("Final State Keys:") # print(output_state.keys())
                # print(output_state) # Display full final state
                print(f"  Final Document: {output_state.get('final_document')}")
                print(f"  Human in Loop Needed at End: {output_state.get('human_in_loop_needed')}")
                if output_state.get('current_verification_request'):
                    print(f"  Pending Verification: Data ID {output_state['current_verification_request']['data_id']}")


    print("\nTest run finished.")
    print("REMINDER: Ensure TAVILY_API_KEY is correctly set in backend/.env for actual internet searches.")
