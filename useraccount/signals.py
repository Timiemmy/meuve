from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AdminUser, Agent, FleetManager, Driver


@receiver(post_save, sender=AdminUser)
def update_admin_status(sender, instance, created, **kwargs):
    instance.user.is_admin = True
    instance.user.save(update_fields=['is_admin'])


@receiver(post_delete, sender=AdminUser)
def remove_admin_status(sender, instance, **kwargs):
    instance.user.is_admin = False
    instance.user.save(update_fields=['is_admin'])


@receiver(post_save, sender=Agent)
def update_agent_status(sender, instance, created, **kwargs):
    instance.user.is_agent = True
    instance.user.save(update_fields=['is_agent'])


@receiver(post_delete, sender=Agent)
def remove_agent_status(sender, instance, **kwargs):
    instance.user.is_agent = False
    instance.user.save(update_fields=['is_agent'])


@receiver(post_save, sender=FleetManager)
def update_fleet_manager_status(sender, instance, created, **kwargs):
    instance.user.is_fleet_manager = True
    instance.user.save(update_fields=['is_fleet_manager'])


@receiver(post_delete, sender=FleetManager)
def remove_fleet_manager_status(sender, instance, **kwargs):
    instance.user.is_fleet_manager = False
    instance.user.save(update_fields=['is_fleet_manager'])


@receiver(post_save, sender=Driver)
def update_driver_status(sender, instance, created, **kwargs):
    instance.user.is_driver = True
    instance.user.save(update_fields=['is_driver'])


@receiver(post_delete, sender=Driver)
def remove_driver_status(sender, instance, **kwargs):
    instance.user.is_driver = False
    instance.user.save(update_fields=['is_driver'])
