from rest_framework import generics
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from useraccount.permissions import IsAdmin, IsAdminOrFleetManager, IsAgent, IsFleetManager, IsDriver
from . import serializers
from .models import Vehicle, VehicleType, Amenity, VehicleImage


class VehicleTypeListView(generics.ListAPIView):
    """List all vehicle types."""
    permission_classes = [IsAuthenticated]
    queryset = VehicleType.objects.all()
    serializer_class = serializers.VehicleTypeSerializer


class VehicleTypeCreateView(generics.CreateAPIView):
    """Create a new vehicle type."""
    permission_classes = [IsAuthenticated, IsAdminOrFleetManager]
    queryset = VehicleType.objects.all()
    serializer_class = serializers.VehicleTypeSerializer


class VehicleTypeDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve a specific vehicle type."""
    permission_classes = [IsAuthenticated]
    queryset = VehicleType.objects.all()
    serializer_class = serializers.VehicleTypeSerializer


class VehicleTypeDeleteView(generics.RetrieveDestroyAPIView):
    """Delete a specific vehicle type."""
    permission_classes = [IsAuthenticated, IsAdminOrFleetManager]
    queryset = VehicleType.objects.all()
    serializer_class = serializers.VehicleTypeSerializer


class VehicleAmenityListView(generics.ListAPIView):
    """List all vehicle amenities."""
    permission_classes = [IsAuthenticated]
    queryset = Amenity.objects.all()
    serializer_class = serializers.VehicleAmenitySerializer


class VehicleAmenityCreateView(generics.CreateAPIView):
    """Create a new vehicle amenity."""
    permission_classes = [IsAuthenticated, IsAdminOrFleetManager]
    queryset = Amenity.objects.all()
    serializer_class = serializers.VehicleAmenitySerializer


class VehicleAmenityDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve a specific vehicle amenity."""
    permission_classes = [IsAuthenticated]
    queryset = Amenity.objects.all()
    serializer_class = serializers.VehicleAmenitySerializer


class VehicleAmenityDeleteView(generics.RetrieveDestroyAPIView):
    """Delete a specific vehicle amenity."""
    permission_classes = [IsAuthenticated, IsAdminOrFleetManager]
    queryset = Amenity.objects.all()
    serializer_class = serializers.VehicleAmenitySerializer


class VehicleListView(generics.ListAPIView):
    """List all vehicles."""
    permission_classes = [IsAuthenticated]
    queryset = Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'make': ['exact', 'icontains'],
        'model': ['exact', 'icontains'],
        'category': ['exact'],
    }
    ordering = ['-departure_time']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by vehicle type if specified
        vehicle_type = self.request.query_params.get('vehicle_type')
        if vehicle_type:
            queryset = queryset.filter(category__id=vehicle_type)

        vehicle_driver = self.request.query_params.get('vehicle_driver')
        if vehicle_driver:
            queryset = queryset.filter(drivers__user__id=vehicle_driver)

        return queryset


class VehicleCreateWithImages(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrFleetManager]
    queryset = Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extract images data
        images_data = []
        for key, value in request.data.items():
            if key.startswith('images[') and key.endswith('][image]'):
                index = key[7:-8]  # Extract index from 'images[0][image]'

                # Find corresponding caption if exists
                caption_key = f'images[{index}][caption]'
                caption = request.data.get(caption_key, '')

                images_data.append({
                    'image': value,
                    'caption': caption
                })

        # Handle regular vehicle data
        vehicle_data = {}
        for key, value in request.data.items():
            if not key.startswith('images['):
                vehicle_data[key] = value

        # Create vehicle
        vehicle_serializer = self.get_serializer(data=vehicle_data)
        vehicle_serializer.is_valid(raise_exception=True)
        vehicle = vehicle_serializer.save()

        # Create images
        for image_data in images_data:
            image_serializer = serializers.VehicleImageCreateSerializer(data=image_data)
            if image_serializer.is_valid():
                image_serializer.save(vehicle=vehicle)

        headers = self.get_success_headers(vehicle_serializer.data)
        return Response(vehicle_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class VehicleUpdateWithImages(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrFleetManager]
    queryset = Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        vehicle = self.get_object()

        # Extract images data
        images_data = []
        for key, value in request.data.items():
            if key.startswith('images[') and key.endswith('][image]'):
                index = key[7:-8]  # Extract index from 'images[0][image]'

                # Find corresponding caption if exists
                caption_key = f'images[{index}][caption]'
                caption = request.data.get(caption_key, '')

                # Check if there's an image ID (for existing images)
                id_key = f'images[{index}][id]'
                image_id = request.data.get(id_key, None)

                images_data.append({
                    'id': image_id,
                    'image': value,
                    'caption': caption
                })

        # Handle regular vehicle data
        vehicle_data = {}
        for key, value in request.data.items():
            if not key.startswith('images['):
                vehicle_data[key] = value

        # Update vehicle
        vehicle_serializer = self.get_serializer(
            vehicle, data=vehicle_data, partial=True)
        vehicle_serializer.is_valid(raise_exception=True)
        vehicle = vehicle_serializer.save()

        # Process images
        for image_data in images_data:
            image_id = image_data.pop('id', None)

            if image_id:
                # Update existing image
                try:
                    vehicle_image = VehicleImage.objects.get(
                        id=image_id, vehicle=vehicle)
                    image_serializer = serializers.VehicleImageCreateSerializer(
                        vehicle_image, data=image_data, partial=True)
                    if image_serializer.is_valid():
                        image_serializer.save()
                except VehicleImage.DoesNotExist:
                    pass
            else:
                # Create new image
                image_serializer = serializers.VehicleImageCreateSerializer(
                    data=image_data)
                if image_serializer.is_valid():
                    image_serializer.save(vehicle=vehicle)

        # Handle image deletions
        if 'delete_images' in request.data:
            delete_ids = request.data.getlist('delete_images')
            VehicleImage.objects.filter(
                id__in=delete_ids, vehicle=vehicle).delete()

        return Response(vehicle_serializer.data)


# Vehicle image upload for existing vehicle
class VehicleImageUpload(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrFleetManager]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, vehicle_id, format=None):
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response(
                {"detail": "Vehicle not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Handle multiple images
        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {"detail": "No images provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create image objects
        image_objects = []
        for image in images:
            vehicle_image = VehicleImage.objects.create(
                vehicle=vehicle,
                image=image,
                caption=request.data.get('caption', '')
            )
            image_objects.append(vehicle_image)

        # Serialize and return
        serializer = serializers.VehicleImageSerializer(
            image_objects, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VehicleDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer


class VehicleUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrFleetManager]
    queryset = Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer


class VehicleDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrFleetManager]
    queryset = Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer


class VehicleImageListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.VehicleImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return VehicleImage.objects.filter(vehicle_id=self.kwargs['vehicle_id'])

    def perform_create(self, serializer):
        vehicle = Vehicle.objects.get(pk=self.kwargs['vehicle_id'])
        serializer.save(vehicle=vehicle)


class VehicleImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = VehicleImage.objects.all()
    serializer_class = serializers.VehicleImageSerializer
