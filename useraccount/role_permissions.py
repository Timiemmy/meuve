from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from .models import CustomUser, AdminUser, Agent, FleetManager, Driver

# Define permission sets for each role
ADMIN_PERMISSIONS = [
    # User management
    ('useraccount', 'customuser', ['view', 'add', 'change', 'delete']),
    ('useraccount', 'adminuser', ['view', 'add', 'change', 'delete']),
    ('useraccount', 'agent', ['view', 'add', 'change', 'delete']),
    ('useraccount', 'fleetmanager', ['view', 'add', 'change', 'delete']),
    ('useraccount', 'driver', ['view', 'add', 'change', 'delete']),
    ('useraccount', 'emergencycontact', ['view', 'add', 'change', 'delete']),
    ('useraccount', 'address', ['view', 'add', 'change', 'delete']),

    # Booking management
    ('booking', 'booking', ['view', 'add', 'change', 'delete']),

    # Vehicle management
    ('vehicle', 'vehicle', ['view', 'add', 'change', 'delete']),
    ('vehicle', 'vehiclemodel', ['view', 'add', 'change', 'delete']),
    ('vehicle', 'vehiclemake', ['view', 'add', 'change', 'delete']),

    # Park management
    ('park', 'park', ['view', 'add', 'change', 'delete']),

    # Payment management
    ('payment', 'payment', ['view', 'add', 'change', 'delete']),
]

AGENT_PERMISSIONS = [
    # User management
    ('useraccount', 'customuser', ['view']),
    ('useraccount', 'driver', ['view', 'add', 'change']),
    ('useraccount', 'emergencycontact', ['view', 'add', 'change']),
    ('useraccount', 'address', ['view', 'add', 'change']),

    # Booking management
    ('booking', 'booking', ['view', 'add', 'change']),

    # Vehicle management
    ('vehicle', 'vehicle', ['view']),
    ('vehicle', 'vehiclemodel', ['view']),
    ('vehicle', 'vehiclemake', ['view']),

    # Park management
    ('park', 'park', ['view']),

    # Payment management
    ('payment', 'payment', ['view', 'add', 'change']),
]

FLEET_MANAGER_PERMISSIONS = [
    # User management
    ('useraccount', 'customuser', ['view']),
    ('useraccount', 'driver', ['view', 'add', 'change']),
    ('useraccount', 'emergencycontact', ['view']),
    ('useraccount', 'address', ['view']),

    # Booking management
    ('booking', 'booking', ['view', 'change']),

    # Vehicle management
    ('vehicle', 'vehicle', ['view', 'add', 'change', 'delete']),
    ('vehicle', 'vehiclemodel', ['view', 'add', 'change']),
    ('vehicle', 'vehiclemake', ['view', 'add', 'change']),

    # Park management
    ('park', 'park', ['view']),

    # Payment management
    ('payment', 'payment', ['view']),
]

DRIVER_PERMISSIONS = [
    # User management
    ('useraccount', 'customuser', ['view']),
    ('useraccount', 'emergencycontact', ['view']),
    ('useraccount', 'address', ['view']),

    # Booking management
    ('booking', 'booking', ['view', 'change']),

    # Vehicle management
    ('vehicle', 'vehicle', ['view']),
    ('vehicle', 'vehiclemodel', ['view']),
    ('vehicle', 'vehiclemake', ['view']),

    # Park management
    ('park', 'park', ['view']),

    # Payment management
    ('payment', 'payment', ['view']),
]


def get_or_create_permissions(app_label, model_name, codenames):
    """Helper function to get or create permissions for a model"""
    content_type = ContentType.objects.get(
        app_label=app_label, model=model_name)
    permissions = []

    for codename_base in codenames:
        codename = f"{codename_base}_{model_name}"
        try:
            permission = Permission.objects.get(
                codename=codename,
                content_type=content_type
            )
        except Permission.DoesNotExist:
            # If the permission doesn't exist yet, create it with a descriptive name
            name = f"Can {codename_base} {model_name}"
            permission = Permission.objects.create(
                codename=codename,
                name=name,
                content_type=content_type
            )
        permissions.append(permission)

    return permissions


