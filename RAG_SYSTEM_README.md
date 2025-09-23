# RAG (Retrieval-Augmented Generation) System

This document describes the complete RAG system implementation for indexing your knowledge base and providing search and answer generation capabilities.

## Overview

The RAG system consists of several components:

1. **Document Processor** - Reads and chunks documents from your knowledge base
2. **Vector Database** - Stores embeddings using ChromaDB
3. **RAG Service** - Handles search and answer generation
4. **API Endpoints** - REST API for search and answer generation
5. **Indexing Scripts** - Tools to process your knowledge base

## Features

- ✅ Supports multiple file formats: `.txt`, `.md`, `.pdf`, `.docx`, `.py`, `.js`, `.html`, `.css`, `.json`, `.yaml`, `.yml`
- ✅ Intelligent text chunking with configurable size and overlap
- ✅ OpenAI embeddings for semantic search
- ✅ ChromaDB vector database for efficient similarity search
- ✅ Relevance scoring and threshold filtering
- ✅ Answer generation with confidence metrics
- ✅ Unanswered query logging for knowledge base improvements
- ✅ REST API endpoints for integration

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Index Your Knowledge Base

```bash
python scripts/index_knowledge_base_complete.py
```

This will:

- Process all files in the `knowledge_base/` directory
- Chunk content into manageable segments (1000 tokens with 200 token overlap)
- Generate embeddings using OpenAI
- Store embeddings and metadata in ChromaDB

### 4. Start the API Server

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

## Usage

### Document Search

**Endpoint:** `GET /api/rag-search`

**Parameters:**

- `q` (required): Search query
- `n_results` (optional): Number of results (1-20, default: 5)

**Example:**

```bash
curl "http://localhost:8000/api/rag-search?q=What services do you offer?&n_results=3"
```

**Response:**

```json
{
  "query": "What services do you offer?",
  "documents": [
    {
      "text": "We offer web development, mobile app development...",
      "file_name": "Services.md",
      "score": 0.85,
      "file_path": "knowledge_base/Services/Services.md",
      "chunk_index": 0
    }
  ],
  "total_results": 1,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Answer Generation

**Endpoint:** `POST /api/rag-answer`

**Parameters:**

- `query` (required): Your question
- `session_context` (optional): Additional context
- `relevance_threshold` (optional): Minimum relevance score (0.0-1.0, default: 0.7)

**Example:**

```bash
curl -X POST "http://localhost:8000/api/rag-answer" \
  -d "query=How can I contact support?" \
  -d "relevance_threshold=0.6"
```

**Response:**

```json
{
  "query": "How can I contact support?",
  "answer": "You can contact our support team through...",
  "confidence": "high",
  "reason": "success",
  "documents_used": [...],
  "avg_relevance": 0.82,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Knowledge Base Statistics

**Endpoint:** `GET /api/knowledge`

**Response:**

```json
{
  "message": "Knowledge base endpoint ready",
  "stats": {
    "total_chunks": 150,
    "collection_name": "knowledge_base",
    "last_updated": "2024-01-01T12:00:00Z"
  }
}
```

## Configuration

### Chunking Parameters

You can customize chunking in the indexing script:

```bash
python scripts/index_knowledge_base_complete.py \
  --chunk-size 800 \
  --chunk-overlap 150
```

### Relevance Threshold

The system uses a relevance threshold to filter out low-quality matches:

- **High confidence**: Average relevance ≥ 0.8
- **Medium confidence**: Average relevance ≥ 0.6
- **Low confidence**: Average relevance < 0.6

## File Structure

```
knowledge_base/
├── processors/
│   └── document_processor.py    # Document processing and chunking
├── embeddings/
│   └── chroma_db/             # Vector database storage
├── unanswered_queries.json    # Log of unanswered queries
└── [your content files]

backend/
├── services/
│   └── rag_service.py         # RAG service implementation
├── api/
│   └── routes.py             # API endpoints
└── requirements.txt          # Dependencies

scripts/
├── index_knowledge_base_complete.py  # Main indexing script
├── test_rag_system_complete.py      # Comprehensive tests
└── example_rag_usage.py             # Usage examples
```

## Testing

### Run Comprehensive Tests

```bash
python scripts/test_rag_system_complete.py
```

### Test Individual Components

```bash
# Test document processing
python scripts/index_knowledge_base_complete.py --dry-run

# Test RAG service
python scripts/example_rag_usage.py
```

## Troubleshooting

### Common Issues

1. **"No documents found"**

   - Ensure knowledge base is indexed: `python scripts/index_knowledge_base_complete.py`
   - Check that files are in supported formats

2. **"Low relevance" responses**

   - Try rephrasing your query
   - Lower the relevance threshold
   - Check if your knowledge base contains relevant information

3. **API connection errors**

   - Ensure the server is running: `uvicorn backend.main:app --reload`
   - Check the server URL and port

4. **OpenAI API errors**
   - Verify your API key is set correctly
   - Check your OpenAI account has sufficient credits

### Logs

- Unanswered queries are logged to `knowledge_base/unanswered_queries.json`
- Server logs are displayed in the terminal when running `uvicorn`
- Document processing logs are shown during indexing

## Advanced Usage

### Custom Document Processing

You can extend the document processor to handle additional file types by modifying `knowledge_base/processors/document_processor.py`.

### Integration with Other Systems

The API endpoints can be easily integrated with:

- Frontend applications
- Chatbots
- Other microservices
- Webhooks

### Scaling

For production use, consider:

- Using a more robust vector database (Pinecone, Weaviate)
- Implementing caching for frequent queries
- Adding authentication and rate limiting
- Monitoring and logging

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the test scripts for examples
3. Examine the logs for error details
4. Ensure all dependencies are installed correctly
