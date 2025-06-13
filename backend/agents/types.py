from typing import TypedDict, List, Dict, Optional, Any
from langchain_core.messages import BaseMessage

# This was originally in research_workflow.py
class DataVerificationRequest(TypedDict):
    task_id: str
    data_id: str
    data_to_verify: Dict # Simplified, consider a more specific type for data_to_verify
    # conflicting_sources: List[DataSource] # Example of more specific typing

# This was originally in research_workflow.py
class HumanApproval(TypedDict):
    task_id: str
    data_id: str
    approved: bool
    notes: Optional[str]
    corrected_content: Optional[str]

# This was originally in research_workflow.py (KnowledgeNexusState)
class KnowledgeNexusState(TypedDict):
    topic: str
    task_id: str  # Unique ID for the entire research task
    current_stage: str # Added field to track current human-readable stage
    research_data: List[Dict[str, Any]]  # Raw data from internet research
    verified_data: List[Dict[str, Any]]  # Verified data
    synthesized_content: str
    detected_conflicts: List[Dict[str, Any]]  # List of conflict details
    final_document: str
    human_in_loop_needed: bool
    current_verification_request: Optional[DataVerificationRequest]
    messages: List[BaseMessage]  # For conversation history with LLMs
    error_message: Optional[str]
    human_feedback: Optional[HumanApproval] # For HITL
    sources_explored: int # For progress tracking
    data_collected: int # For progress tracking
    # num_search_results: Optional[int] # Example: if we want to control this per task
