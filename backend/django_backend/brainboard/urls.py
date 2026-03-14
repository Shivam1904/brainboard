from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.dashboard.views import DashboardWidgetViewSet, DashboardViewSet
from apps.tracker.views import TrackerView
from apps.weather.views import WeatherView
from django.http import JsonResponse

router = DefaultRouter(trailing_slash=False)
router.register(
    r"dashboard-widgets", DashboardWidgetViewSet, basename="dashboard-widgets"
)
router.register(r"dashboard", DashboardViewSet, basename="dashboard")

urlpatterns = [
    path(
        "",
        lambda r: JsonResponse(
            {
                "message": "Brainboard Django API",
                "version": "1.0.0",
                "docs": "/docs",
                "health": "/health",
            }
        ),
    ),
    path("health", lambda r: JsonResponse({"status": "healthy"}), name="health"),
    path("api/v1/", include(router.urls)),
    path(
        "api/v1/tracker/getWidgetActivityForCalendar",
        TrackerView.as_view(),
        name="tracker-calendar",
    ),
    path("api/v1/weather", WeatherView.as_view(), name="weather"),
]
