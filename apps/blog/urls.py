from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('categories/', views.category_list, name='category_list'),
    path('tags/', views.tag_list, name='tag_list'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/<slug:slug>/', views.post_detail, name='post_detail'),
    path('posts/<slug:post_slug>/comment/', views.add_comment, name='add_comment'),
]