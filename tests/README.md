# Tests

This directory contains all tests for the chatbot application.

## Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for API endpoints and services
- `conftest.py` - Pytest configuration and shared fixtures

## Running Tests

### Backend Tests
```bash
cd backend
pytest ../tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### All Tests
```bash
# From project root
pytest tests/ -v
```

## Test Categories

### Unit Tests
- `test_chat_service.py` - Chat service functionality
- `test_database.py` - Database models and operations

### Integration Tests
- `test_api_routes.py` - API endpoint testing
- `test_knowledge_base.py` - Knowledge base integration

## Test Configuration

Tests use pytest with the following configuration:
- Async support for FastAPI testing
- Mock objects for external dependencies
- Test fixtures for common test data
- Path configuration for module imports

