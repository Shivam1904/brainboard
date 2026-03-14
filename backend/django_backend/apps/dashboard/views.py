from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    queryset = []
    lookup_field = "id"

    def list(self, request, *args, **kwargs):
        return Response([])

    def create(self, request, *args, **kwargs):
        return Response({"status": "created"}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        return Response({})

    def update(self, request, *args, **kwargs):
        return Response({})

    def partial_update(self, request, *args, **kwargs):
        return Response({})

    def destroy(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="priority")
    def get_priority(self, request, pk=None):
        priority_data = {"priority": "medium", "reason": "Based on importance"}
        return Response(priority_data)

    @action(detail=False, methods=["get"], url_path="alloftype/(?P<widget_type>[^/.]+)")
    def by_type(self, request, widget_type=None):
        return Response([])


class DashboardViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="getTodayWidgetList")
    def get_today_widget_list(self, request):
        return Response([])


from rest_framework.views import APIView
from rest_framework.response import Response


class DashboardWidgetView(APIView):
    def get(self, request):
        return Response({"message": "Dashboard widgets"})

    def post(self, request):
        return Response({"message": "Create widget"}, status=status.HTTP_201_CREATED)
