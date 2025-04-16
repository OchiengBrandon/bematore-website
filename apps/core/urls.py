# apps/core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success/', views.ContactSuccessView.as_view(), name='contact_success'),
    path('faq/', views.FAQListView.as_view(), name='faq'),
    path('team/', views.TeamView.as_view(), name='team'),
    path('partners/', views.PartnersView.as_view(), name='partners'),
    path('testimonials/', views.TestimonialsView.as_view(), name='testimonials'),
    path('search/', views.SearchResultsView.as_view(), name='search'),
    path('newsletter/subscribe/', views.NewsletterSubscriptionView.as_view(), name='newsletter_subscribe'),
]