"""
Pydantic schemas for RAG system API requests and responses.
Domain: Academic & Research Documents (AI & ML PDFs)
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Citation(BaseModel):
    """Citation metadata for retrieved content."""
    document: str = Field(..., description="Name of the source document")
    page: int = Field(..., description="Page number in the document")
    chunk_id: str = Field(..., description="Unique chunk identifier")


class ChatRequest(BaseModel):
    """User query request."""
    query: str = Field(..., min_length=1, max_length=1000, description="User question")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for multi-turn")


class ChatResponse(BaseModel):
    """RAG system response with citations."""
    answer: str = Field(..., description="Generated answer grounded in documents")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    retrieved_chunks: int = Field(..., description="Number of chunks retrieved")


class UploadResponse(BaseModel):
    """Document upload response."""
    filename: str = Field(..., description="Uploaded filename")
    chunks_created: int = Field(..., description="Number of chunks created")
    total_tokens: int = Field(..., description="Total tokens in document")
    status: str = Field(default="success", description="Upload status")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy", description="System status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    vector_db_ready: bool = Field(..., description="Vector database status")
    embedding_model_ready: bool = Field(..., description="Embedding model status")
