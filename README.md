# Metalogics AI Chatbot

A production-ready smart chatbot for metalogics.io with RAG capabilities, Google Calendar integration, HubSpot CRM integration, and intelligent booking management. Built with FastAPI backend and React frontend.

## 🏗️ Project Structure

```
Chatbot/
├── backend/                 # FastAPI backend server
│   ├── api/                # API routes and endpoints
│   ├── services/           # Business logic services
│   ├── db/                 # Database models and connections
│   ├── main.py            # Backend entry point
│   └── requirements.txt   # Python dependencies
├── frontend/               # React frontend application
│   ├── src/               # React source code
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── vite.config.js     # Vite configuration
├── knowledge_base/         # RAG knowledge base
│   ├── documents/         # Raw documents for processing
│   ├── embeddings/        # Processed embeddings
│   ├── processors/        # Document processing scripts
│   └── config/            # Knowledge base configuration
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── conftest.py        # Pytest configuration
└── .env                   # Environment variables (create this)
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

| Endpoint                 | Method | Description                 |
| ------------------------ | ------ | --------------------------- |
| `/api/chat`              | POST   | Main chat endpoint with RAG |
| `/api/rag-search`        | GET    | Search knowledge base       |
| `/api/rag-answer`        | POST   | Generate RAG answer         |
| `/api/schedule-check`    | POST   | Check booking availability  |
| `/api/create-booking`    | POST   | Create calendar booking     |
| `/api/pricing`           | GET    | Get service pricing         |
| `/api/intent-hint`       | POST   | Get upsell suggestions      |
| `/api/upsert-hubspot`    | POST   | Manage HubSpot contacts     |
| `/api/calendar/auth`     | GET    | Initiate Google OAuth       |
| `/api/calendar/freebusy` | GET    | Get calendar availability   |

## 🚀 Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- PostgreSQL (required)
- [Miniconda or Anaconda](https://docs.conda.io/projects/miniconda/en/latest/) (recommended for environment management)

### 1. Install Dependencies

#### Option 1: Using Conda (Recommended)

Conda provides isolated environments, making it easier to manage dependencies and save system memory.

```bash
# Create conda environment from the provided environment.yml
conda env create -f environment.yml

# Activate the environment
conda activate chatbot-backend

# For frontend dependencies (still use npm)
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

# Vector Database (ChromaDB is used instead of Pinecone)
# No additional configuration needed - uses local ChromaDB

# Database (SQLite for development, can be configured for PostgreSQL)
DATABASE_URL=sqlite:///./chatbot.db

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
| `PORT`                      | Application port (default: 8000)           | ❌       |

### 3. Run Development Servers

#### Start Backend Server

If using conda:

```bash
# Activate conda environment (if not already activated)
conda activate chatbot-backend

cd backend
python main.py
```

If using pip environment:

```bash
cd backend
python main.py
```

The backend will run on `http://localhost:8000`

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
conda activate chatbot-backend
cd backend && python main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

If using pip:

```bash
# Terminal 1 - Backend
cd backend && python main.py

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
- **Vector Storage**: Pinecone or similar vector database
- **Retrieval**: Context-aware document retrieval

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
- Production database (PostgreSQL required)
- OpenAI API access
- Google Cloud Console project for OAuth
- HubSpot developer account
- ChromaDB for vector storage

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
GOOGLE_REDIRECT_URI=https://yourdomain.com/google/callback

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
   - `https://yourdomain.com/google/callback` (production)
   - `http://localhost:3000/google/callback` (development)

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

The application uses ChromaDB for vector storage. The database is automatically initialized when the application starts.

1. **Process knowledge base documents**:

   ```bash
   cd backend
   python -c "from services.rag_service import RAGService; rag = RAGService(); rag.process_knowledge_base()"
   ```

2. **Verify vector database**:
   ```bash
   curl http://localhost:8001/knowledge
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
   python main.py

   # Production with uvicorn
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

   # Production with gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
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
curl http://yourdomain.com/knowledge
```

#### Process Knowledge Base

```bash
curl -X POST http://yourdomain.com/knowledge/process
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

**Note**: This is a project scaffold. The placeholder implementations need to be replaced with actual functionality for production use.
# chatbot-project
