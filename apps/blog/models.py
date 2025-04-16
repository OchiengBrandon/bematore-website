# apps/blog/models.py

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from apps.core.models import TimeStampedModel
from apps.accounts.models import User
from ckeditor_uploader.fields import RichTextUploadingField  # Upgraded for image uploads
from taggit.managers import TaggableManager
from django.db.models import Count


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog/categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)  # Add this line

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def post_count(self):
        return self.post_set.filter(status='published').count()


class Tag(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PostManager(models.Manager):
    def published(self):
        return self.filter(status='published', published_at__lte=timezone.now())
        
    def get_popular_posts(self, limit=5):
        return self.published().order_by('-views_count')[:limit]
        
    def get_related_posts(self, post, limit=3):
        # Get related posts by tags
        post_tags_ids = post.tags.values_list('id', flat=True)
        related_posts = self.published().filter(tags__in=post_tags_ids).exclude(id=post.id)
        related_posts = related_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-published_at')[:limit]
        return related_posts


class Post(TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    FEATURED_CHOICES = [
        ('not_featured', 'Not Featured'),
        ('featured', 'Featured'),
        ('hero', 'Hero (Main Feature)'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = RichTextUploadingField()
    featured_image = models.ImageField(upload_to='blog/posts/%Y/%m/')
    thumbnail = models.ImageField(upload_to='blog/thumbnails/%Y/%m/', blank=True, null=True,
                                  help_text="Small image used in post listings")
    excerpt = models.TextField(help_text="A short summary of the post content")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured = models.CharField(max_length=15, choices=FEATURED_CHOICES, default='not_featured')
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta_description = models.CharField(max_length=160, blank=True, 
                                       help_text="Description for SEO purposes")
    meta_keywords = models.CharField(max_length=255, blank=True,
                                   help_text="Keywords for SEO (comma-separated)")
    views_count = models.PositiveIntegerField(default=0)
    allow_comments = models.BooleanField(default=True)
    
    objects = PostManager()
    
    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['status']),
            models.Index(fields=['featured']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when post is published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
            
        # Generate thumbnail from featured image if not provided
        # (This is a placeholder - actual implementation would require PIL/Pillow)
        if self.featured_image and not self.thumbnail:
            # You would implement actual thumbnail generation here
            self.thumbnail = self.featured_image
            
        super().save(*args, **kwargs)
        
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])
        
    @property
    def comment_count(self):
        return self.comments.filter(is_approved=True).count()
    
    @property
    def reading_time(self):
        """Estimate reading time in minutes"""
        word_count = len(self.content.split())
        minutes = word_count // 200  # Average reading speed
        return max(1, minutes)  # At least 1 minute


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, 
                              related_name='replies')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'
        
    def get_absolute_url(self):
        return f"{self.post.get_absolute_url()}#comment-{self.id}"
        
    @property
    def is_reply(self):
        return self.parent is not None


# Additional models for enhanced functionality

class PostView(models.Model):
    """Track individual post views with user info when available"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        # Prevent duplicate logging in short time period
        unique_together = ['post', 'ip_address', 'user_agent', 'viewed_at']


class Subscription(TimeStampedModel):
    """Email subscriptions for blog updates"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    confirmation_token = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.email