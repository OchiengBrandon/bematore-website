# apps/blog/urls.py

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Post views
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('drafts/', views.DraftsListView.as_view(), name='drafts_list'),
    
    # Category views
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:slug>/', views.CategoryPostListView.as_view(), name='category_detail'),
    path('category/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<slug:slug>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('category/<slug:slug>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Tag views
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tag/<slug:slug>/', views.TagPostListView.as_view(), name='tag_detail'),
    path('tag/create/', views.TagCreateView.as_view(), name='tag_create'),
    path('tag/<slug:slug>/edit/', views.TagUpdateView.as_view(), name='tag_edit'),
    path('tag/<slug:slug>/delete/', views.TagDeleteView.as_view(), name='tag_delete'),
    
    # Comment actions
    path('comment/<int:comment_id>/approve/', views.approve_comment, name='approve_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Subscription
    path('subscribe/', views.subscribe, name='subscribe'),
]