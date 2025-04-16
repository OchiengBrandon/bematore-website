# apps/solutions/models.py

from django.db import models
from apps.core.models import TimeStampedModel
from django.utils.text import slugify

class Solution(TimeStampedModel):
    PLATFORM_CHOICES = [
        ('mobile', 'Mobile App'),
        ('web', 'Web App'),
        ('both', 'Mobile & Web'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    icon = models.ImageField(upload_to='solutions/icons/')
    featured_image = models.ImageField(upload_to='solutions/featured/')
    app_store_link = models.URLField(blank=True)
    play_store_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Feature(TimeStampedModel):
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # For FontAwesome icons
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.solution.name} - {self.name}"