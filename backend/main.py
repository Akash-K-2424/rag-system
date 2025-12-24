""""
GET  /health  → {status, vector_db_ready, embedding_model_ready}
POST /upload  → Upload PDF → {filename, chunks_created, total_tokens}
POST /chat    → {query} → {answer, citations, confidence, retrieved_chunks}
"""

"""
FastAPI backend for RAG system.
Exposes REST endpoints for document upload and querying.
Domain: Academic & Research Documents (AI & ML PDFs)
"""

import os
import tempfile
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try to import agent, but provide mock if dependencies fail
try:
    from agent import RAGAgent
    from schemas import ChatRequest, ChatResponse, UploadResponse, HealthResponse
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import agent dependencies: {e}")
    AGENT_AVAILABLE = False
    
    # Mock classes for demo
    from pydantic import BaseModel
    from typing import List, Optional
    
    class Citation(BaseModel):
        document: str
        page: int
        chunk_id: str
    
    class ChatRequest(BaseModel):
        query: str
        conversation_id: Optional[str] = None
    
    class ChatResponse(BaseModel):
        answer: str
        citations: List[Citation] = []
        confidence: float = 0.0
        retrieved_chunks: int = 0
    
    class UploadResponse(BaseModel):
        filename: str
        chunks_created: int
        total_tokens: int
        status: str = "success"
    
    class HealthResponse(BaseModel):
        status: str = "healthy"
        vector_db_ready: bool = False
        embedding_model_ready: bool = False


# Initialize FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Retrieval-Augmented Generation for Academic & Research Documents",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG agent
agent = None
if AGENT_AVAILABLE:
    try:
        from agent import RAGAgent
        agent = RAGAgent()
        print("✓ RAG Agent initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize RAG Agent: {e}")
        print("⚠️  Running in demo mode without full RAG functionality")
else:
    print("⚠️  Running in demo mode - dependencies not available")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Verifies system components are ready.
    """
    return HealthResponse(
        status="healthy" if agent else "degraded",
        vector_db_ready=agent is not None,
        embedding_model_ready=agent is not None
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and ingest a PDF document.
    
    - Accepts PDF files
    - Extracts text and creates chunks
    - Stores embeddings in vector database
    - Returns chunk count and token count
    
    Args:
        file: PDF file to upload
        
    Returns:
        UploadResponse with ingestion results
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Extract document name (without extension)
        document_name = file.filename.replace('.pdf', '')
        
        if agent:
            # Ingest document using agent
            result = agent.ingest_and_store(tmp_path, document_name)
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            if result["status"] != "success":
                raise HTTPException(status_code=400, detail=result.get("error", "Ingestion failed"))
            
            return UploadResponse(
                filename=file.filename,
                chunks_created=result["chunks_created"],
                total_tokens=result["total_tokens"],
                status="success"
            )
        else:
            # Demo mode - simulate successful upload
            os.unlink(tmp_path)
            return UploadResponse(
                filename=file.filename,
                chunks_created=42,
                total_tokens=12500,
                status="success (demo mode)"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process user query and return RAG-based answer with citations.
    Supports conversation memory for context-aware responses.
    
    Args:
        request: ChatRequest with user query and optional conversation_id
        
    Returns:
        ChatResponse with answer, citations, and confidence
    """
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        if agent:
            # Process query through RAG pipeline with memory
            response = agent.process_query(
                request.query, 
                conversation_id=request.conversation_id
            )
            return response
        else:
            # Demo mode - return simulated response
            return ChatResponse(
                answer=f"Demo Response: This is a simulated answer to your query: '{request.query}'. In production, this would be grounded in your uploaded documents with proper citations.",
                citations=[
                    Citation(document="sample_document.pdf", page=1, chunk_id="sample_0"),
                    Citation(document="sample_document.pdf", page=3, chunk_id="sample_5")
                ],
                confidence=0.85,
                retrieved_chunks=5
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "RAG System API",
        "description": "Retrieval-Augmented Generation for Academic & Research Documents",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "upload": "POST /upload",
            "chat": "POST /chat"
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"\n{'='*60}")
    print(f"RAG System Backend")
    print(f"{'='*60}")
    print(f"Starting server on {host}:{port}")
    print(f"API Docs: http://localhost:{port}/docs")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
