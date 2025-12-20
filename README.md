# RAG System: Academic & Research Document Q&A

A production-ready Retrieval-Augmented Generation (RAG) system designed for querying academic and research documents (AI & ML PDFs). Users can upload documents, ask questions, and receive answers grounded strictly in retrieved content with proper citations.

## Problem Statement

Traditional LLMs suffer from hallucinations when answering domain-specific questions. This system ensures answers are:
- **Grounded in source documents** (no hallucinations)
- **Cited with document name and page number**
- **Accurate and verifiable**

Perfect for research teams, students, and organizations managing large document repositories.

## Architecture

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

## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI (REST API)
- ChromaDB (vector database)
- SentenceTransformers (embeddings)
- Google Gemini API (LLM)
- PyPDF2 (PDF parsing)

**Frontend:**
- React 18 (Vite)
- Axios (HTTP client)
- TailwindCSS (styling)
- Vercel (deployment)

**Deployment:**
- Backend: Render/Railway
- Frontend: Vercel

## How RAG Works

1. **Document Ingestion**: PDFs are uploaded and parsed into chunks (400 tokens, 80-token overlap)
2. **Embedding**: Each chunk is converted to a vector using SentenceTransformers
3. **Storage**: Vectors and metadata stored in ChromaDB
4. **Query Processing**: User question is embedded
5. **Retrieval**: Top-5 similar chunks retrieved via vector similarity
6. **Re-ranking**: Results re-ranked by relevance (MMR)
7. **Generation**: LLM generates answer using only retrieved context
8. **Citations**: Answer includes document name and page number

## Hallucination Control

- **Context-only prompting**: LLM instructed to answer only from provided context
- **Confidence threshold**: Answers below confidence threshold trigger fallback
- **Fallback response**: "Insufficient information in documents" if context is weak

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Gemini API key (or OpenAI)

### Local Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"
python main.py
```

Backend runs on `http://localhost:8000`

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

### API Endpoints

- `POST /upload` - Upload PDF documents
- `POST /chat` - Ask questions
- `GET /health` - Health check

### Example Usage

**Upload Document:**
```bash
curl -X POST -F "file=@paper.pdf" http://localhost:8000/upload
```

**Ask Question:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is transformer architecture?"}'
```

## Deployment

### Deploy Backend (Render)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repo
4. Set environment variables: `GEMINI_API_KEY`
5. Deploy

### Deploy Frontend (Vercel)

1. Push code to GitHub
2. Import project in Vercel
3. Set build command: `npm run build`
4. Set output directory: `dist`
5. Deploy

Update `frontend/.env.production` with backend URL:
```
VITE_API_URL=https://your-backend.onrender.com
```

## Project Structure

```
rag-system/
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── agent.py             # Kiro agent orchestration
│   ├── ingest.py            # PDF ingestion pipeline
│   ├── retriever.py         # Vector search & re-ranking
│   ├── generator.py         # LLM answer generation
│   ├── schemas.py           # Pydantic models
│   ├── requirements.txt      # Python dependencies
│   └── .env.example         # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── App.jsx          # Main app
│   │   └── main.jsx         # Entry point
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite config
├── data/
│   └── sample_pdfs/         # Sample documents
└── README.md                # This file
```

## Features

✅ PDF document upload  
✅ Semantic search with vector embeddings  
✅ Context re-ranking (MMR)  
✅ Citation tracking (document + page)  
✅ Hallucination prevention  
✅ Chat history  
✅ Responsive UI  
✅ Production-ready deployment  

## Future Enhancements

- Conversational memory (multi-turn context)
- Streaming responses
- Cached embeddings
- Multiple LLM support
- Advanced filtering (date, author, category)
- Analytics dashboard

## License

MIT

## Support

For issues or questions, open an issue on GitHub.
