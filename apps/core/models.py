# apps/core/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class SiteSettings(TimeStampedModel):
    site_name = models.CharField(max_length=100, default="Bematore")
    tagline = models.CharField(max_length=200, blank=True, help_text="A short tagline for the site")
    site_description = models.TextField()
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    
    # Contact Information
    contact_email = models.EmailField()
    support_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    
    # Social Media
    social_facebook = models.URLField(blank=True)
    social_twitter = models.URLField(blank=True)
    social_instagram = models.URLField(blank=True)
    social_linkedin = models.URLField(blank=True)
    social_tiktok = models.URLField(blank=True)
    
    # Analytics and SEO
    google_analytics_id = models.CharField(max_length=50, blank=True)
    meta_keywords = models.TextField(blank=True, help_text="Comma separated keywords for SEO")
    meta_description = models.TextField(blank=True, help_text="Site meta description for SEO")
    
    # App Store Links
    app_store_link = models.URLField(blank=True, help_text="iOS App Store link")
    play_store_link = models.URLField(blank=True, help_text="Google Play Store link")
    
    class Meta:
        verbose_name = _("Site Settings")
        verbose_name_plural = _("Site Settings")
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        if SiteSettings.objects.exists() and not self.pk:
            raise ValidationError("Only one Site Settings instance is allowed")
        return super().save(*args, **kwargs)

class FAQ(TimeStampedModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=100, blank=True, help_text="Category for grouping FAQs")
    
    class Meta:
        ordering = ['category', 'order']
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
    
    def __str__(self):
        return self.question

class Contact(TimeStampedModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    is_read = models.BooleanField(default=False)
    responded = models.BooleanField(default=False)
    responded_at = models.DateTimeField(blank=True, null=True)
    responded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        blank=True, null=True, 
        related_name='contact_responses'
    )
    
    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    def mark_as_responded(self, user):
        self.responded = True
        self.responded_at = timezone.now()
        self.responded_by = user
        self.save()

class Newsletter(TimeStampedModel):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    confirmation_token = models.CharField(max_length=100, blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Newsletter Subscriber")
        verbose_name_plural = _("Newsletter Subscribers")
    
    def __str__(self):
        return self.email
    
    def confirm_subscription(self):
        self.confirmed = True
        self.confirmed_at = timezone.now()
        self.save()

class Testimonial(TimeStampedModel):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.name

class TeamMember(TimeStampedModel):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=150)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")
        ordering = ['order']
    
    def __str__(self):
        return self.name

class Partner(TimeStampedModel):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partners/')
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    partner_type = models.CharField(
        max_length=50, 
        choices=[
            ('health', 'Healthcare'),
            ('tech', 'Technology'),
            ('academic', 'Academic'),
            ('ngo', 'NGO'),
            ('government', 'Government'),
            ('corporate', 'Corporate')
        ],
        default='health'
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")
        ordering = ['partner_type', 'order']
    
    def __str__(self):
        return self.name