# Metalogics AI Chatbot

A production-ready smart chatbot for metalogics.io with RAG capabilities, Google Calendar integration, HubSpot CRM integration, and intelligent booking management. Built with FastAPI backend, React frontend, and PostgreSQL with pgvector for vector storage.

## 🏗️ Project Structure

```
Chatbot/
├── backend/                 # FastAPI backend server
│   ├── api/                # API routes and endpoints
│   │   ├── routes.py       # RAG and general API endpoints
│   │   ├── chat.py         # Chat processing endpoint
│   │   ├── calender.py     # Calendar booking endpoints
│   │   ├── hubspot.py      # HubSpot CRM integration
│   │   ├── intent.py       # Intent detection and upsell
│   │   └── health.py       # Health check endpoint
│   ├── services/           # Business logic services
│   ├── db/                 # Database models and connections
│   ├── main.py            # Backend entry point with FastAPI app
│   └── requirements.txt   # Python dependencies
├── frontend/               # React frontend application
│   ├── src/               # React source code
│   ├── components/        # Reusable React components
│   ├── package.json       # Node.js dependencies
│   └── vite.config.js     # Vite configuration
├── knowledge_base/         # RAG knowledge base documents
│   ├── documents/         # Raw documents for processing
│   ├── embeddings/        # Processed embeddings (generated)
│   ├── processors/        # Document processing scripts
│   └── scripts/           # Knowledge base management scripts
├── scripts/               # Utility scripts
├── docker/                # Docker configuration
├── pgvector/              # pgvector extension source
├── environment.yml        # Conda environment configuration
├── docker-compose.yml     # Multi-container Docker setup
└── .env                   # Environment variables (create from .env.example)
```

## ✨ Key Features

### 🤖 Intelligent Chat with RAG

- **Retrieval-Augmented Generation**: Answers based on Metalogics knowledge base
- **Confidence Scoring**: Provides fallback responses for low-confidence answers
- **Context-Aware Responses**: Maintains conversation context

### 📅 Smart Calendar Integration

- **OAuth Flow**: Secure Google Calendar authentication
- **Free/Busy Checks**: Real-time availability checking
- **Intelligent Booking Rules**:
  - Max 2 bookings of 15 minutes within any rolling 1-hour window
  - Max 2 bookings of 30 minutes within any rolling 2-hour window
  - Max 2 bookings of 60 minutes within any rolling 3-hour window
- **Automatic Reminders**: Email and popup notifications for events

### 🏢 HubSpot CRM Integration

- **Contact Management**: Automatic upsert of leads with name, email, company
- **Timeline Notes**: Links conversation history to HubSpot contacts
- **Session Tracking**: Associates leads with their chat sessions

### 💰 Dynamic Pricing

- **Structured Templates**: Service pricing with duration options and breakdowns
- **Upsell Logic**: Proactive suggestions (Web Development → SEO + Graphic Design)

### 📊 Data Persistence

- **Session Management**: Complete chat history storage
- **Lead Tracking**: Links leads to conversation metadata
- **Webhook Support**: APIs for external system integration

## 🔌 API Endpoints

| Endpoint                 | Method | Description                          |
| ------------------------ | ------ | ------------------------------------ |
| `/api/chat`              | POST   | Main chat endpoint with RAG          |
| `/api/rag-search`        | GET    | Search knowledge base documents      |
| `/api/rag-answer`        | POST   | Generate RAG answer                  |
| `/api/knowledge`         | GET    | Get knowledge base statistics        |
| `/api/knowledge/process` | POST   | Process knowledge base documents     |
| `/api/pricing`           | GET    | Get service pricing information      |
| `/api/intent-hint`       | POST   | Get upsell suggestions by intent     |
| `/api/log-message`       | POST   | Log chat messages to database        |
| `/api/schedule-check`    | POST   | Check booking availability           |
| `/api/create-booking`    | POST   | Create calendar booking              |
| `/api/calendar/auth`     | GET    | Initiate Google Calendar OAuth       |
| `/api/calendar/callback` | GET    | Handle Google OAuth callback         |
| `/api/calendar/freebusy` | GET    | Get calendar free/busy info          |
| `/api/calendar/create`   | POST   | Create calendar event                |
| `/api/upsert-hubspot`    | POST   | Manage HubSpot contacts              |
| `/api/health`            | GET    | Health check endpoint                |
| `/`                      | GET    | Root endpoint with API info          |
| `/docs`                  | GET    | FastAPI interactive documentation    |

## 🚀 Setup

### Prerequisites

- Python 3.11 (Note: Python 3.13+ may have SQLAlchemy compatibility issues)
- Node.js 16+
- npm or yarn
- PostgreSQL with pgvector extension (for vector storage)
- [Miniconda or Anaconda](https://docs.conda.io/projects/miniconda/en/latest/) (recommended for environment management)
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) (for containerized deployment)

