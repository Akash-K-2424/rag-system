# RAG System - Architecture Documentation

Detailed technical architecture of the RAG system.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (React)                   │
│              Chat | Upload | Citation Viewer                 │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────────┐
│                   FASTAPI BACKEND                            │
├─────────────────────────────────────────────────────────────┤
│  Agent Orchestration Layer (Kiro)                            │
│  ├─ ingest_documents()                                       │
│  ├─ embed_chunks()                                           │
│  ├─ vector_search()                                          │
│  ├─ rerank_context()                                         │
│  └─ generate_answer_with_citations()                         │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼──────────┐ ┌──▼──────────────┐
│  ChromaDB      │ │ SentenceXForm  │ │ Gemini/OpenAI   │
│  (Vector DB)   │ │ (Embeddings)   │ │ (LLM)           │
└────────────────┘ └────────────────┘ └─────────────────┘
```

## Data Flow

### Document Ingestion Pipeline

```
PDF Upload
    ↓
[ingest.py] Extract Text
    ↓
Split into Chunks (400 tokens, 80-token overlap)
    ↓
Extract Metadata (document_name, page_number, chunk_id)
    ↓
[retriever.py] Generate Embeddings (SentenceTransformers)
    ↓
Store in ChromaDB with Metadata
    ↓
Ready for Retrieval
```

### Query Processing Pipeline

```
User Query
    ↓
[agent.py] tool_vector_search()
    ├─ Embed query using SentenceTransformers
    ├─ Search ChromaDB for top-5 similar chunks
    └─ Return with similarity scores
    ↓
[agent.py] tool_rerank_context()
    ├─ Apply MMR (Maximal Marginal Relevance)
    ├─ Balance relevance and diversity
    └─ Return re-ranked chunks
    ↓
[agent.py] tool_generate_answer_with_citations()
    ├─ Build context-only prompt
    ├─ Call Gemini API
    ├─ Extract citations from metadata
    ├─ Calculate confidence score
    └─ Apply confidence threshold
    ↓
Return Answer + Citations + Confidence
```

## Component Details

### 1. Document Ingestion (ingest.py)

**Purpose:** Extract and chunk PDF documents

**Key Functions:**
- `extract_text_from_pdf()`: Parse PDF with page tracking
- `chunk_text()`: Split into overlapping chunks
- `estimate_tokens()`: Approximate token count
- `ingest_document()`: Complete pipeline

**Chunking Strategy:**
- Chunk size: 400 tokens (configurable)
- Overlap: 80 tokens (configurable)
- Boundary: Sentence-based for semantic coherence
- Metadata: document_name, page_number, chunk_id

**Token Estimation:**
- Uses word-based heuristic: 1 token ≈ 1.3 words
- Approximates OpenAI tokenization

### 2. Vector Retrieval (retriever.py)

**Purpose:** Store and retrieve document chunks using vector similarity

**Key Components:**
- **Embedding Model:** SentenceTransformers (all-MiniLM-L6-v2)
  - Lightweight (22M parameters)
  - Fast inference
  - Good semantic understanding
  
- **Vector Database:** ChromaDB
  - Persistent storage
  - Cosine similarity search
  - Metadata filtering

**Retrieval Process:**
1. Embed query using SentenceTransformers
2. Search ChromaDB for top-k similar chunks
3. Return with similarity scores

**Re-ranking (MMR):**
- Balances relevance and diversity
- Formula: `MMR = λ * relevance - (1-λ) * diversity`
- Default λ = 0.5 (equal weight)
- Reduces redundancy in results

### 3. Answer Generation (generator.py)

**Purpose:** Generate answers grounded in retrieved context

**Hallucination Control Mechanisms:**

1. **Context-Only Prompting**
   - Explicit instruction: "Answer ONLY using provided context"
   - Fallback: "Insufficient information in documents"
   - Prevents LLM from using training data

2. **Confidence Threshold**
   - Calculated from:
     - Average similarity of retrieved chunks (60% weight)
     - Answer length relative to context (40% weight)
   - Default threshold: 0.5
   - Below threshold: Return fallback response

3. **Citation Extraction**
   - Automatically extract from metadata
   - Include document name and page number
   - Deduplicate citations

**LLM Integration:**
- Provider: Google Gemini API
- Model: gemini-pro
- Temperature: Default (0.7)
- Max tokens: Default (2048)

### 4. Agent Orchestration (agent.py)

**Purpose:** Coordinate RAG pipeline with explicit tool calls

**Tools:**
1. `tool_ingest_documents()` - Document ingestion
2. `tool_embed_chunks()` - Embedding generation
3. `tool_vector_search()` - Vector similarity search
4. `tool_rerank_context()` - MMR re-ranking
5. `tool_generate_answer_with_citations()` - Answer generation

**Orchestration Methods:**
- `process_query()` - Complete query pipeline
- `ingest_and_store()` - Complete ingestion pipeline

### 5. FastAPI Backend (main.py)

**Endpoints:**

- `GET /health` - Health check
  - Returns: status, vector_db_ready, embedding_model_ready
  
- `POST /upload` - Document upload
  - Input: PDF file
  - Returns: filename, chunks_created, total_tokens
  
- `POST /chat` - Query processing
  - Input: query string
  - Returns: answer, citations, confidence, retrieved_chunks

**CORS Configuration:**
- Allows all origins (configure for production)
- Supports credentials
- Allows all methods and headers

## Configuration

### Environment Variables

```
# API Configuration
GEMINI_API_KEY=your-key-here
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=False

