# 🚀 Backend Setup Instructions

## Prerequisites

- **Conda** installed on your system
- **Python 3.10+** (will be installed via conda)

## Step-by-Step Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Conda Environment
```bash
conda env create -f conda_environment.yml
```

### 3. Activate Conda Environment
```bash
conda activate brainboard-ai
```

### 4. Verify Installation
```bash
python -c "import fastapi, sqlalchemy, pydantic; print('✅ All dependencies installed successfully!')"
```

### 5. Initialize Database
```bash
python init_db.py
```

### 6. Run Tests
```bash
python test_basic.py
```

### 7. Start Server
```bash
python run.py
```

## 🎯 Quick Commands

### Development Workflow
```bash
# Activate environment
conda activate brainboard-ai

# Run tests
python test_basic.py

# Start development server
python run.py

# Format code
black .
isort .

# Lint code
flake8 .
```

### Database Operations
```bash
# Initialize database (first time only)
python init_db.py

# Reset database (if needed)
rm brainboard.db
python init_db.py
```

## 🔧 Environment Management

### Update Environment
```bash
conda env update -f conda_environment.yml
```

### Remove Environment
```bash
conda env remove -n brainboard-ai
```

### List Environments
```bash
conda env list
```

## 📝 Important Notes

- **Always activate the conda environment** before running any commands
- The environment name is `brainboard-ai`
- Database file is `brainboard.db` in the backend directory
- Server runs on `http://localhost:8000`
- API docs available at `http://localhost:8000/docs`

## 🐛 Troubleshooting

### If conda env create fails:
```bash
# Try with explicit channel
conda env create -f conda_environment.yml -c conda-forge
```

### If packages conflict:
```bash
# Remove and recreate environment
conda env remove -n brainboard-ai
conda env create -f conda_environment.yml
```

### If database issues:
```bash
# Remove database and reinitialize
rm brainboard.db
python init_db.py
```

## 🎉 Success Indicators

- ✅ `conda activate brainboard-ai` works
- ✅ `python test_basic.py` passes all tests
- ✅ `python run.py` starts server without errors
- ✅ `curl http://localhost:8000/health` returns healthy status 