### 1. Install Dependencies

#### Option 1: Using Conda (Recommended)

Conda provides isolated environments, making it easier to manage dependencies and save system memory.

```bash
# Create conda environment from the provided environment.yml
conda env create -f environment.yml

# Activate the environment
conda activate chatbot

# Install frontend dependencies
cd frontend
npm install
cd ..
```

#### Option 2: Using pip (Traditional)

If you prefer not to use conda, you can install dependencies directly with pip.

#### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Frontend Dependencies

```bash
cd frontend
npm install
```

#### Option 3: Using Docker (Recommended for Production)

Docker provides complete containerization with all dependencies pre-configured.

1. **Install Docker and Docker Compose** (see Prerequisites)

2. **Clone the repository and navigate to the project directory**

3. **Create environment file**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual API keys and configuration.

4. **Start all services**:
   ```bash
   docker-compose up --build
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

#### Docker Services

- **postgres**: PostgreSQL database with pgvector extension for vector embeddings
- **backend**: FastAPI application server with RAG, calendar, and HubSpot integrations
- **frontend**: React application served by nginx on port 3000

#### Useful Docker Commands

```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Run tests in Docker
docker-compose exec backend pytest tests/ -v
```

### 2. Environment Configuration

Create a `.env` file in the project root with the following required keys:

```env
# Google Calendar Integration (OAuth flow for calendar access)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/callback

# HubSpot CRM Integration (contact management and timeline notes)
HUBSPOT_CLIENT_ID=your_hubspot_client_id
HUBSPOT_CLIENT_SECRET=your_hubspot_client_secret
HUBSPOT_DEVELOPER_API_KEY=your_hubspot_developer_api_key
HUBSPOT_ACCESS_TOKEN=your_hubspot_access_token

# OpenAI Integration (for RAG and chat responses)
OPENAI_API_KEY=your_openai_api_key

# Vector Database (pgvector with PostgreSQL)
# No additional configuration needed - uses local PostgreSQL with pgvector

# Database (PostgreSQL with pgvector for production, SQLite for simple testing)
DATABASE_URL=postgresql://postgres:bilal%40123@localhost:5432/chatbotdb
# For SQLite (simpler setup): DATABASE_URL=sqlite:///./test_booking.db

# Application Settings
APP_BASE_URL=http://localhost:8000
SESSIONS_API_URL=http://localhost:8000  # Optional: for fetching session data
PORT=8000
```

#### Required Environment Variables

| Variable                    | Description                                | Required |
| --------------------------- | ------------------------------------------ | -------- |
| `GOOGLE_CLIENT_ID`          | Google OAuth client ID for Calendar access | ✅       |
| `GOOGLE_CLIENT_SECRET`      | Google OAuth client secret                 | ✅       |
| `GOOGLE_REDIRECT_URI`       | Google OAuth redirect URI                  | ✅       |
| `HUBSPOT_CLIENT_ID`         | HubSpot OAuth client ID                    | ✅       |
| `HUBSPOT_CLIENT_SECRET`     | HubSpot OAuth client secret                | ✅       |
| `HUBSPOT_DEVELOPER_API_KEY` | HubSpot developer API key                  | ✅       |
| `HUBSPOT_ACCESS_TOKEN`      | HubSpot access token                       | ✅       |
| `OPENAI_API_KEY`            | OpenAI API key for AI responses            | ✅       |
| `DATABASE_URL`              | Database connection URL                    | ✅       |
| `APP_BASE_URL`              | Base URL for the application               | ✅       |
| `PORT`                      | Application port (default: 8000)           | ✅       |
| `SECRET_KEY`                | Application secret key                     | ✅       |

### Google OAuth Setup

#### Development Setup
- [ ] Go to [Google Cloud Console](https://console.cloud.google.com/)
- [ ] Create/select a project
- [ ] Enable Google Calendar API
- [ ] Create OAuth 2.0 credentials
- [ ] Add authorized redirect URI: `http://localhost:8000/api/calendar/callback`
- [ ] Set environment variables:
  - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
  - `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
  - `GOOGLE_REDIRECT_URI`: `http://localhost:8000/api/calendar/callback`

#### Production Setup
- [ ] In Google Cloud Console, add additional authorized redirect URI: `https://yourdomain.com/api/calendar/callback`
- [ ] Update `GOOGLE_REDIRECT_URI` in your production `.env` file to: `https://yourdomain.com/api/calendar/callback`
- [ ] Ensure your production domain is properly configured for HTTPS

### 3. Run Development Servers

#### Start Backend Server

If using conda:

