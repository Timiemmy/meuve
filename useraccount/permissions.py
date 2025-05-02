from rest_framework import permissions
from django.contrib.auth import get_user_model
from park.models import Park

CustomUser = get_user_model()


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to perform actions.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not request.user.is_admin:
            return False

        # Check if the object is within the admin's service region
        if hasattr(obj, 'service_region'):
            admin_region = request.user.admin_profile.service_region
            return obj.service_region == admin_region
        return True


class IsFleetManager(permissions.BasePermission):
    """
    Custom permission to only allow fleet managers to perform actions on vehicles in their service region.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_fleet_manager

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not request.user.is_fleet_manager:
            return False

        # Check if the vehicle is within the fleet manager's service region
        fleet_manager_region = request.user.fleetmanager_profile.service_region
        if hasattr(obj, 'service_region'):
            return obj.service_region == fleet_manager_region
        return False


class IsDriver(permissions.BasePermission):
    """
    Custom permission to only allow drivers to view bookings and parks in their service region.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_driver

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not request.user.is_driver:
            return False

        driver_region = request.user.driver_profile.service_region

        # For bookings, check if the driver is assigned to the vehicle
        if hasattr(obj, 'vehicle'):
            return obj.vehicle == request.user.driver_profile.vehicle

        # For parks, check if they're in the driver's service region
        if isinstance(obj, Park):
            return obj == driver_region

        return False


class IsAgent(permissions.BasePermission):
    """
    Custom permission to only allow agents to manage bookings in their service region.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_agent

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not request.user.is_agent:
            return False

        agent_region = request.user.agent_profile.service_region

        # For bookings, check if they're in the agent's service region
        if hasattr(obj, 'service_region'):
            return obj.service_region == agent_region

        return False


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow users to perform actions on their own objects.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Check if the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # Check if the object is a CustomUser
        if isinstance(obj, CustomUser):
            return obj == request.user

        return False


class IsAdminOrFleetManager(permissions.BasePermission):
    """
    Custom permission to allow both admins and fleet managers to perform actions.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_fleet_manager)

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.is_admin:
            return True

        if request.user.is_fleet_manager:
            fleet_manager_region = request.user.fleetmanager_profile.service_region
            if hasattr(obj, 'service_region'):
                return obj.service_region == fleet_manager_region

        return False
