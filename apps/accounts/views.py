# apps/accounts/views.py

from django.views.generic import UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import UserUpdateForm, UserProfileUpdateForm, UserSettingsForm
from .models import User, UserProfile

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = UserProfileUpdateForm(
                self.request.POST,
                instance=self.request.user.userprofile
            )
        else:
            context['profile_form'] = UserProfileUpdateForm(
                instance=self.request.user.userprofile
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(self.request, 'Profile updated successfully!')
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))