```bash
# Activate conda environment (if not already activated)
conda activate chatbot

# Run the backend server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

If using pip environment:

```bash
# Run the backend server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will run on `http://localhost:8000`
API documentation available at `http://localhost:8000/docs`

#### Start Frontend Server

```bash
cd frontend
npm run dev
```

The frontend will run on `http://localhost:3000`

#### Start Both Servers (from project root)

If using conda:

```bash
# Terminal 1 - Backend
conda activate chatbot
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

If using pip:

```bash
# Terminal 1 - Backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### 4. Testing

#### Backend Tests

If using conda:

```bash
conda activate chatbot-backend
cd backend
pytest ../tests/ -v
```

If using pip:

```bash
cd backend
pytest ../tests/ -v
```

#### Frontend Tests

```bash
cd frontend
npm test
```

#### Booking Rules Testing

Test the intelligent booking rules with the provided test script:

```bash
# Test booking scenarios
python scripts/test_booking_scenarios.py

# Run unit tests for calendar service
pytest tests/unit/test_calendar_service.py -v

# Run integration tests with mocked services
pytest tests/integration/test_booking_integration.py -v
```

The booking rules enforce:

- **15-minute bookings**: Max 2 per rolling 1-hour window
- **30-minute bookings**: Max 2 per rolling 2-hour window
- **60-minute bookings**: Max 2 per rolling 3-hour window

#### Run All Tests

If using conda:

```bash
# From project root
conda activate chatbot-backend
pytest tests/ -v
```

If using pip:

```bash
# From project root
pytest tests/ -v
```

## 🛠️ Development

### Backend Development

The backend is built with FastAPI and includes:

- **API Routes** (`backend/api/`): RESTful endpoints for chat functionality
- **Services** (`backend/services/`): Business logic for chat processing
- **Database** (`backend/db/`): SQLAlchemy models and database connections
- **Authentication**: Google OAuth integration
- **Integrations**: HubSpot CRM integration

### Frontend Development

The frontend is built with React and Vite:

- **Modern UI**: Clean, responsive chat interface
- **Real-time Chat**: Live messaging with the backend
- **Authentication**: Google OAuth integration
- **Responsive Design**: Mobile-friendly interface

### Knowledge Base

The RAG system includes:

- **Document Processing**: Support for PDF, DOCX, TXT, HTML files
- **Embedding Generation**: OpenAI embeddings for semantic search
- **Vector Storage**: PostgreSQL with pgvector extension for local vector storage
- **Retrieval**: Context-aware document retrieval with relevance scoring

## 📁 Key Files

### Backend

- `backend/main.py` - Backend entry point and initialization
- `backend/api/routes.py` - API endpoint definitions
- `backend/services/chat_service.py` - Chat processing logic
- `backend/db/models.py` - Database models

### Frontend

- `frontend/src/App.jsx` - Main React component
- `frontend/src/main.jsx` - React entry point
- `frontend/package.json` - Dependencies and scripts

### Knowledge Base

- `knowledge_base/processors/document_processor.py` - Document processing
- `knowledge_base/config/settings.py` - Configuration management

## 🔧 Available Scripts

### Backend

```bash
python main.py              # Run backend server
pytest tests/ -v           # Run tests
```

### Frontend

```bash
npm run dev                # Start development server
npm run build              # Build for production
npm run preview            # Preview production build
npm test                   # Run tests
npm run lint               # Run linter
```

## 🚀 Deployment

### Prerequisites for Deployment

- Python 3.8+
- Node.js 16+
- Production database (PostgreSQL with pgvector extension required)
- OpenAI API access
- Google Cloud Console project for OAuth
- HubSpot developer account
- pgvector extension for vector storage

### Environment Variables Setup

Create a `.env` file in the project root with the following required variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/chatbot_db

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/calendar/callback

# HubSpot
HUBSPOT_DEVELOPER_API_KEY=your_hubspot_developer_api_key
HUBSPOT_CLIENT_ID=your_hubspot_client_id
HUBSPOT_CLIENT_SECRET=your_hubspot_client_secret
HUBSPOT_REDIRECT_URI=https://yourdomain.com/hubspot/callback

# Application
PORT=8000
KNOWLEDGE_BASE_PATH=./knowledge_base
APP_BASE_URL=https://yourdomain.com
SESSIONS_API_URL=https://yourdomain.com/api  # Optional: for session data fetching
```

### Database Setup and Migrations

1. **Set up database connection**:

   Create a PostgreSQL database and update `DATABASE_URL`

2. **Run database migrations**:
   ```bash
   cd backend
   python -c "from db.database import create_tables; create_tables()"
   ```

### OAuth Redirect URI Setup

#### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `https://yourdomain.com/api/calendar/callback` (production)
   - `http://localhost:8000/api/calendar/callback` (development)

