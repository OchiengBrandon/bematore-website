# apps/api/models.py

from django.db import models
from apps.core.models import TimeStampedModel

class APIKey(TimeStampedModel):
    name = models.CharField(max_length=50)
    key = models.CharField(max_length=40, unique=True)
    is_active = models.BooleanField(default=True)
    rate_limit = models.PositiveIntegerField(default=100)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class APILog(TimeStampedModel):
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    response_code = models.PositiveIntegerField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.endpoint} - {self.response_code}"