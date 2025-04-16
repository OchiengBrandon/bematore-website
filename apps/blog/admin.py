# apps/blog/admin.py

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count

from .models import Category, Tag, Post, Comment, PostView, Subscription


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count', 'image_preview', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    actions = ['activate_categories', 'deactivate_categories']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image"
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(posts_count=Count('post'))  # Changed from post_count to posts_count
        return queryset

    def post_count(self, obj):
        return obj.posts_count  # Changed to access the annotation instead of the property
    post_count.admin_order_field = 'posts_count'  # Changed sorting field
    post_count.short_description = 'Posts'
    
    def activate_categories(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} categories activated successfully.")
    activate_categories.short_description = "Activate selected categories"
    
    def deactivate_categories(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} categories deactivated successfully.")
    deactivate_categories.short_description = "Deactivate selected categories"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(post_count=Count('post'))
        return queryset
    
    def post_count(self, obj):
        return obj.post_count
    post_count.admin_order_field = 'post_count'
    post_count.short_description = 'Posts'


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('author', 'content', 'is_approved', 'created_at')
    readonly_fields = ('author', 'content', 'created_at')
    can_delete = True
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'author', 'category', 'status', 'featured', 'image_preview', 
                    'comment_count', 'views_count', 'published_at')
    list_filter = ('status', 'featured', 'category', 'author', 'allow_comments', 'published_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    filter_horizontal = ('tags',)
    raw_id_fields = ('author',)
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    actions = ['publish_posts', 'unpublish_posts', 'feature_posts', 'unfeature_posts']
    inlines = [CommentInline]
    
    fieldsets = (
        ('Post Content', {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt')
        }),
        ('Media', {
            'fields': ('featured_image', 'thumbnail'),
            'classes': ('collapse',),
        }),
        ('Categorization', {
            'fields': ('category', 'tags'),
        }),
        ('Publishing', {
            'fields': ('status', 'featured', 'published_at', 'allow_comments'),
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Statistics', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def image_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="50" height="30" style="object-fit: cover;" />', obj.thumbnail.url)
        elif obj.featured_image:
            return format_html('<img src="{}" width="50" height="30" style="object-fit: cover;" />', obj.featured_image.url)
        return "No Image"
    image_preview.short_description = "Image"
    
    def comment_count(self, obj):
        return obj.comment_count
    comment_count.short_description = 'Comments'
    
    def publish_posts(self, request, queryset):
        queryset.update(status='published')
        self.message_user(request, f"{queryset.count()} posts published successfully.")
    publish_posts.short_description = "Publish selected posts"
    
    def unpublish_posts(self, request, queryset):
        queryset.update(status='draft')
        self.message_user(request, f"{queryset.count()} posts unpublished successfully.")
    unpublish_posts.short_description = "Unpublish selected posts"
    
    def feature_posts(self, request, queryset):
        queryset.update(featured='featured')
        self.message_user(request, f"{queryset.count()} posts featured successfully.")
    feature_posts.short_description = "Mark selected posts as featured"
    
    def unfeature_posts(self, request, queryset):
        queryset.update(featured='not_featured')
        self.message_user(request, f"{queryset.count()} posts unfeatured successfully.")
    unfeature_posts.short_description = "Remove featured status from selected posts"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_title', 'author', 'short_content', 'is_approved', 'is_reply', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__username', 'author__email', 'post__title')
    raw_id_fields = ('post', 'author', 'parent')
    readonly_fields = ('ip_address', 'user_agent', 'created_at')
    actions = ['approve_comments', 'unapprove_comments']
    
    def post_title(self, obj):
        return obj.post.title
    post_title.admin_order_field = 'post__title'
    post_title.short_description = 'Post'
    
    def short_content(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    short_content.short_description = 'Content'
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} comments approved successfully.")
    approve_comments.short_description = "Approve selected comments"
    
    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} comments unapproved successfully.")
    unapprove_comments.short_description = "Unapprove selected comments"


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'ip_address', 'user_agent', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('post__title', 'user__username', 'ip_address')
    raw_id_fields = ('post', 'user')
    date_hierarchy = 'viewed_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email', 'name')
    readonly_fields = ('confirmation_token',)
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} subscriptions activated successfully.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} subscriptions deactivated successfully.")
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"