from django.urls import path
from . import views

app_name = 'solutions'

urlpatterns = [
    path('', views.solution_list, name='solution_list'),
    path('<slug:slug>/', views.solution_detail, name='solution_detail'),
]