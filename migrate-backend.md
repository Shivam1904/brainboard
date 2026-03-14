# Backend Migration Plan: Django + FastAPI Hybrid

## Current Backend Overview

The current backend is built with **FastAPI** and uses:
- **Database**: SQLite with SQLAlchemy (async)
- **ORM**: SQLAlchemy 2.0 with async support
- **API Style**: REST endpoints with async/await
- **WebSocket**: FastAPI WebSocket for AI chat
- **Authentication**: None (development mode)

---

## Migration Goals

1. Introduce **Django** for core backend (widgets, dashboard, tracker, weather)
2. Keep **FastAPI** for AI workloads (orchestrator, LLM calls, WebSocket)
3. Maintain **100% API compatibility** with existing frontend
4. Use **Django ORM** for data models and admin
5. Preserve **async performance** for AI operations
6. Keep infrastructure **minimal** (SQLite, no Redis/PostgreSQL initially)

---

## Target Architecture

```
Frontend
   │
   ├── Django API (Core Backend) - Port 8000
   │      ├── /api/v1/dashboard-widgets/*  (CRUD)
   │      ├── /api/v1/dashboard/*          (Daily widgets)
   │      ├── /api/v1/tracker/*            (Calendar queries)
   │      ├── /api/v1/weather/*           (Weather data)
   │      ├── /health                      (Health check)
   │      └── Django Admin                 (Model inspection)
   │
   └── FastAPI AI Service - Port 8001
          ├── /ai/health                   (AI health)
          ├── /ai/generate-daily-plan      (AI planning)
          ├── /ai/web-search-summary       (Web search)
          └── /ai/ws                       (WebSocket chat)
```

---

## Phase 1: Project Structure

### 1.1 Directory Layout

```
backend/
│
├── django_backend/                 # Django core API (Port 8000)
│   ├── manage.py
│   ├── brainboard/                 # Django project
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── apps/
│   │   ├── dashboard/             # Widget & daily widget management
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   ├── admin.py
│   │   │   └── services.py
│   │   │
│   │   ├── tracker/               # Calendar queries
│   │   │   └── views.py
│   │   │
│   │   ├── weather/              # Weather API
│   │   │   └── views.py
│   │   │
│   │   └── core/                 # Shared utilities
│   │
│   └── db.sqlite3                # Primary database
│
├── fastapi_ai/                   # FastAPI AI service (Port 8001)
│   ├── main.py
│   ├── requirements.txt
│   │
│   ├── routers/
│   │   ├── ai_health.py
│   │   ├── ai_planning.py
│   │   └── websearch.py
│   │
│   ├── services/
│   │   ├── ai_orchestrator.py   # From current backend
│   │   ├── llm_service.py
│   │   └── web_search_service.py
│   │
│   ├── websocket/
│   │   └── ai_ws_manager.py     # From current backend
│   │
│   └── schemas/
│       └── ai.py
│
├── .env                          # Shared environment
└── requirements.txt             # Unified requirements
```

### 1.2 Python Packages

```python
# requirements.txt

# Django Backend
Django>=5.0
djangorestframework>=3.14
django-cors-headers>=4.3
python-dotenv>=1.0

# FastAPI AI Service  
fastapi>=0.110
uvicorn[standard]>=0.24
pydantic>=2.0
openai>=1.3
httpx>=0.25

# Shared
requests>=2.31
```

---

## Phase 2: Django Backend Setup

### 2.1 Django Settings

```python
# brainboard/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# CRITICAL: Disable trailing slash redirects (FastAPI compatibility)
APPEND_SLASH = False

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.dashboard',
    'apps.tracker',
    'apps.weather',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'brainboard.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

CORS_ALLOW_ALL_ORIGINS = True
```

### 2.2 Django URL Configuration

