# RAG System - Setup Guide

Complete setup instructions for running the RAG system locally and deploying to production.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- Google Gemini API key (get it at https://makersuite.google.com/app/apikey)

## Local Development Setup

### 1. Clone and Navigate

```bash
git clone <your-repo-url>
cd rag-system
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your-key-here
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# .env should have:
# VITE_API_URL=http://localhost:8000
```

### 4. Run Locally

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

Backend will start on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend will start on `http://localhost:5173`

### 5. Test the System

1. Open http://localhost:5173 in your browser
2. Upload a PDF document
3. Ask a question about the document
4. Verify you get an answer with citations

## API Testing

### Upload Document

```bash
curl -X POST -F "file=@sample.pdf" http://localhost:8000/upload
```

### Ask Question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Production Deployment

### Deploy Backend to Render

1. Push code to GitHub
2. Go to https://render.com
3. Create new Web Service
4. Connect your GitHub repository
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Environment Variables:**
     - `GEMINI_API_KEY`: Your API key
     - `BACKEND_HOST`: 0.0.0.0
     - `BACKEND_PORT`: 8000
6. Deploy

Note the backend URL (e.g., `https://rag-system-backend.onrender.com`)

### Deploy Frontend to Vercel

1. Push code to GitHub
2. Go to https://vercel.com
3. Import your project
4. Configure:
   - **Framework:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Environment Variables:**
     - `VITE_API_URL`: Your Render backend URL
5. Deploy

### Update Frontend Environment

After deploying backend, update frontend `.env.production`:

```
VITE_API_URL=https://your-backend.onrender.com
```

Then redeploy frontend on Vercel.

## Docker Deployment

### Build Docker Image

```bash
cd backend
docker build -t rag-system-backend .
```

### Run Docker Container

```bash
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your-key \
  -e BACKEND_HOST=0.0.0.0 \
  -e BACKEND_PORT=8000 \
  rag-system-backend
```

## Troubleshooting

### Backend won't start

- Check Python version: `python --version` (should be 3.10+)
- Check GEMINI_API_KEY is set: `echo $GEMINI_API_KEY`
- Check port 8000 is available: `lsof -i :8000`

### Frontend can't connect to backend

- Verify backend is running: `curl http://localhost:8000/health`
- Check VITE_API_URL in frontend .env
- Check browser console for CORS errors

### PDF upload fails

- Ensure file is valid PDF
- Check file size (should be < 50MB)
- Check backend logs for errors

### Slow responses

- Check internet connection
- Verify Gemini API quota
- Check ChromaDB is persisting (chroma_db/ folder exists)

## Performance Optimization

### For Production

1. **Caching:** Implement Redis for embedding cache
2. **Async Processing:** Use Celery for document ingestion
3. **Database:** Use PostgreSQL instead of ChromaDB for scale
4. **CDN:** Use Cloudflare for frontend
5. **Monitoring:** Add Sentry for error tracking

### Configuration Tuning

Edit backend `.env`:

```
# Larger chunks for better context
CHUNK_SIZE=600
CHUNK_OVERLAP=100

# More retrieval for better coverage
TOP_K_RETRIEVAL=10

# Lower threshold for more answers
CONFIDENCE_THRESHOLD=0.3
```

## Support

For issues:
1. Check logs: `tail -f backend/main.py`
2. Check browser console (F12)
3. Verify API endpoints: `curl http://localhost:8000/docs`
4. Open GitHub issue with error details