#### HubSpot OAuth

1. Go to [HubSpot Developer](https://developers.hubspot.com/)
2. Create a private app
3. Configure scopes (see below)
4. Set redirect URI: `https://yourdomain.com/hubspot/callback`

### HubSpot Scopes

The application requires the following HubSpot scopes for the private app:

- `crm.objects.contacts.read` - Read contacts
- `crm.objects.contacts.write` - Create/update contacts
- `crm.objects.notes.read` - Read notes
- `crm.objects.notes.write` - Create notes
- `crm.objects.companies.read` - Read companies (optional)

### Vector Database Setup

The application uses PostgreSQL with pgvector extension for vector storage. The database is automatically initialized when the application starts.

1. **Ensure PostgreSQL is running with pgvector**:

    For Docker setup:
    ```bash
    docker-compose up postgres -d
    ```

    For local PostgreSQL, ensure pgvector extension is installed.

2. **Process knowledge base documents**:

    ```bash
    # From project root
    python -c "from backend.services.rag_service import RAGService; rag = RAGService(); rag.process_knowledge_base()"
    ```

3. **Verify vector database**:
    ```bash
    curl http://localhost:8000/api/knowledge
    ```

### Backend Deployment

1. **Install dependencies**:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set environment variables** (see above)

3. **Run database setup** (see Database Setup section)

4. **Process knowledge base** (see Vector Database Setup)

5. **Start the server**:

    ```bash
    # Development
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

    # Production with uvicorn
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

    # Production with gunicorn
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
    ```

### Frontend Deployment

1. **Install dependencies**:

   ```bash
   cd frontend
   npm install
   ```

2. **Build for production**:

   ```bash
   npm run build
   ```

3. **Configure environment variables** (if needed):

   ```bash
   # Create .env.production file
   VITE_API_BASE_URL=https://your-api-domain.com
   ```

4. **Serve static files**:

   ```bash
   # Using nginx
   server {
       listen 80;
       server_name yourdomain.com;
       root /path/to/frontend/dist;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### API Testing Examples

Test the deployed endpoints with these curl commands:

#### Chat Endpoint

```bash
curl -X POST http://yourdomain.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What services do you offer?", "session_id": "test-session"}'
```

#### RAG Search

```bash
curl "http://yourdomain.com/rag-search?q=web%20development&n_results=3"
```

#### Knowledge Base Stats

```bash
curl http://localhost:8000/api/knowledge
```

#### Process Knowledge Base

```bash
curl -X POST http://localhost:8000/api/knowledge/process
```

#### Pricing Information

```bash
curl "http://yourdomain.com/pricing?service=web-development"
```

#### Schedule Check

```bash
curl -X POST http://localhost:8000/api/schedule-check \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "start": "2023-10-01T10:00:00Z",
    "duration": 30
  }'
```

#### Create Booking

```bash
curl -X POST http://localhost:8000/api/create-booking \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "start": "2023-10-01T10:00:00Z",
    "duration": 30,
    "summary": "Demo Call",
    "description": "Product demo call",
    "attendees": ["user@example.com"],
    "hubspot_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "company": "Example Corp",
      "interest": "web-development",
      "session_id": "session-123"
    }
  }'
```

#### Pricing Information

```bash
curl "http://localhost:8000/api/pricing?service=web-development"
```

#### Intent Hints (Upsell Suggestions)

```bash
curl -X POST http://localhost:8000/api/intent-hint \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "web-development",
    "session_id": "session-123"
  }'
```

#### HubSpot Contact Upsert

```bash
curl -X POST http://localhost:8000/api/upsert-hubspot \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Example Corp",
    "interest": "web development",
    "session_id": "session-123"
  }'
```

#### Log Message

```bash
curl -X POST http://localhost:8000/api/log-message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "message": "Hello, I need help with web development",
    "role": "user"
  }'
```

#### Calendar Auth (initiates OAuth flow)

```bash
curl http://localhost:8000/api/calendar/auth
```

### Health Check

```bash
curl http://yourdomain.com/docs  # Should return FastAPI docs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

1. Check the documentation in each module
2. Review the test files for usage examples
3. Create an issue in the repository

---

## ⚠️ Known Issues

- **Python 3.13+ Compatibility**: The current SQLAlchemy version may have compatibility issues with Python 3.13+. Use Python 3.11 as specified in `environment.yml` for best compatibility.
- **Conda Environment**: If conda commands are not recognized in your terminal, you may need to use Anaconda Prompt or ensure conda is properly initialized in your shell.

**Note**: This is a production-ready chatbot implementation with RAG, calendar booking, and CRM integrations. All core functionality is implemented and ready for deployment.
