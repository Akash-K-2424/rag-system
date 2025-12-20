# RAG System - Quick Start Guide

Get the RAG system running in 5 minutes.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Google Gemini API key (free at https://makersuite.google.com/app/apikey)

## 1. Clone Repository

```bash
git clone <your-repo-url>
cd rag-system
```

## 2. Backend Setup (2 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your API key
# GEMINI_API_KEY=your-key-here
```

## 3. Frontend Setup (1 minute)

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# VITE_API_URL=http://localhost:8000
```

## 4. Run the System

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 5. Use the System

1. Open http://localhost:5173
2. Upload a PDF document
3. Ask a question
4. Get answer with citations

## Example Questions

After uploading an AI/ML research paper:

- "What is the main contribution of this paper?"
- "What datasets were used in the experiments?"
- "What are the limitations mentioned?"
- "How does this compare to previous work?"

## API Examples

### Upload Document

```bash
curl -X POST -F "file=@paper.pdf" http://localhost:8000/upload
```

Response:
```json
{
  "filename": "paper.pdf",
  "chunks_created": 45,
  "total_tokens": 12500,
  "status": "success"
}
```

### Ask Question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}'
```

Response:
```json
{
  "answer": "The paper focuses on transformer architectures...",
  "citations": [
    {
      "document": "paper.pdf",
      "page": 1,
      "chunk_id": "paper_0"
    }
  ],
  "confidence": 0.85,
  "retrieved_chunks": 5
}
```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Check API key is set
echo $GEMINI_API_KEY

# Check port is available
lsof -i :8000
```

### Frontend can't connect
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check VITE_API_URL in frontend/.env
cat frontend/.env
```

### PDF upload fails
- Ensure file is valid PDF
- Check file size (< 50MB)
- Check backend logs for errors

## Next Steps

1. **Read Architecture:** See ARCHITECTURE.md
2. **Deploy:** See SETUP.md for production deployment
3. **Customize:** Modify prompts in generator.py
4. **Scale:** Add caching, async processing, etc.

## Support

- API Docs: http://localhost:8000/docs
- GitHub Issues: [your-repo-url]/issues
- Documentation: README.md, ARCHITECTURE.md, SETUP.md