```python
# brainboard/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.dashboard.views import DashboardWidgetViewSet, DashboardViewSet
from apps.tracker.views import TrackerView
from apps.weather.views import WeatherView
from django.http import JsonResponse

router = DefaultRouter(trailing_slash=False)
router.register(r'dashboard-widgets', DashboardWidgetViewSet, basename='dashboard-widgets')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    # Root endpoints (no trailing slash)
    path('', lambda r: JsonResponse({
        'message': 'Brainboard Django API',
        'version': '1.0.0',
        'docs': '/docs',
        'health': '/health'
    })),
    path('health', lambda r: JsonResponse({'status': 'healthy'}), name='health'),
    
    # API routes
    path('api/v1/', include(router.urls)),
    
    # Tracker endpoint
    path('api/v1/tracker/getWidgetActivityForCalendar', TrackerView.as_view(), name='tracker-calendar'),
    
    # Weather endpoint
    path('api/v1/weather', WeatherView.as_view(), name='weather'),
]
```

---

## Phase 3: Django Models

### 3.1 Model Mapping

| FastAPI SQLAlchemy | Django Model |
|-------------------|--------------|
| `DashboardWidgetDetails` | `DashboardWidget` |
| `DailyWidget` | `DailyWidget` |
| `DailyWidgetsAIOutput` | `DailyPlanAIOutput` |
| `WebSearchSummaryAIOutput` | `WebSearchResult` |

### 3.2 Model Implementation

```python
# apps/dashboard/models.py
from django.db import models
import uuid


class DashboardWidget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=50)  # alarm, todo, single_item_tracker, websearch
    frequency = models.CharField(max_length=20)    # daily, weekly, monthly
    frequency_details = models.JSONField(null=True, blank=True)
    importance = models.FloatField()
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    is_permanent = models.BooleanField(default=False)
    widget_config = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delete_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'dashboard_widget_details'
        ordering = ['-created_at']


class DailyWidget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE, related_name='daily_widgets')
    priority = models.CharField(max_length=10)  # HIGH, LOW
    reasoning = models.TextField(null=True, blank=True)
    date = models.DateField()
    is_active = models.BooleanField(default=True)
    activity_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delete_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'daily_widgets'
        ordering = ['-date', '-priority']
        unique_together = ['widget', 'date']


class DailyPlanAIOutput(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10)
    reasoning = models.TextField(null=True, blank=True)
    result_json = models.JSONField(null=True, blank=True)
    date = models.DateField()
    ai_model_used = models.CharField(max_length=50, null=True, blank=True)
    generation_type = models.CharField(max_length=20, default='ai_generated')
    created_at = models.DateTimeField(auto_now_add=True)
    delete_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'daily_widgets_ai_output'


class WebSearchResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    query = models.CharField(max_length=500)
    summary = models.TextField(null=True, blank=True)
    source_json = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delete_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'websearch_summary_ai_output'
```

---

## Phase 4: Django API Endpoints

### 4.1 Dashboard Widgets API (`/api/v1/dashboard-widgets/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/newwidget` | POST | Create new widget |
| `/allwidgets` | GET | Get all widgets for user |
| `/{widget_id}` | GET | Get specific widget |
| `/{widget_id}/update` | PUT | Update widget |
| `/{widget_id}/delete` | DELETE | Delete widget (soft) |
| `/alloftype/{widget_type}` | GET | Get widgets by type |
| `/{widget_id}/priority` | GET | Get widget priority for date |

### 4.2 Dashboard API (`/api/v1/dashboard/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/getTodayWidgetList` | GET | Get today's widget list |
| `/widget/addtotoday/{widget_id}` | POST | Add widget to today |
| `/widget/removefromtoday/{daily_widget_id}` | POST | Remove widget from today |
| `/daily-widgets/{daily_widget_id}/updateactivity` | PUT | Update activity data |
| `/daily-widgets/{widget_id}/getTodayWidgetbyWidgetId` | GET | Get widget by ID and date |

