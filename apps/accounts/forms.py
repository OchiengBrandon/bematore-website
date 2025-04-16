# apps/accounts/forms.py

from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4})
        }

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['preferred_language', 'notification_preferences']

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['notification_preferences']
        widgets = {
            'notification_preferences': forms.CheckboxSelectMultiple
        }