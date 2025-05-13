from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import AdminUser, Agent, FleetManager, Driver


def get_or_create_group(name):
    group, _ = Group.objects.get_or_create(name=name)
    return group


@receiver(post_save, sender=AdminUser)
def update_admin_status(sender, instance, created, **kwargs):
    admin_group = get_or_create_group('admin')
    instance.user.groups.add(admin_group)


@receiver(post_delete, sender=AdminUser)
def remove_admin_status(sender, instance, **kwargs):
    admin_group = get_or_create_group('admin')
    instance.user.groups.remove(admin_group)


@receiver(post_save, sender=Agent)
def update_agent_status(sender, instance, created, **kwargs):
    agent_group = get_or_create_group('agent')
    instance.user.groups.add(agent_group)


@receiver(post_delete, sender=Agent)
def remove_agent_status(sender, instance, **kwargs):
    agent_group = get_or_create_group('agent')
    instance.user.groups.remove(agent_group)


@receiver(post_save, sender=FleetManager)
def update_fleet_manager_status(sender, instance, created, **kwargs):
    fleetmanager_group = get_or_create_group('fleetmanager')
    instance.user.groups.add(fleetmanager_group)


@receiver(post_delete, sender=FleetManager)
def remove_fleet_manager_status(sender, instance, **kwargs):
    fleetmanager_group = get_or_create_group('fleetmanager')
    instance.user.groups.remove(fleetmanager_group)


@receiver(post_save, sender=Driver)
def update_driver_status(sender, instance, created, **kwargs):
    driver_group = get_or_create_group('driver')
    instance.user.groups.add(driver_group)


@receiver(post_delete, sender=Driver)
def remove_driver_status(sender, instance, **kwargs):
    driver_group = get_or_create_group('driver')
    instance.user.groups.remove(driver_group)
