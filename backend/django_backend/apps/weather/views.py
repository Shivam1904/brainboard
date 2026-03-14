from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class WeatherView(APIView):
    def get(self, request):
        return Response({"weather": "sunny", "temperature": 72})
