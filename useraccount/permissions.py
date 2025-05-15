from rest_framework import permissions
from django.contrib.auth import get_user_model
from park.models import Park
import logging

logger = logging.getLogger(__name__)
CustomUser = get_user_model()


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to perform actions.
    """

    def has_permission(self, request, view):
        user_groups = list(request.user.groups.values_list('name', flat=True))
        logger.debug(f"User groups for {request.user.email}: {user_groups}")
        return bool(request.user and request.user.is_authenticated and request.user.groups.filter(name='admin').exists())

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not request.user.groups.filter(name='admin').exists():
            return False

        # Admin has full permissions on objects in their service region
        admin_region = request.user.admin_profile.service_region
        if hasattr(obj, 'service_region'):
            return obj.service_region == admin_region
        elif isinstance(obj, Park):
            return obj == admin_region
        return False


class IsFleetManager(permissions.BasePermission):
    """
    Custom permission to only allow fleet managers to perform actions on vehicles in their service region.
    """

    def has_permission(self, request, view):
        user_groups = list(request.user.groups.values_list('name', flat=True))
        logger.debug(f"User groups for {request.user.email}: {user_groups}")
        return bool(request.user and request.user.is_authenticated and request.user.groups.filter(name='fleetmanager').exists())

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not request.user.groups.filter(name='fleetmanager').exists():
            return False

        fleet_manager_region = request.user.fleetmanager_profile.service_region
        if hasattr(obj, 'service_region'):
            return obj.service_region == fleet_manager_region
        elif isinstance(obj, Park):
            return obj == fleet_manager_region
        return False


class IsDriver(permissions.BasePermission):
    """
    Custom permission to only allow drivers to view bookings and parks in their service region.
    """

    def has_permission(self, request, view):
        user_groups = list(request.user.groups.values_list('name', flat=True))
        logger.debug(f"User groups for {request.user.email}: {user_groups}")
        return bool(request.user and request.user.is_authenticated and request.user.groups.filter(name='driver').exists())

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not request.user.groups.filter(name='driver').exists():
            return False

        driver_region = request.user.driver_profile.service_region

        # For bookings, check if the driver is assigned to the vehicle
        if hasattr(obj, 'vehicle'):
            return obj.vehicle == request.user.driver_profile.vehicle

        # For parks, check if they're in the driver's service region
        if isinstance(obj, Park):
            return obj == driver_region

        # For other objects with service_region
        if hasattr(obj, 'service_region'):
            return obj.service_region == driver_region

        return False


class IsAgent(permissions.BasePermission):
    """
    Custom permission to only allow agents to perform actions.
    No service region constraints for agents.
    """

    def has_permission(self, request, view):
        user_groups = list(request.user.groups.values_list('name', flat=True))
        print(f"User groups for {request.user.email}: {user_groups}")
        is_authenticated = bool(request.user and request.user.is_authenticated)
        is_agent = bool(request.user.groups.filter(name='agent').exists())
        print(f"Is authenticated: {is_authenticated}, Is agent: {is_agent}")
        return is_authenticated and is_agent

    def has_object_permission(self, request, view, obj):
        print(f"Checking object permission for user {request.user.email}")
        print(f"Object type: {type(obj)}")

        if not request.user.is_authenticated:
            print("User not authenticated")
            return False

        if not request.user.groups.filter(name='agent').exists():
            print("User not in agent group")
            return False

        # Agents have full access to all objects
        return True


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow users to perform actions on their own objects.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

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
        user_groups = list(request.user.groups.values_list('name', flat=True))
        logger.debug(f"User groups for {request.user.email}: {user_groups}")
        return bool(request.user and request.user.is_authenticated and (
            request.user.groups.filter(name='admin').exists() or
            request.user.groups.filter(name='fleetmanager').exists()
        ))

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.groups.filter(name='admin').exists():
            admin_region = request.user.admin_profile.service_region
            if hasattr(obj, 'service_region'):
                return obj.service_region == admin_region
            elif isinstance(obj, Park):
                return obj == admin_region
            return False

        if request.user.groups.filter(name='fleetmanager').exists():
            fleet_manager_region = request.user.fleetmanager_profile.service_region
            if hasattr(obj, 'service_region'):
                return obj.service_region == fleet_manager_region
            elif isinstance(obj, Park):
                return obj == fleet_manager_region
            return False

        return False
