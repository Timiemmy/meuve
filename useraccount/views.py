from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from useraccount.models import CustomUser, EmergencyContact, Address, Driver
from .permissions import IsAdmin, IsAgent, IsAdminOrFleetManager, IsFleetManager, IsOwner, IsDriver
from . import serializers


class CustomUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin | IsAgent]
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer


class CustomUserCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer


class CustomUserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_address(self, obj):
        try:
            address = Address.objects.get(user=obj)
            # This is important - pass the context
            return serializers.AddressSerializer(address, context=self.context).data
        except Address.DoesNotExist:
            return None


class CustomUserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    #permission_classes = [IsAuthenticated]


class CustomUserDestroyView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    permission_classes = [IsAuthenticated]


class DriverListView(generics.ListAPIView):
    queryset = Driver.objects.all()
    serializer_class = serializers.DriverSerializer
    permission_classes = [IsAuthenticated]


class DriverDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Driver.objects.all()
    serializer_class = serializers.DriverSerializer
    permission_classes = [IsAuthenticated]


class EmergencyContactListView(generics.ListAPIView):
    queryset = EmergencyContact.objects.all()
    serializer_class = serializers.EmergencyContactSerializer
    permission_classes = [IsAuthenticated]


class EmergencyContactOwnerListView(generics.ListAPIView):
    serializer_class = serializers.EmergencyContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        return EmergencyContact.objects.filter(user_id=user_id)


class EmergencyContactCreateView(generics.CreateAPIView):
    serializer_class = serializers.EmergencyContactSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_id = self.kwargs.get('pk')
        user = CustomUser.objects.get(pk=user_id)
        serializer.save(user=user)


class EmergencyContactDeleteView(generics.RetrieveDestroyAPIView):
    serializer_class = serializers.EmergencyContactSerializer
    queryset = EmergencyContact.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


# Address
class AddressListView(generics.ListAPIView):
    serializer_class = serializers.AddressSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        return Address.objects.filter(user_id=user_id)


class AddressCreateView(generics.CreateAPIView):
    serializer_class = serializers.AddressSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_id = self.kwargs.get('pk')
        user = CustomUser.objects.get(pk=user_id)
        serializer.save(user=user)


class AddressDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.AddressSerializer
    queryset = Address.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


class AddressDeleteView(generics.RetrieveDestroyAPIView):
    serializer_class = serializers.AddressSerializer
    queryset = Address.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
