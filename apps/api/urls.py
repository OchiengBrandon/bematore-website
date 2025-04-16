from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('keys/', views.api_key_list, name='api_key_list'),
    path('keys/<int:pk>/', views.api_key_detail, name='api_key_detail'),
    path('logs/', views.api_log_list, name='api_log_list'),
]