### 4.3 Tracker API (`/api/v1/tracker/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/getWidgetActivityForCalendar` | GET | Get widgets for calendar period |

### 4.4 Weather API (`/api/v1/weather`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Get weather for coordinates |

### 4.5 Root Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |

### 4.6 View Implementation

```python
# apps/dashboard/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import DashboardWidget, DailyWidget
from .serializers import (
    DashboardWidgetSerializer,
    DashboardWidgetCreateSerializer,
    DashboardWidgetUpdateSerializer,
)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    queryset = DashboardWidget.objects.filter(delete_flag=False)
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DashboardWidgetCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DashboardWidgetUpdateSerializer
        return DashboardWidgetSerializer
    
    def list(self, request, *args, **kwargs):
        # GET /allwidgets - return all widgets for user
        user_id = request.query_params.get('user_id', 'user_001')
        queryset = self.get_queryset().filter(user_id=user_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='priority')
    def get_priority(self, request, pk=None):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'detail': 'Date parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        widget = self.get_object()
        # Fetch priority from DailyPlanAIOutput or calculate
        priority_data = {'priority': 'medium', 'reason': 'Based on importance'}
        return Response(priority_data)
    
    @action(detail=False, methods=['get'], url_path='alloftype/(?P<widget_type>[^/.]+)')
    def by_type(self, request, widget_type=None):
        queryset = self.get_queryset().filter(widget_type=widget_type)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DashboardViewSet(viewsets.ViewSet):
    
    def get_today_widget_list(self, request):
        target_date = request.query_params.get('target_date')
        widgets = DailyWidget.objects.filter(
            date=target_date,
            is_active=True,
            delete_flag=False
        ).select_related('widget')
        # Serialize and return
        return Response([])
    
    @action(detail=False, methods=['get'], url_path='getTodayWidgetList')
    def get_today_widget_list(self, request):
        target_date = request.query_params.get('target_date')
        widgets = DailyWidget.objects.filter(
            date=target_date,
            is_active=True,
            delete_flag=False
        ).select_related('widget')
        # Transform to match existing response format
        results = []
        for dw in widgets:
            w = dw.widget
            results.append({
                'daily_widget_id': str(dw.id),
                'widget_id': str(w.id),
                'widget_type': w.widget_type,
                'title': w.title,
                'frequency': w.frequency,
                'importance': w.importance,
                'category': w.category,
                'description': w.description,
                'is_permanent': w.is_permanent,
                'widget_config': w.widget_config,
                'activity_data': dw.activity_data,
                'priority': dw.priority,
                'reasoning': dw.reasoning,
                'date': str(dw.date),
                'is_active': dw.is_active,
            })
        return Response(results)
```

---

## Phase 5: FastAPI AI Service

### 5.1 Main Application

```python
# fastapi_ai/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import ai_health, ai_planning, websearch
from websocket.ai_ws_manager import AIWebSocketManager

app = FastAPI(title="Brainboard AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_health.router, prefix="/ai", tags=["AI Health"])
app.include_router(ai_planning.router, prefix="/ai", tags=["AI Planning"])
app.include_router(websearch.router, prefix="/ai", tags=["Web Search"])

ws_manager = AIWebSocketManager()

@app.websocket("/ai/ws")
async def websocket_ai(websocket: WebSocket):
    await ws_manager.handle_connection(websocket)

@app.get("/")
async def root():
    return {"message": "Brainboard AI Service", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### 5.2 AI Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/health` | GET | AI service health check |
| `/ai/websocket/health` | GET | WebSocket health |
| `/ai/generate-daily-plan` | POST | Generate daily widget plan |
| `/ai/web-search-summary` | POST | Get web search summary |

### 5.3 Router Implementation

```python
# fastapi_ai/routers/ai_health.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    message: str

@router.get("/health")
async def ai_health_check():
    return {"status": "healthy", "message": "AI service operational"}

@router.get("/websocket/health")
async def websocket_health():
    return {"status": "healthy", "active_connections": 0}
```

