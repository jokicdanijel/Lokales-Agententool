# 🔌 Research Paper Manager - API Reference

Complete API documentation for the Research Paper Management System.

---

## 🚀 Base URL

```
http://localhost:5002/api
```

---

## 📊 Status Endpoints

### Health Check

```
GET /health
```

**Response (200):**

```json
{
  "status": "healthy",
  "service": "Research Paper Manager",
  "version": "0.1.0",
  "timestamp": "2025-11-25T10:30:00"
}
```

### Status Details

```
GET /api/status
```

**Response (200):**

```json
{
  "status": "operational",
  "database": {
    "papers": 150,
    "collections": 8,
    "tags": 45
  },
  "features": {
    "arxiv_integration": true,
    "ai_features": true,
    "search": true,
    "tagging": true
  }
}
```

---

## 📚 Paper Endpoints

### List Papers

```
GET /api/papers?page=1&per_page=20
```

**Parameters:**

- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20)

**Response (200):**

```json
{
  "data": [
    {
      "id": 1,
      "arxiv_id": "2505.09388",
      "title": "Qwen3 Technical Report",
      "authors": "[\"Qwen Team\"]",
      "abstract": "...",
      "category": "cs.CL",
      "url": "https://arxiv.org/abs/2505.09388",
      "pdf_url": "https://arxiv.org/pdf/2505.09388.pdf",
      "published_date": "2025-05-14",
      "summary": "AI-generated summary...",
      "keywords": "[\"LLM\", \"Coding\"]",
      "created_at": "2025-11-25T10:00:00",
      "updated_at": "2025-11-25T10:00:00",
      "metadata": {}
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8
}
```

### Get Single Paper

```
GET /api/papers/<paper_id>
```

**Response (200):**

```json
{
  "id": 1,
  "arxiv_id": "2505.09388",
  "title": "Qwen3 Technical Report",
  "authors": "[\"Qwen Team\"]",
  "abstract": "...",
  "category": "cs.CL",
  "tags": ["AI", "LLM", "Coding"],
  "metadata": {}
}
```

**Error (404):**

```json
{ "error": "Paper not found" }
```

### Create Paper

```
POST /api/papers
Content-Type: application/json

{
  "arxiv_id": "2505.09388",
  "title": "Qwen3 Technical Report",
  "authors": "[\"Qwen Team\"]",
  "abstract": "Large language model for coding...",
  "category": "cs.CL",
  "url": "https://arxiv.org/abs/2505.09388",
  "pdf_url": "https://arxiv.org/pdf/2505.09388.pdf",
  "published_date": "2025-05-14",
  "summary": "Optional AI summary",
  "keywords": "[\"LLM\"]",
  "metadata": {}
}
```

**Response (201):**

```json
{
  "id": 1,
  "arxiv_id": "2505.09388",
  "title": "Qwen3 Technical Report",
  ...
}
```

### Update Paper

```
PUT /api/papers/<paper_id>
Content-Type: application/json

{
  "title": "Updated Title",
  "abstract": "Updated abstract...",
  "summary": "New AI summary",
  "category": "cs.AI"
}
```

**Response (200):**

```json
{
  "id": 1,
  "title": "Updated Title",
  ...
}
```

### Delete Paper

```
DELETE /api/papers/<paper_id>
```

**Response (200):**

```json
{ "message": "Paper deleted" }
```

---

## 🔍 Search Endpoints

### Local Search

```
GET /api/search?q=machine%20learning&category=cs.AI
```

**Parameters:**

- `q` (string): Search query
- `category` (string, optional): Filter by category

**Response (200):**

```json
{
  "query": "machine learning",
  "count": 25,
  "papers": [...]
}
```

### arXiv Search

```
GET /api/arxiv/search?q=neural%20networks&category=cs.AI&max_results=50
```

**Parameters:**

- `q` (string): Search query
- `category` (string, optional): arXiv category
- `max_results` (int, optional): Max results (default: 50)

**Response (200):**

```json
{
  "query": "neural networks",
  "count": 50,
  "papers": [
    {
      "arxiv_id": "2505.09388",
      "title": "...",
      "authors": [...],
      "abstract": "...",
      ...
    }
  ]
}
```

---

## 🌐 arXiv Integration Endpoints

### Fetch Paper from arXiv

```
POST /api/arxiv/fetch
Content-Type: application/json

{
  "arxiv_id": "2505.09388"
}
```

**Response (201):** Paper imported successfully

```json
{
  "id": 1,
  "arxiv_id": "2505.09388",
  ...
}
```

**Response (200):** Paper already exists

```json
{
  "message": "Paper already imported",
  "paper": {...}
}
```

**Error (404):**

```json
{ "error": "Paper not found on arXiv" }
```

### Parse arXiv ID

```
POST /api/arxiv/parse
Content-Type: application/json

{
  "text": "Check out this paper: https://arxiv.org/abs/2505.09388"
}
```

**Response (200):**

```json
{ "arxiv_id": "2505.09388" }
```

**Error (404):**

```json
{ "error": "No valid arXiv ID found" }
```

---

## 🏷️ Tag Endpoints

### Add Tag to Paper

```
POST /api/papers/<paper_id>/tags
Content-Type: application/json

{
  "tag_name": "machine-learning"
}
```

**Response (201):**

```json
{
  "id": 42,
  "paper_id": 1,
  "tag_name": "machine-learning",
  "created_at": "2025-11-25T10:00:00"
}
```

**Response (200):** Tag already exists

```json
{ "message": "Tag already exists" }
```

---

## 📁 Collection Endpoints

### List Collections

```
GET /api/collections
```

**Response (200):**

```json
[
  {
    "id": 1,
    "name": "Qwen Models",
    "description": "Papers about Qwen AI models",
    "paper_count": 5,
    "created_at": "2025-11-25T10:00:00",
    "updated_at": "2025-11-25T10:00:00"
  }
]
```

### Create Collection

```
POST /api/collections
Content-Type: application/json

{
  "name": "Qwen Models",
  "description": "Papers about Qwen AI models"
}
```

**Response (201):**

```json
{
  "id": 1,
  "name": "Qwen Models",
  "description": "Papers about Qwen AI models",
  "paper_count": 0,
  "created_at": "2025-11-25T10:00:00",
  "updated_at": "2025-11-25T10:00:00"
}
```

---

## 🛠️ Useful cURL Examples

### Search for Papers

```bash
curl "http://localhost:5002/api/search?q=machine%20learning" \
  -H "Content-Type: application/json"
```

### Import Paper from arXiv

```bash
curl -X POST "http://localhost:5002/api/arxiv/fetch" \
  -H "Content-Type: application/json" \
  -d '{"arxiv_id": "2505.09388"}'
```

### Add Tag to Paper

```bash
curl -X POST "http://localhost:5002/api/papers/1/tags" \
  -H "Content-Type: application/json" \
  -d '{"tag_name": "important"}'
```

### Create Collection

```bash
curl -X POST "http://localhost:5002/api/collections" \
  -H "Content-Type: application/json" \
  -d '{"name": "ML Papers", "description": "Machine Learning Research"}'
```

---

## 📋 HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

---

## 🔐 Error Handling

All errors follow this format:

```json
{
  "error": "Error message"
}
```

---

**Last Updated:** 2025-11-25
**Version:** 1.0.0
