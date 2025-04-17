# apps/core/context_processors.py
from apps.core.models import SiteSettings

def site_settings(request):
    """
    Context processor to make site settings available in all templates.
    Returns the single SiteSettings instance or None if it doesn't exist.
    """
    try:
        # Since SiteSettings is designed to have only one instance,
        # we can use first() instead of filtering by an is_active field
        settings = SiteSettings.objects.first()
    except Exception:
        # Handle any unexpected errors to prevent template rendering issues
        settings = None
    
    return {'site_settings': settings}