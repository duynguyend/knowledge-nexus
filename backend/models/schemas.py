from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str


class ResearchStatus(BaseModel):
    task_id: str
    status: str  # e.g., "pending", "in_progress", "completed", "failed", "needs_human_input"
    message: Optional[str] = None
    progress: Optional[float] = None  # e.g., 0.5 for 50%
    sources_explored: Optional[int] = None
    data_collected: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    verification_request: Optional['DataVerificationRequest'] = None # Added for HITL


class DocumentOutput(BaseModel):
    task_id: str
    document_content: str
    format: str  # e.g., "markdown", "pdf", "text"


class DataSource(BaseModel):
    id: str  # Could be a hash of the content or a URL
    url: Optional[str] = None
    content_preview: str  # A snippet or summary of the content


class DataVerificationRequest(BaseModel):
    task_id: str
    data_id: str
    data_to_verify: 'DataSource'  # The specific piece of data/claim
    conflicting_sources: Optional[List['DataSource']] = None


class HumanApproval(BaseModel):
    task_id: str
    data_id: str
    approved: bool
    notes: Optional[str] = None
    corrected_content: Optional[str] = None # If human provides a correction


class Conflict(BaseModel):
    conflict_id: str
    task_id: str
    description: str # Description of the conflict
    sources_involved: List[DataSource] # IDs or full objects of conflicting data sources
    suggested_resolution: Optional[str] = None


class ConflictResolution(BaseModel):
    conflict_id: str
    task_id: str
    chosen_resolution: str  # Could be one of the source IDs, or a new user-provided statement/correction
    user_notes: Optional[str] = None
