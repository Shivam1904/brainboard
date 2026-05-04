.PHONY: dev backend-dev frontend-dev setup backend-setup frontend-setup test lint help

# --- Development ---

dev: ## Run backend (FastAPI) and frontend development servers
	@echo "Killing existing processes on ports 8989, 5173..."
	@-lsof -t -i:8989 | xargs kill -9 2>/dev/null || true
	@-lsof -t -i:5173 | xargs kill -9 2>/dev/null || true
	@-lsof -t -i:5511 | xargs kill -9 2>/dev/null || true
	@echo "Starting FastAPI AI service and frontend..."
	@(make fastapi-ai & make frontend-dev & wait)


django-backend: ## Run Django backend server on port 8220
	@echo "Starting Django server on port 8220..."
	@cd backend/django_backend && python manage.py runserver 0.0.0.0:8220


fastapi-ai: ## Run FastAPI AI service on port 8989
	@echo "Starting FastAPI AI service on port 8989..."
	@cd backend && . .venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8989


frontend-dev: ## Run Vite development server
	@echo "Starting Vite server..."
	@cd frontend && npm run dev


setup: backend-setup frontend-setup ## Setup all dependencies


backend-setup: ## Setup backend Python environment
	@echo "Setting up backend..."
	@cd backend && \
	if [ ! -d ".venv" ]; then \
		python -m venv .venv; \
	fi && \
	. .venv/bin/activate && pip install -r requirements.txt


frontend-setup: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install


# --- Testing ---

test: frontend-test ## Run tests


frontend-test: ## Run frontend tests
	@cd frontend && npm test


# --- Linting & Quality ---

lint: frontend-lint ## Run linters


frontend-lint: ## Run frontend linter (eslint)
	@cd frontend && npm run lint


# --- Help ---

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


.DEFAULT_GOAL := help
