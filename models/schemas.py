from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str = Field(..., description="'customer' or 'agent'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None

class ConversationData(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation identifier")
    customer_id: str = Field(..., description="Customer identifier")
    agent_id: Optional[str] = Field(None, description="Agent identifier")
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

class IngestRequest(BaseModel):
    conversations: List[ConversationData] = Field(..., description="List of conversations to ingest")
    batch_id: Optional[str] = Field(None, description="Optional batch identifier")

class IngestResponse(BaseModel):
    success: bool
    processed_count: int
    failed_count: int
    batch_id: Optional[str] = None
    errors: List[str] = Field(default_factory=list)

class ChatQuery(BaseModel):
    query: str = Field(..., description="Customer query")
    customer_id: str = Field(..., description="Customer identifier")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SourceReference(BaseModel):
    source_id: str
    conversation_id: str
    snippet: str
    relevance_score: float

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI-generated response")
    confidence: float = Field(..., description="Confidence score 0-1")
    sources: List[SourceReference] = Field(default_factory=list)
    escalate_to_human: bool = Field(default=False)
    reasoning: Optional[str] = None
    query_id: Optional[str] = None

class IssueNode(BaseModel):
    id: str
    canonical_description: str
    one_liner: str
    tags: List[str]
    intent: str
    embedding: List[float]
    quality_score: float = 0.0
    human_reviewed: bool = False
    created_at: datetime
    updated_at: datetime

class SolutionNode(BaseModel):
    id: str
    canonical_description: str
    one_liner: str
    steps: List[str]
    confidence: float
    embedding: List[float]
    quality_score: float = 0.0
    human_reviewed: bool = False
    created_at: datetime
    updated_at: datetime