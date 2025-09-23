# AI Chatbot Project Makefile

.PHONY: help install dev test clean build rag-index rag-test

# Default target
help:
	@echo "AI Chatbot Project - Available Commands:"
	@echo ""
	@echo "  make install     - Install all dependencies (Node.js + Python)"
	@echo "  make dev         - Start both backend and frontend in development mode"
	@echo "  make dev-backend - Start only the backend server"
	@echo "  make dev-frontend- Start only the frontend server"
	@echo "  make test        - Run all tests (backend + frontend)"
	@echo "  make test-backend- Run backend tests only"
	@echo "  make test-frontend- Run frontend tests only"
	@echo "  make build       - Build frontend for production"
	@echo "  make clean       - Clean build artifacts and dependencies"
	@echo "  make setup       - Complete project setup (install + env setup guide)"
	@echo ""
	@echo "RAG System Commands:"
	@echo "  make rag-index   - Index knowledge base documents"
	@echo "  make rag-test    - Test RAG system functionality"
	@echo "  make rag-clean   - Clean RAG embeddings and vector DB"
	@echo ""
	@echo "Metalogics Knowledge Base:"
	@echo "  make metalogics-index - Index Metalogics knowledge base with analysis"
	@echo "  make metalogics-test  - Test Metalogics knowledge base specifically"

# Install all dependencies
install:
	@echo "Installing Node.js dependencies..."
	npm install
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing Python dependencies..."
	cd backend && pip install -r requirements.txt

# Development commands
dev:
	@echo "Starting both backend and frontend servers..."
	npm run dev

dev-backend:
	@echo "Starting backend server..."
	cd backend && python main.py

dev-frontend:
	@echo "Starting frontend server..."
	cd frontend && npm run dev

# Testing commands
test:
	@echo "Running all tests..."
	npm run test

test-backend:
	@echo "Running backend tests..."
	cd backend && pytest ../tests/ -v

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

# Build commands
build:
	@echo "Building frontend for production..."
	cd frontend && npm run build

# Cleanup commands
clean:
	@echo "Cleaning build artifacts..."
	rm -rf frontend/dist
	rm -rf frontend/node_modules
	rm -rf node_modules
	rm -rf backend/__pycache__
	rm -rf backend/*.pyc
	rm -rf tests/__pycache__
	rm -rf tests/*.pyc
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Complete setup
setup: install
	@echo ""
	@echo "✅ Dependencies installed successfully!"
	@echo ""
	@echo "📝 Next steps:"
	@echo "  1. Create a .env file in the project root"
	@echo "  2. Add the required environment variables (see README.md)"
	@echo "  3. Run 'make dev' to start the development servers"
	@echo ""
	@echo "🔧 Required environment variables:"
	@echo "  - GOOGLE_CLIENT_ID"
	@echo "  - GOOGLE_CLIENT_SECRET"
	@echo "  - HUBSPOT_CLIENT_ID / HUBSPOT_CLIENT_SECRET / HUBSPOT_API_KEY"
	@echo "  - VECTOR_DB_KEY"
	@echo "  - OPENAI_API_KEY (for RAG system)"
	@echo "  - DATABASE_URL"

# RAG System commands
rag-index:
	@echo "Indexing knowledge base documents..."
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "❌ OPENAI_API_KEY environment variable not set"; \
		echo "Please set your OpenAI API key:"; \
		echo "export OPENAI_API_KEY='your-api-key-here'"; \
		exit 1; \
	fi
	python scripts/index_knowledge_base.py

rag-test:
	@echo "Testing RAG system..."
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "❌ OPENAI_API_KEY environment variable not set"; \
		echo "Please set your OpenAI API key:"; \
		echo "export OPENAI_API_KEY='your-api-key-here'"; \
		exit 1; \
	fi
	python scripts/test_rag_system.py

rag-clean:
	@echo "Cleaning RAG embeddings and vector DB..."
	rm -rf knowledge_base/embeddings/chroma_db
	rm -rf knowledge_base/embeddings/*.json
	@echo "✅ RAG data cleaned"

# Metalogics Knowledge Base commands
metalogics-index:
	@echo "Indexing Metalogics knowledge base with analysis..."
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "❌ OPENAI_API_KEY environment variable not set"; \
		echo "Please set your OpenAI API key:"; \
		echo "export OPENAI_API_KEY='your-api-key-here'"; \
		exit 1; \
	fi
	python scripts/index_metalogics_kb.py

metalogics-test:
	@echo "Testing Metalogics knowledge base..."
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "❌ OPENAI_API_KEY environment variable not set"; \
		echo "Please set your OpenAI API key:"; \
		echo "export OPENAI_API_KEY='your-api-key-here'"; \
		exit 1; \
	fi
	python scripts/test_metalogics_kb.py

