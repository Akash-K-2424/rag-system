# RAG System - Testing Guide

Comprehensive testing procedures for the RAG system.

## Unit Testing

### Backend Tests

Create `backend/test_ingest.py`:

```python
import pytest
from ingest import estimate_tokens, chunk_text, extract_page_number

def test_estimate_tokens():
    text = "This is a test sentence with several words."
    tokens = estimate_tokens(text)
    assert tokens > 0
    assert tokens < 20

def test_chunk_text():
    text = "Sentence one. Sentence two. Sentence three. " * 50
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 0
    assert all(len(chunk) > 0 for chunk in chunks)

def test_extract_page_number():
    text = "[PAGE 5] Some content here"
    page = extract_page_number(text)
    assert page == 5
```

Run tests:
```bash
cd backend
pytest test_ingest.py -v
```

## Integration Testing

### API Endpoint Tests

Create `backend/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded"]

def test_chat_empty_query():
    response = client.post("/chat", json={"query": ""})
    assert response.status_code == 400

def test_chat_valid_query():
    response = client.post("/chat", json={"query": "What is AI?"})
    assert response.status_code in [200, 503]  # 503 if no docs uploaded
```

Run tests:
```bash
cd backend
pytest test_api.py -v
```

## Manual Testing

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "vector_db_ready": true,
  "embedding_model_ready": true
}
```

### 2. Document Upload

```bash
# Create a test PDF (or use existing)
curl -X POST -F "file=@test.pdf" http://localhost:8000/upload
```

Expected response:
```json
{
  "filename": "test.pdf",
  "chunks_created": 10,
  "total_tokens": 2500,
  "status": "success"
}
```

### 3. Query Processing

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}'
```

Expected response:
```json
{
  "answer": "The document discusses...",
  "citations": [
    {
      "document": "test.pdf",
      "page": 1,
      "chunk_id": "test_0"
    }
  ],
  "confidence": 0.75,
  "retrieved_chunks": 5
}
```

## Frontend Testing

### 1. Component Rendering

- [ ] Header displays correctly
- [ ] Upload section visible
- [ ] Chat interface loads
- [ ] Footer displays

### 2. Document Upload

- [ ] Click upload button
- [ ] Select PDF file
- [ ] Success message appears
- [ ] Error handling for non-PDF files

### 3. Chat Functionality

- [ ] Type message in input
- [ ] Send button works
- [ ] Message appears in chat
- [ ] Loading state shows
- [ ] Answer appears with citations
- [ ] Citations expandable

### 4. Error Handling

- [ ] Backend unavailable message
- [ ] Network error handling
- [ ] Invalid file type error
- [ ] Empty query error

## Performance Testing

### 1. Document Ingestion Speed

```python
import time
from agent import RAGAgent

agent = RAGAgent()
start = time.time()
result = agent.ingest_and_store("large_document.pdf", "test")
elapsed = time.time() - start
print(f"Ingestion time: {elapsed:.2f}s")
print(f"Chunks per second: {result['chunks_created'] / elapsed:.2f}")
```

### 2. Query Response Time

```python
import time
from agent import RAGAgent

agent = RAGAgent()
queries = [
    "What is the main topic?",
    "What are the key findings?",
    "How does this compare to previous work?"
]

for query in queries:
    start = time.time()
    response = agent.process_query(query)
    elapsed = time.time() - start
    print(f"Query: {query}")
    print(f"Response time: {elapsed:.2f}s")
    print(f"Confidence: {response.confidence:.2f}\n")
```

### 3. Concurrent Requests

```bash
# Test 10 concurrent requests
ab -n 10 -c 10 http://localhost:8000/health

# Test with POST data
ab -n 10 -c 10 -p query.json -T application/json http://localhost:8000/chat
```

## Hallucination Testing

### Test Cases

1. **Question Outside Document Scope**
   - Query: "What is the capital of France?"
   - Expected: "Insufficient information in documents"

2. **Ambiguous Question**
   - Query: "What is it?"
   - Expected: Low confidence or fallback response

3. **Multi-part Question**
   - Query: "What are the methods, results, and conclusions?"
   - Expected: Answer grounded in document

4. **Contradictory Information**
   - Upload conflicting documents
   - Query: "What is X?"
   - Expected: Answer from one document with citation

## Citation Accuracy Testing

### Verification Steps

1. Upload document
2. Ask question
3. Get answer with citations
4. Manually verify:
   - [ ] Document name is correct
   - [ ] Page number is accurate
   - [ ] Content matches citation
   - [ ] No hallucinated citations

## Regression Testing

### Before Each Release

- [ ] All endpoints return correct status codes
- [ ] Error messages are helpful
- [ ] Citations are accurate
- [ ] Confidence scores are reasonable
- [ ] No hallucinations detected
- [ ] Performance is acceptable
- [ ] Frontend loads without errors
- [ ] Upload/chat flow works end-to-end

## Load Testing

### Simulate Multiple Users

```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8000/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/health
```

### Monitor Resources

```bash
# CPU and memory usage
top -p $(pgrep -f "python main.py")

# Disk usage
du -sh chroma_db/

# Network connections
netstat -an | grep 8000
```

## Browser Testing

### Browsers to Test

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Responsive Design

- [ ] Desktop (1920x1080)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

## Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast sufficient
- [ ] Focus indicators visible
- [ ] Form labels present

## Security Testing

### Input Validation

- [ ] SQL injection attempts blocked
- [ ] XSS attempts blocked
- [ ] Large file uploads rejected
- [ ] Invalid file types rejected

### API Security

- [ ] CORS properly configured
- [ ] API keys not exposed
- [ ] Rate limiting works
- [ ] Error messages don't leak info

## Deployment Testing

### Before Production

- [ ] Backend builds successfully
- [ ] Frontend builds successfully
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] Health check passes
- [ ] Sample document uploads
- [ ] Sample queries work
- [ ] Logs are readable
- [ ] Monitoring is active

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm run build
```

## Test Coverage Goals

- Backend: 80%+ coverage
- Frontend: 70%+ coverage
- Critical paths: 100% coverage

## Reporting Issues

When reporting test failures:

1. Include error message
2. Provide reproduction steps
3. Attach logs
4. Specify environment (OS, Python version, Node version)
5. Include screenshots if UI-related
