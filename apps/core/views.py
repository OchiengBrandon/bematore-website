# apps/core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, FormView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from django.db.models import Q

from .models import FAQ, SiteSettings, Contact, Newsletter, Testimonial, TeamMember, Partner
from .forms import ContactForm, NewsletterSubscriptionForm, SearchForm, FAQFilterForm
import uuid

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_settings'] = SiteSettings.objects.first()
        context['faqs'] = FAQ.objects.filter(is_active=True).order_by('order')[:5]
        context['testimonials'] = Testimonial.objects.filter(is_active=True, is_featured=True)[:3]
        context['team_members'] = TeamMember.objects.filter(is_active=True).order_by('order')[:4]
        context['partners'] = Partner.objects.filter(is_active=True).order_by('order')[:6]
        context['newsletter_form'] = NewsletterSubscriptionForm()
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_settings'] = SiteSettings.objects.first()
        context['team_members'] = TeamMember.objects.filter(is_active=True).order_by('order')
        return context

class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact_success')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_settings'] = SiteSettings.objects.first()
        return context
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thank you for your message. We'll respond as soon as possible.")
        return super().form_valid(form)

class ContactSuccessView(TemplateView):
    template_name = 'core/contact_success.html'

class FAQListView(ListView):
    model = FAQ
    template_name = 'core/faq.html'
    context_object_name = 'faqs'
    
    def get_queryset(self):
        queryset = FAQ.objects.filter(is_active=True)
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by('category', 'order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_settings'] = SiteSettings.objects.first()
        context['filter_form'] = FAQFilterForm(self.request.GET)
        
        # Group FAQs by category
        faqs_by_category = {}
        for faq in context['faqs']:
            category = faq.category or 'General'
            if category not in faqs_by_category:
                faqs_by_category[category] = []
            faqs_by_category[category].append(faq)
        
        context['faqs_by_category'] = faqs_by_category
        return context

class NewsletterSubscriptionView(View):
    def post(self, request):
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            # Check if already exists
            email = form.cleaned_data['email']
            if Newsletter.objects.filter(email=email).exists():
                if request.is_ajax():
                    return JsonResponse({
                        'success': False,
                        'message': 'You are already subscribed to our newsletter.'
                    })
                messages.info(request, 'You are already subscribed to our newsletter.')
            else:
                subscriber = form.save(commit=False)
                subscriber.confirmation_token = str(uuid.uuid4())
                subscriber.save()
                
                # Here you would typically send a confirmation email
                # but we'll just show a success message for now
                
                if request.is_ajax():
                    return JsonResponse({
                        'success': True,
                        'message': 'Thank you for subscribing to our newsletter!'
                    })
                messages.success(request, 'Thank you for subscribing to our newsletter!')
        else:
            if request.is_ajax():
                return JsonResponse({
                    'success': False,
                    'message': 'Please provide a valid email address.'
                })
            messages.error(request, 'Please provide a valid email address.')
        
        # If not AJAX, redirect back
        return redirect(request.META.get('HTTP_REFERER', 'core:home'))

class SearchResultsView(TemplateView):
    template_name = 'core/search_results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '')
        context['query'] = query
        context['site_settings'] = SiteSettings.objects.first()
        
        if query:
            # Search in FAQs
            faqs = FAQ.objects.filter(
                Q(question__icontains=query) | Q(answer__icontains=query),
                is_active=True
            )
            context['faqs'] = faqs
            
            # Here you could add more search results from other models
            
            context['total_results'] = faqs.count()
        else:
            context['total_results'] = 0
            
        context['search_form'] = SearchForm(initial={'query': query})
        return context

class TeamView(ListView):
    model = TeamMember
    template_name = 'core/team.html'
    context_object_name = 'team_members'
    
    def get_queryset(self):
        return TeamMember.objects.filter(is_active=True).order_by('order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_settings'] = SiteSettings.objects.first()
        return context

class PartnersView(ListView):
    model = Partner
    template_name = 'core/partners.html'
    context_object_name = 'partners'
    
    def get_queryset(self):
        return Partner.objects.filter(is_active=True).order_by('partner_type', 'order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_settings'] = SiteSettings.objects.first()
        
        # Group partners by type
        partners_by_type = {}
        for partner in context['partners']:
            partner_type = partner.get_partner_type_display()
            if partner_type not in partners_by_type:
                partners_by_type[partner_type] = []
            partners_by_type[partner_type].append(partner)
        
        context['partners_by_type'] = partners_by_type
        return context

class TestimonialsView(ListView):
    model = Testimonial
    template_name = 'core/testimonials.html'
    context_object_name = 'testimonials'
    paginate_by = 6
    
    def get_queryset(self):
        return Testimonial.objects.filter(is_active=True).order_by('-is_featured', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_settings'] = SiteSettings.objects.first()
        return context