# RAG System - Project Summary

Complete overview of the production-ready RAG system for academic and research documents.

## Project Overview

A full-stack Retrieval-Augmented Generation (RAG) system that enables users to upload academic/research PDFs and ask questions with answers grounded strictly in the documents. The system prevents hallucinations through context-only prompting, confidence thresholds, and proper citation tracking.

**Domain:** Academic & Research Documents (AI & ML PDFs)

## Key Features

✅ **Document Management**
- PDF upload and parsing
- Automatic text extraction with page tracking
- Intelligent chunking (400 tokens, 80-token overlap)
- Metadata preservation (document name, page number, chunk ID)

✅ **Semantic Search**
- Vector embeddings using SentenceTransformers
- ChromaDB for persistent vector storage
- Top-5 similarity-based retrieval
- MMR (Maximal Marginal Relevance) re-ranking

✅ **Hallucination Prevention**
- Context-only prompting (LLM instructed to use only provided context)
- Confidence threshold filtering (default 0.5)
- Fallback responses for low-confidence answers
- Automatic citation extraction

✅ **User Interface**
- Chat-style interface for natural interaction
- Document upload with progress feedback
- Expandable citation viewer
- Real-time message history
- Loading states and error handling

✅ **Production Ready**
- FastAPI backend with CORS support
- Vercel-ready React frontend
- Docker containerization
- Environment-based configuration
- Health check endpoints
- Comprehensive error handling

## Technology Stack

### Backend
- **Framework:** FastAPI (Python)
- **Vector DB:** ChromaDB
- **Embeddings:** SentenceTransformers (all-MiniLM-L6-v2)
- **LLM:** Google Gemini API
- **PDF Parsing:** PyPDF2
- **Server:** Uvicorn

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite
- **Styling:** TailwindCSS
- **HTTP Client:** Axios
- **Deployment:** Vercel

### Infrastructure
- **Backend Hosting:** Render/Railway
- **Frontend Hosting:** Vercel
- **Containerization:** Docker
- **Version Control:** Git

## Project Structure

```
rag-system/
├── backend/
│   ├── main.py              # FastAPI application & endpoints
│   ├── agent.py             # Kiro agent orchestration (5 tools)
│   ├── ingest.py            # PDF ingestion pipeline
│   ├── retriever.py         # Vector search & MMR re-ranking
│   ├── generator.py         # LLM answer generation
│   ├── schemas.py           # Pydantic data models
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Docker configuration
│   ├── render.yaml          # Render deployment config
│   ├── .env.example         # Environment template
│   └── .gitignore
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx    # Main chat component
│   │   │   ├── Message.jsx          # Message display
│   │   │   ├── CitationViewer.jsx   # Citation display
│   │   │   └── DocumentUpload.jsx   # Upload component
│   │   ├── api.js           # API client
│   │   ├── App.jsx          # Main app component
│   │   ├── main.jsx         # Entry point
│   │   └── index.css        # Global styles
│   ├── package.json         # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── tailwind.config.js   # TailwindCSS config
│   ├── postcss.config.js    # PostCSS config
│   ├── vercel.json          # Vercel deployment config
│   ├── .env.example         # Environment template
│   └── .gitignore
│
├── data/
│   └── sample_pdfs/         # Sample documents for testing
│
├── README.md                # Main documentation
├── QUICKSTART.md            # 5-minute setup guide
├── SETUP.md                 # Detailed setup & deployment
├── ARCHITECTURE.md          # Technical architecture
├── TESTING.md               # Testing procedures
├── PROJECT_SUMMARY.md       # This file
└── .gitignore
```

## RAG Pipeline

### Step 1: Document Ingestion
```
PDF Upload → Extract Text → Split into Chunks → Extract Metadata
```
- Chunk size: 400 tokens
- Overlap: 80 tokens
- Metadata: document_name, page_number, chunk_id

### Step 2: Embedding Generation
```
Chunks → SentenceTransformers → 384-dim Vectors → ChromaDB
```
- Model: all-MiniLM-L6-v2 (22M parameters)
- Storage: Persistent ChromaDB
- Indexing: Cosine similarity

### Step 3: Query Processing
```
User Query → Embed → Vector Search → MMR Re-rank → LLM Generation
```
- Retrieval: Top-5 similar chunks
- Re-ranking: Maximal Marginal Relevance
- Generation: Context-only prompting

