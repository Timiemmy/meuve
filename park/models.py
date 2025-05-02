from django.db import models
#from django.contrib.gis.db import models as gis_models
from core.models import TimeStampedModel, UUIDModel


class Park( TimeStampedModel, UUIDModel):
    """Company park/station locations"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    #location = gis_models.PointField()  # GeoDjango PointField for coordinates
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name