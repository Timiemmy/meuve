from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import ParkSerializer
from .models import Park


class ParkListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Park.objects.all()
    serializer_class = ParkSerializer


class ParkDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Park.objects.all()
    serializer_class = ParkSerializer