@transaction.atomic
def create_groups_and_permissions():
    """Create groups and assign permissions"""
    # Create groups
    admin_group, _ = Group.objects.get_or_create(name='admin')
    agent_group, _ = Group.objects.get_or_create(name='agent')
    fleet_manager_group, _ = Group.objects.get_or_create(name='fleetmanager')
    driver_group, _ = Group.objects.get_or_create(name='driver')

    # Clear existing permissions to ensure consistency
    admin_group.permissions.clear()
    agent_group.permissions.clear()
    fleet_manager_group.permissions.clear()
    driver_group.permissions.clear()

    # Assign Admin permissions
    for app_label, model_name, codenames in ADMIN_PERMISSIONS:
        permissions = get_or_create_permissions(
            app_label, model_name, codenames)
        admin_group.permissions.add(*permissions)

    # Assign Agent permissions
    for app_label, model_name, codenames in AGENT_PERMISSIONS:
        permissions = get_or_create_permissions(
            app_label, model_name, codenames)
        agent_group.permissions.add(*permissions)

    # Assign FleetManager permissions
    for app_label, model_name, codenames in FLEET_MANAGER_PERMISSIONS:
        permissions = get_or_create_permissions(
            app_label, model_name, codenames)
        fleet_manager_group.permissions.add(*permissions)

    # Assign Driver permissions
    for app_label, model_name, codenames in DRIVER_PERMISSIONS:
        permissions = get_or_create_permissions(
            app_label, model_name, codenames)
        driver_group.permissions.add(*permissions)


def sync_user_groups(user):
    """Sync a user's groups based on their roles"""
    # Remove user from all role-based groups first
    user.groups.remove(
        *Group.objects.filter(name__in=['admin', 'agent', 'fleetmanager', 'driver']))

    # Add user to appropriate groups based on their roles
    try:
        if AdminUser.objects.filter(user=user).exists():
            admin_group = Group.objects.get(name='admin')
            user.groups.add(admin_group)
    except ObjectDoesNotExist:
        pass

    try:
        if Agent.objects.filter(user=user).exists():
            agent_group = Group.objects.get(name='agent')
            user.groups.add(agent_group)
    except ObjectDoesNotExist:
        pass

    try:
        if FleetManager.objects.filter(user=user).exists():
            fleet_manager_group = Group.objects.get(name='fleetmanager')
            user.groups.add(fleet_manager_group)
    except ObjectDoesNotExist:
        pass

    try:
        if Driver.objects.filter(user=user).exists():
            driver_group = Group.objects.get(name='driver')
            user.groups.add(driver_group)
    except ObjectDoesNotExist:
        pass

# Signal handlers for role-based models


@receiver(post_save, sender=AdminUser)
def handle_admin_save(sender, instance, created, **kwargs):
    """Add user to Admin group when Admin role is created"""
    admin_group = Group.objects.get(name='admin')
    instance.user.groups.add(admin_group)


@receiver(post_save, sender=Agent)
def handle_agent_save(sender, instance, created, **kwargs):
    """Add user to Agent group when Agent role is created"""
    agent_group = Group.objects.get(name='agent')
    instance.user.groups.add(agent_group)


@receiver(post_save, sender=FleetManager)
def handle_fleet_manager_save(sender, instance, created, **kwargs):
    """Add user to FleetManager group when FleetManager role is created"""
    fleet_manager_group = Group.objects.get(name='fleetmanager')
    instance.user.groups.add(fleet_manager_group)


@receiver(post_save, sender=Driver)
def handle_driver_save(sender, instance, created, **kwargs):
    """Add user to Driver group when Driver role is created"""
    driver_group = Group.objects.get(name='driver')
    instance.user.groups.add(driver_group)
