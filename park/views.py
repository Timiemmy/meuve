from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .serializers import ParkSerializer
from .models import Park


@extend_schema(
    tags=['Parks'],
    description='List all available parks',
    responses={200: ParkSerializer(many=True)}
)
class ParkListView(generics.ListAPIView):
    """
    API endpoint that allows parks to be viewed.
    """
    permission_classes = [IsAuthenticated]
    queryset = Park.objects.all()
    serializer_class = ParkSerializer


@extend_schema(
    tags=['Parks'],
    description='Retrieve a specific park by ID',
    responses={200: ParkSerializer}
)
class ParkDetailView(generics.RetrieveAPIView):
    """
    API endpoint that allows a specific park to be viewed.
    """
    permission_classes = [IsAuthenticated]
    queryset = Park.objects.all()
    serializer_class = ParkSerializer