---

## Phase 6: Service Communication

### 6.1 Django Calling FastAPI

Django uses HTTP to call FastAPI for AI operations:

```python
# apps/dashboard/services/ai_service.py
import requests
from django.conf import settings

AI_SERVICE_URL = "http://localhost:8001"


def generate_daily_plan(widget_data: dict) -> dict:
    """Call FastAPI AI service to generate daily plan."""
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/ai/generate-daily-plan",
            json=widget_data,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


def get_web_search_summary(query: str) -> dict:
    """Call FastAPI AI service for web search summary."""
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/ai/web-search-summary",
            json={"query": query},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
```

---

## Phase 7: Django Admin

```python
# apps/dashboard/admin.py
from django.contrib import admin
from .models import DashboardWidget, DailyWidget, DailyPlanAIOutput, WebSearchResult


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'widget_type', 'user_id', 'frequency', 'importance', 'created_at']
    list_filter = ['widget_type', 'frequency', 'is_permanent']
    search_fields = ['title', 'description']


@admin.register(DailyWidget)
class DailyWidgetAdmin(admin.ModelAdmin):
    list_display = ['id', 'widget', 'date', 'priority', 'is_active']
    list_filter = ['date', 'priority', 'is_active']


@admin.register(DailyPlanAIOutput)
class DailyPlanAIOutputAdmin(admin.ModelAdmin):
    list_display = ['id', 'widget', 'date', 'priority', 'ai_model_used']
    list_filter = ['date', 'ai_model_used']
```

---

## Phase 8: Running Development Environment

### 8.1 Start Django Backend

```bash
cd backend/django_backend
python manage.py runserver 0.0.0.0:8000
```

### 8.2 Start FastAPI AI Service

```bash
cd backend/fastapi_ai
uvicorn main:app --reload --port 8001
```

### 8.3 Verify Both Services

```bash
# Django health
curl http://localhost:8000/health

# FastAPI AI health
curl http://localhost:8001/ai/health
```

---

## Phase 9: Testing API Compatibility

```python
# tests/test_django_api.py
import pytest
from django.test import Client

@pytest.fixture
def client():
    return Client()

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200

def test_create_widget(client):
    response = client.post(
        '/api/v1/dashboard-widgets/newwidget',
        data={
            'widget_type': 'todo',
            'title': 'Test Todo',
            'frequency': 'daily',
            'importance': 0.5,
            'widget_config': {}
        },
        content_type='application/json'
    )
    assert response.status_code == 201

def test_get_all_widgets(client):
    response = client.get('/api/v1/dashboard-widgets/allwidgets')
    assert response.status_code == 200
```

---

## Implementation Order

1. **Create Django project structure** - Set up Django with apps
2. **Migrate models** - Convert SQLAlchemy to Django ORM
3. **Implement Django REST endpoints** - All core CRUD operations
4. **Create FastAPI AI service** - Separate service for AI workloads
5. **Connect Django to FastAPI** - HTTP communication layer
6. **Configure Django admin** - Model inspection interface
7. **Run both services** - Verify functionality
8. **Test API compatibility** - Ensure frontend works unchanged

---

## Key Considerations

### API Compatibility
- All Django endpoints use **no trailing slash** (matches FastAPI)
- Same URL paths, methods, and response formats
- Frontend works without any changes

### Sync vs Async
- Django APIs are **synchronous** (standard DRF)
- FastAPI handles **async** (LLM calls, WebSocket)

### Database
- **SQLite** for development (no PostgreSQL initially)
- Django ORM manages all database operations
- FastAPI does NOT directly access database

### Service Communication
- Django calls FastAPI via HTTP (`requests` library)
- FastAPI endpoints for AI: `/ai/*`
- Keep services independent and loosely coupled

### Minimal Infrastructure
- No Redis (development)
- No Celery (use async directly)
- No PostgreSQL (SQLite sufficient)