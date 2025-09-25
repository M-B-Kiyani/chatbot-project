# RAG (Retrieval-Augmented Generation) System

This implementation provides a complete RAG system for the chatbot, including document processing, vector database storage, and API endpoints for search and answer generation.

## Features

- **Document Processing**: Automatically processes various file types (txt, md, py, js, html, css, json, yaml, yml)
- **Text Chunking**: Intelligent text chunking with configurable size and overlap
- **Embeddings**: OpenAI text-embedding-3-small for high-quality vector representations
- **Vector Database**: ChromaDB for efficient similarity search
- **Search API**: RESTful endpoints for document search and answer generation
- **Answer Generation**: GPT-3.5-turbo for context-aware answer generation

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

### 3. Add Documents

Place your documents in the `knowledge_base/metalogics_kb/` directory. Supported formats:

- Text files (.txt, .md, .py, .js, .html, .css, .json, .yaml, .yml)
- PDF files (.pdf) - requires additional setup
- DOCX files (.docx) - requires additional setup

### 4. Index the Knowledge Base

```bash
python scripts/index_knowledge_base.py
```

This will:

- Process all documents in the knowledge_base/metalogics_kb/ directory
- Chunk the text into optimal sizes for embedding
- Generate embeddings using OpenAI
- Store everything in the PostgreSQL vector database (pgvector)

### 5. Rebuild Embeddings (Advanced)

If you need to rebuild embeddings from scratch (e.g., after updating documents or changing embedding parameters):

```bash
# Dry run to see what would be done
python knowledge_base/scripts/rebuild_embeddings.py --dry-run

# Actually rebuild embeddings (this will clear existing data)
python knowledge_base/scripts/rebuild_embeddings.py

# Append new documents without clearing existing data
python knowledge_base/scripts/rebuild_embeddings.py --skip-clear
```

**Requirements:**
- Set `OPENAI_API_KEY` environment variable
- PostgreSQL database with pgvector extension enabled

**What it does:**
- Clears existing documents and chunks from the database
- Re-processes all documents in the knowledge_base/ directory
- Generates new embeddings using OpenAI text-embedding-3-small
- Stores everything in the PostgreSQL vector database

## API Endpoints

### Search Documents

```http
GET /api/rag-search?q=your_query&n_results=5
```

**Parameters:**

- `q` (required): Search query
- `n_results` (optional): Number of results to return (1-20, default: 5)

**Response:**

```json
{
  "query": "your_query",
  "documents": [
    {
      "id": "document_chunk_id",
      "content": "chunk content",
      "metadata": {
        "file_name": "document.txt",
        "file_path": "path/to/document.txt",
        "file_type": ".txt",
        "chunk_index": 0,
        "chunk_size": 500,
        "processed_at": "2024-01-01T00:00:00Z"
      },
      "relevance_score": 0.85
    }
  ],
  "total_results": 5,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Generate Answer

```http
POST /api/rag-answer
Content-Type: application/json

{
  "query": "your_question",
  "session_context": "optional_context"
}
```

**Response:**

```json
{
  "query": "your_question",
  "answer": "Generated answer based on retrieved documents",
  "documents_used": [
    {
      "id": "document_chunk_id",
      "content": "chunk content",
      "metadata": {...},
      "relevance_score": 0.85
    }
  ],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Knowledge Base Statistics

```http
GET /api/knowledge
```

**Response:**

```json
{
  "message": "Knowledge base endpoint ready",
  "stats": {
    "total_chunks": 150,
    "collection_name": "knowledge_base",
    "last_updated": "2024-01-01T00:00:00Z"
  }
}
```

### Process Knowledge Base

```http
POST /api/knowledge/process
```

**Response:**

```json
{
  "message": "Knowledge base processing completed",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Configuration

### Document Processor Settings

- **Chunk Size**: 1000 tokens (configurable in `DocumentProcessor.__init__`)
- **Chunk Overlap**: 200 tokens (configurable in `DocumentProcessor.__init__`)
- **Embedding Model**: text-embedding-3-small (configurable in `generate_embeddings`)

### RAG Service Settings

- **Max Search Results**: 5 (configurable in `search_documents`)
- **LLM Model**: gpt-3.5-turbo (configurable in `generate_answer`)
- **Max Tokens**: 1000 (configurable in `generate_answer`)

## File Structure

```
knowledge_base/
├── metalogics_kb/       # Place your documents here
├── embeddings/          # ChromaDB storage (auto-created)
│   └── chroma_db/
├── processors/
│   └── document_processor.py
└── config/
    └── settings.py

backend/
├── services/
│   └── rag_service.py
├── api/
│   └── routes.py
└── requirements.txt

scripts/
└── index_knowledge_base.py
```

## Usage Examples

### Python Client

```python
import requests

# Search for documents
response = requests.get("http://localhost:8000/api/rag-search",
                       params={"q": "chatbot features", "n_results": 3})
results = response.json()
print(f"Found {results['total_results']} documents")

# Generate an answer
response = requests.post("http://localhost:8000/api/rag-answer",
                        json={"query": "What are the main features of this chatbot?"})
answer = response.json()
print(f"Answer: {answer['answer']}")
```

### cURL Examples

```bash
# Search documents
curl "http://localhost:8000/api/rag-search?q=API%20endpoints&n_results=3"

# Generate answer
curl -X POST "http://localhost:8000/api/rag-answer" \
     -H "Content-Type: application/json" \
     -d '{"query": "How do I use the search API?"}'
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Not Set**

   - Ensure `OPENAI_API_KEY` environment variable is set
   - Check that the API key is valid and has sufficient credits

2. **No Documents Found**

   - Verify documents are in the `knowledge_base/metalogics_kb/` directory
   - Check file permissions and encoding

3. **Empty Search Results**

   - Ensure the knowledge base has been indexed
   - Try different search queries
   - Check if documents contain relevant content

4. **ChromaDB Errors**
   - Ensure the `knowledge_base/embeddings/` directory is writable
   - Try deleting the `chroma_db` folder and re-indexing

### Debug Mode

Set the following environment variable for detailed logging:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/knowledge_base:$(pwd)/backend/services"
```

## Performance Considerations

- **Chunk Size**: Larger chunks provide more context but may reduce precision
- **Chunk Overlap**: Higher overlap improves context continuity but increases storage
- **Search Results**: More results provide better context but increase processing time
- **Embedding Model**: text-embedding-3-small is fast and cost-effective

## Security Notes

- Store API keys securely using environment variables
- Consider rate limiting for production use
- Validate and sanitize user inputs
- Monitor API usage and costs