# Vector Database
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# RAG Configuration
CHUNK_SIZE=400
CHUNK_OVERLAP=80
TOP_K_RETRIEVAL=5
CONFIDENCE_THRESHOLD=0.5
```

### Tuning Parameters

**For Better Coverage:**
- Increase `TOP_K_RETRIEVAL` (5 → 10)
- Decrease `CONFIDENCE_THRESHOLD` (0.5 → 0.3)
- Increase `CHUNK_SIZE` (400 → 600)

**For Better Precision:**
- Decrease `TOP_K_RETRIEVAL` (5 → 3)
- Increase `CONFIDENCE_THRESHOLD` (0.5 → 0.7)
- Decrease `CHUNK_SIZE` (400 → 300)

## Performance Characteristics

### Latency

- Document ingestion: ~2-5 seconds per page
- Query processing: ~3-8 seconds
  - Embedding: ~0.5s
  - Retrieval: ~0.5s
  - Re-ranking: ~1s
  - Generation: ~2-5s

### Storage

- Embedding size: 384 dimensions (all-MiniLM-L6-v2)
- Per chunk: ~1.5KB (embedding + metadata)
- 1000 chunks: ~1.5MB

### Scalability

- ChromaDB: Handles 100K+ chunks efficiently
- SentenceTransformers: Batch processing for speed
- Gemini API: Rate limits apply (check quota)

## Security Considerations

1. **API Keys**
   - Store GEMINI_API_KEY in environment variables
   - Never commit to version control
   - Rotate regularly

2. **CORS**
   - Configure allowed origins for production
   - Restrict to specific domains

3. **Input Validation**
   - Validate file types (PDF only)
   - Limit file size
   - Sanitize query strings

4. **Rate Limiting**
   - Implement per-user rate limits
   - Monitor API usage
   - Set quotas

## Monitoring & Logging

### Logging

- Agent logs: `[AGENT] Tool: ...`
- FastAPI logs: Request/response logs
- Error logs: Exceptions and failures

### Metrics to Track

- Document ingestion time
- Query processing time
- Confidence scores
- Citation accuracy
- API error rates

## Future Enhancements

1. **Conversational Memory**
   - Multi-turn context
   - Session management
   - History persistence

2. **Advanced Retrieval**
   - Hybrid search (BM25 + vector)
   - Semantic caching
   - Query expansion

3. **Scaling**
   - Distributed embeddings
   - Async processing
   - Load balancing

4. **Evaluation**
   - RAGAS metrics
   - User feedback loop
   - A/B testing

## References

- ChromaDB: https://docs.trychroma.com/
- SentenceTransformers: https://www.sbert.net/
- FastAPI: https://fastapi.tiangolo.com/
- Google Gemini: https://ai.google.dev/
