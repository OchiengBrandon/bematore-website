# apps/core/context_processors.py

from .models import SiteSettings

def site_settings(request):
    try:
        settings = SiteSettings.objects.first()  # Get the first (and likely only) settings instance
    except SiteSettings.DoesNotExist:
        settings = None

    return {
        'site_name': settings.site_name if settings else 'Default Site Name',
        'site_description': settings.site_description if settings else 'Default description.',
        'maintenance_mode': settings.maintenance_mode if settings else False,
        'contact_email': settings.contact_email if settings else 'contact@example.com',
        'phone_number': settings.phone_number if settings else 'N/A',
        'address': settings.address if settings else 'N/A',
        'social_facebook': settings.social_facebook if settings else '',
        'social_twitter': settings.social_twitter if settings else '',
        'social_instagram': settings.social_instagram if settings else '',
        'social_linkedin': settings.social_linkedin if settings else '',
        'google_analytics_id': settings.google_analytics_id if settings else '',
    }