# RAG System - Troubleshooting Guide

## Frontend Connection Error

**Error:** "Backend Connection Error - Unable to connect to the backend"

### Solutions

#### 1. Verify Backend is Running
```bash
# Check if backend is responding
curl http://localhost:8000/health

# Expected response:
# {"status":"degraded","vector_db_ready":false,"embedding_model_ready":false}
```

#### 2. Check Backend Port
```bash
# Verify port 8000 is in use
lsof -i :8000

# If not running, start backend:
cd backend
./venv/bin/python main.py
```

#### 3. Restart Frontend
The frontend may need to be restarted to reconnect:
```bash
# Stop frontend (Ctrl+C)
# Then restart:
cd frontend
npm run dev
```

#### 4. Clear Browser Cache
- Press Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
- Clear cache and cookies
- Refresh the page

#### 5. Check CORS Configuration
The backend has CORS enabled for all origins. If still having issues:
- Check browser console (F12) for specific error messages
- Look for "Access-Control-Allow-Origin" headers in network tab

#### 6. Verify API Endpoints
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# Test upload endpoint
curl -X POST -F "file=@test.pdf" http://localhost:8000/upload
```

## Backend Issues

### ModuleNotFoundError: No module named 'PyPDF2'

**Cause:** Heavy ML dependencies not installed

**Solution:** The system runs in demo mode without these dependencies. To enable full RAG:

```bash
cd backend
./venv/bin/pip install PyPDF2 chromadb sentence-transformers google-generativeai numpy
```

### Port Already in Use

**Error:** "Address already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
BACKEND_PORT=8001 python main.py
```

### Uvicorn Not Found

**Error:** "sh: uvicorn: command not found"

**Solution:**
```bash
cd backend
./venv/bin/pip install uvicorn fastapi
```

## Frontend Issues

### npm: command not found

**Solution:** Install Node.js from https://nodejs.org/

### Vite: command not found

**Solution:**
```bash
cd frontend
npm install
npm run dev
```

### Port 5173 Already in Use

**Solution:**
```bash
# Find process using port 5173
lsof -i :5173

# Kill the process
kill -9 <PID>

# Or use different port
npm run dev -- --port 5174
```

## API Issues

### 404 Not Found

**Cause:** Endpoint doesn't exist or wrong URL

**Solution:** Check endpoint names:
- `/health` - Health check
- `/upload` - Document upload
- `/chat` - Query processing
- `/docs` - API documentation

### 500 Internal Server Error

**Cause:** Backend error

**Solution:**
1. Check backend logs for error message
2. Verify all dependencies are installed
3. Check environment variables (GEMINI_API_KEY)
4. Restart backend

### CORS Error

**Error:** "Access to XMLHttpRequest blocked by CORS policy"

**Solution:** Backend CORS is configured. If still having issues:
1. Clear browser cache
2. Restart both frontend and backend
3. Check browser console for specific error

## Demo Mode

The system runs in **demo mode** when ML dependencies aren't installed.

**Demo Mode Features:**
- ✓ Full UI functionality
- ✓ Simulated document upload
- ✓ Simulated chat responses
- ✓ Citation display
- ✓ All components interactive

**To Enable Full RAG:**
1. Install dependencies: `pip install -r requirements.txt`
2. Set GEMINI_API_KEY: `export GEMINI_API_KEY=your-key`
3. Restart backend

## Performance Issues

### Slow Response Time

**Causes:**
- Network latency
- Backend processing
- API rate limiting

**Solutions:**
1. Check internet connection
2. Monitor backend logs
3. Check Gemini API quota
4. Increase timeout in frontend/src/api.js

### High Memory Usage

**Solution:**
1. Restart backend
2. Clear browser cache
3. Close other applications

## Browser Compatibility

**Tested Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**If having issues:**
1. Try different browser
2. Clear cache and cookies
3. Disable browser extensions
4. Check browser console (F12)

## Getting Help

1. **Check Logs:**
   - Backend: Look at terminal output
   - Frontend: Check browser console (F12)

2. **Test API Directly:**
   ```bash
   curl http://localhost:8000/docs
   ```

3. **Review Documentation:**
   - README.md - Overview
   - ARCHITECTURE.md - Technical details
   - SETUP.md - Setup instructions

4. **Common Issues:**
   - Restart both servers
   - Clear browser cache
   - Check port availability
   - Verify dependencies installed

## Quick Restart

If everything is broken, do a clean restart:

```bash
# Stop all processes (Ctrl+C in terminals)

# Backend
cd backend
./venv/bin/python main.py

# Frontend (new terminal)
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.
