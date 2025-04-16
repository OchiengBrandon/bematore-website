from django.contrib import admin
from .models import Solution, Feature

class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'is_active', 'order')
    list_filter = ('platform', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [FeatureInline]

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'solution', 'order')
    list_filter = ('solution',)
    search_fields = ('name', 'description')