### Step 4: Answer Generation
```
Context + Query → Gemini API → Answer + Citations + Confidence
```
- Hallucination control: 3 mechanisms
- Citations: Document name + page number
- Confidence: 0-1 score

## API Endpoints

### Health Check
```
GET /health
Response: {status, vector_db_ready, embedding_model_ready}
```

### Document Upload
```
POST /upload
Input: PDF file
Response: {filename, chunks_created, total_tokens, status}
```

### Query Processing
```
POST /chat
Input: {query: string}
Response: {answer, citations, confidence, retrieved_chunks}
```

## Agent Orchestration (Kiro)

The system uses explicit tool-based orchestration:

1. **tool_ingest_documents()** - Parse and chunk PDFs
2. **tool_embed_chunks()** - Generate and store embeddings
3. **tool_vector_search()** - Retrieve similar chunks
4. **tool_rerank_context()** - Apply MMR re-ranking
5. **tool_generate_answer_with_citations()** - Generate answer

Each tool is called explicitly in sequence, making the pipeline transparent and debuggable.

## Hallucination Control

### Mechanism 1: Context-Only Prompting
- LLM receives explicit instruction: "Answer ONLY using provided context"
- Fallback response: "Insufficient information in documents"
- Prevents using training data

### Mechanism 2: Confidence Threshold
- Calculated from:
  - Average similarity of retrieved chunks (60%)
  - Answer length relative to context (40%)
- Default threshold: 0.5
- Below threshold: Return fallback response

### Mechanism 3: Citation Extraction
- Automatically extract from metadata
- Include document name and page number
- Deduplicate citations
- Verify grounding

## Configuration

### Environment Variables

```bash
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

## Performance Metrics

### Latency
- Document ingestion: 2-5 seconds per page
- Query processing: 3-8 seconds
  - Embedding: ~0.5s
  - Retrieval: ~0.5s
  - Re-ranking: ~1s
  - Generation: ~2-5s

### Storage
- Per chunk: ~1.5KB (embedding + metadata)
- 1000 chunks: ~1.5MB

### Scalability
- ChromaDB: 100K+ chunks
- SentenceTransformers: Batch processing
- Gemini API: Rate limits apply

## Deployment

### Local Development
```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev
```

### Production (Render + Vercel)

**Backend (Render):**
1. Push to GitHub
2. Create Web Service on Render
3. Set environment variables
4. Deploy

**Frontend (Vercel):**
1. Push to GitHub
2. Import project in Vercel
3. Set build command: `npm run build`
4. Deploy

## Testing

### Unit Tests
- Document ingestion
- Embedding generation
- Vector search
- Answer generation

### Integration Tests
- API endpoints
- End-to-end pipeline
- Error handling

### Manual Testing
- Document upload
- Query processing
- Citation accuracy
- Hallucination prevention

See TESTING.md for comprehensive test procedures.

## Security

- API keys in environment variables
- CORS configuration
- Input validation
- Rate limiting
- Error message sanitization

## Future Enhancements

1. **Conversational Memory** - Multi-turn context
2. **Advanced Retrieval** - Hybrid search, semantic caching
3. **Scaling** - Distributed embeddings, async processing
4. **Evaluation** - RAGAS metrics, user feedback
5. **Multiple LLMs** - OpenAI, Anthropic, local models
6. **Advanced Filtering** - Date, author, category
7. **Analytics** - Usage tracking, performance monitoring

## Getting Started

### Quick Start (5 minutes)
See QUICKSTART.md

### Detailed Setup
See SETUP.md

### Architecture Details
See ARCHITECTURE.md

### Testing Guide
See TESTING.md

## Support & Documentation

- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **README:** Main documentation
- **QUICKSTART:** 5-minute setup
- **SETUP:** Detailed setup & deployment
- **ARCHITECTURE:** Technical details
- **TESTING:** Testing procedures

## Code Quality

- Type hints throughout
- Comprehensive docstrings
- Clear variable names
- Modular architecture
- Error handling
- Logging

## License

MIT

## Author

Built as a production-ready RAG system for AI/ML internship assessment.

---

**Status:** ✅ Complete and Ready for Deployment

**Last Updated:** December 2024

**Version:** 1.0.0
