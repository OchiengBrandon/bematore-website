# apps/core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteSettings, FAQ, Contact, Newsletter, 
    Testimonial, TeamMember, Partner
)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'tagline', 'site_description', 'logo', 'favicon')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'support_email', 'phone_number', 'alternate_phone', 'address')
        }),
        ('Social Media', {
            'fields': ('social_facebook', 'social_twitter', 'social_instagram', 'social_linkedin', 'social_tiktok')
        }),
        ('SEO & Analytics', {
            'fields': ('google_analytics_id', 'meta_keywords', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('App Links', {
            'fields': ('app_store_link', 'play_store_link')
        }),
    )
    
    def has_add_permission(self, request):
        return SiteSettings.objects.count() == 0

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('question', 'answer', 'category')
    list_editable = ('order', 'is_active')
    ordering = ('category', 'order')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read', 'responded')
    list_filter = ('is_read', 'responded', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'responded_at', 'responded_by')
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_responded']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected contacts as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected contacts as unread"
    
    def mark_as_responded(self, request, queryset):
        for contact in queryset:
            contact.mark_as_responded(request.user)
    mark_as_responded.short_description = "Mark selected contacts as responded"

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'confirmed', 'created_at')
    list_filter = ('is_active', 'confirmed', 'created_at')
    search_fields = ('email', 'name')
    readonly_fields = ('created_at', 'confirmed_at')
    
    actions = ['mark_as_confirmed', 'mark_as_unconfirmed', 'mark_as_active', 'mark_as_inactive']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(confirmed=True, confirmed_at=timezone.now())
    mark_as_confirmed.short_description = "Mark selected subscribers as confirmed"
    
    def mark_as_unconfirmed(self, request, queryset):
        queryset.update(confirmed=False, confirmed_at=None)
    mark_as_unconfirmed.short_description = "Mark selected subscribers as unconfirmed"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
    mark_as_active.short_description = "Mark selected subscribers as active"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_as_inactive.short_description = "Mark selected subscribers as inactive"

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'company', 'rating', 'is_featured', 'is_active')
    list_filter = ('rating', 'is_featured', 'is_active')
    search_fields = ('name', 'position', 'company', 'content')
    list_editable = ('is_featured', 'is_active')
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.avatar.url)
        return "(No Avatar)"
    avatar_preview.short_description = "Avatar Preview"

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'order', 'is_active', 'photo_preview')
    list_filter = ('is_active',)
    search_fields = ('name', 'position', 'bio')
    list_editable = ('order', 'is_active')
    ordering = ('order',)
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.photo.url)
        return "(No Photo)"
    photo_preview.short_description = "Photo Preview"

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner_type', 'order', 'is_active', 'logo_preview')
    list_filter = ('partner_type', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_active')
    ordering = ('partner_type', 'order')
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.logo.url)
        return "(No Logo)"
    logo_preview.short_description = "Logo Preview"