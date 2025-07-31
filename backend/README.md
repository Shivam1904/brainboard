# Brainboard Backend (Modular)

A modular, scalable backend for the Brainboard application built with FastAPI and SQLAlchemy.

## 🏗️ Architecture

This backend follows a clean architecture pattern with clear separation of concerns:

```
/backend
├── routes/                      # HTTP endpoints
│   ├── alarm.py                # Alarm endpoints
│   └── widgets.py              # Widget listing endpoints
├── services/                   # Business logic
│   ├── base_service.py         # Base service class
│   └── alarm_service.py        # Alarm business logic
├── repositories/               # Database access
│   ├── base_repository.py      # Base repository class
│   └── alarm_repository.py     # Alarm data access
├── models/                     # SQLAlchemy models
│   ├── base.py                 # Base model class
│   ├── alarm_details.py        # Alarm details model
│   └── alarm_item_activity.py  # Alarm activity model
├── schema/                     # Pydantic schemas
│   └── alarm.py                # Alarm request/response schemas
├── db/                         # Database configuration
│   ├── engine.py               # Database engine
│   ├── session.py              # Session management
│   └── dependency.py           # Dependency injection
└── ai_engine/                  # AI functionality (future)
    ├── prompts/                # AI prompt templates
    └── logic/                  # AI logic implementation
```

## 🚀 Quick Start

### Prerequisites

- **Conda** installed on your system
- Python 3.10+ (will be installed via conda)

### Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create conda environment**:
   ```bash
   conda env create -f conda_environment.yml
   ```

3. **Activate conda environment**:
   ```bash
   conda activate brainboard-ai
   ```

4. **Initialize database**:
   ```bash
   python init_db.py
   ```

5. **Generate test data**:
   ```bash
   python generate_test_data.py
   ```

6. **Start the application**:
   ```bash
   python run.py
   ```

7. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Root: http://localhost:8000/

### 🎯 Quick Commands

```bash
# Start server
./run_with_conda.sh server

# Initialize database
./run_with_conda.sh init-db

# Generate test data
./run_with_conda.sh data
```

## 📚 API Endpoints

### Alarms

- `GET /api/v1/alarms/` - Get all alarms
- `GET /api/v1/alarms/active` - Get active alarms
- `GET /api/v1/alarms/{alarm_id}` - Get specific alarm
- `GET /api/v1/alarms/widget/{widget_id}` - Get alarm by widget ID
- `POST /api/v1/alarms/` - Create new alarm
- `PUT /api/v1/alarms/{alarm_id}` - Update alarm
- `DELETE /api/v1/alarms/{alarm_id}` - Delete alarm

### Widgets

- `GET /api/v1/widgets/` - Get available widget types
- `GET /api/v1/widgets/categories` - Get widget categories
- `GET /api/v1/widgets/{widget_type_id}` - Get specific widget type

## 🧪 Testing

Run tests with pytest:

```bash
pytest
```

## 🔧 Development

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

Format code:
```bash
black .
isort .
```

### Database Migrations

When you modify models, create and run migrations:

```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head
```

## 📝 Migration from Old Backend

This is a new modular backend that will gradually replace the old backend in `apps/backend/`. The migration strategy is:

1. **Phase 1**: Foundation (✅ Complete)
   - Basic structure and alarm domain

2. **Phase 2**: Additional domains
   - Todo domain
   - WebSearch domain
   - SingleItemTracker domain

3. **Phase 3**: AI Engine
   - AI prompts and logic
   - Integration with external AI services

4. **Phase 4**: Testing and optimization
   - Comprehensive test coverage
   - Performance optimization

## 🤝 Contributing

1. Follow the established architecture patterns
2. Add tests for new functionality
3. Update documentation as needed
4. Use conventional commit messages

## 📄 License

This project is part of the Brainboard application. 