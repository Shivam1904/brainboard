# 🔧 Backend Architecture

## Tech Stack
- **Framework**: FastAPI
- **Language**: Python
- **Environment**: Conda (environment.yml)
- **Database**: TBD (PostgreSQL planned)
- **ORM**: SQLAlchemy (planned)

## Project Structure
```
apps/backend/
├── main.py                    # FastAPI application entry point
├── environment.yml            # Conda environment configuration
├── package.json              # Node.js dependencies (if any)
├── core/
│   ├── __init__.py
│   ├── auth.py               # Authentication logic
│   ├── config.py             # Application configuration
│   └── database.py           # Database connection and setup
├── models/
│   ├── __init__.py
│   └── schemas.py            # Pydantic models and database schemas
├── routers/
│   ├── __init__.py
│   ├── auth.py               # Authentication endpoints
│   ├── reminders.py          # Task/reminder CRUD operations
│   └── summaries.py          # AI summary endpoints
└── services/
    ├── __init__.py
    └── ai_service.py         # AI/OpenAI integration service
```

## API Architecture

### Authentication Module
- **Core**: `core/auth.py` - Authentication logic and utilities
- **Routes**: `routers/auth.py` - Login, register, logout endpoints
- **Status**: ❌ Not implemented

### Reminders Module
- **Routes**: `routers/reminders.py` - CRUD operations for tasks
- **Models**: Task creation, update, deletion, listing
- **Status**: ❌ Not implemented

### AI Summary Module
- **Routes**: `routers/summaries.py` - Web search and summary endpoints
- **Service**: `services/ai_service.py` - OpenAI integration
- **Status**: ❌ Not implemented

### Core Infrastructure
- **Config**: `core/config.py` - Environment variables, settings
- **Database**: `core/database.py` - Connection pooling, session management
- **Models**: `models/schemas.py` - Pydantic models for API validation

## Planned Features

### API Endpoints
- **Authentication**:
  - `POST /auth/register` - User registration
  - `POST /auth/login` - User login
  - `POST /auth/logout` - User logout
  - `GET /auth/me` - Get current user
- **Reminders**:
  - `GET /reminders` - List user reminders
  - `POST /reminders` - Create new reminder
  - `PUT /reminders/{id}` - Update reminder
  - `DELETE /reminders/{id}` - Delete reminder
- **Summaries**:
  - `POST /summaries/web` - Generate web page summary
  - `GET /summaries/{id}` - Retrieve saved summary

### External Integrations
- **OpenAI API**: Web content summarization
- **Database**: User data and widget persistence
- **Authentication**: JWT token management

## Current Status
- ✅ Project structure created
- ✅ Module organization (core, models, routers, services)
- ❌ FastAPI server setup (pending)
- ❌ Database integration (pending)
- ❌ Authentication system (pending)
- ❌ API endpoints implementation (pending)
- ❌ AI service integration (pending)
