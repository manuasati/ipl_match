from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from django.core.exceptions import ValidationError

from .models import *


DEPARTMENTS = [("", "Select Department")]
DEPARTMENTS += [ (obj.id, obj.name) for obj in Department.objects.all()]

class CreateUserForm(UserCreationForm):
    department = forms.CharField(
        max_length=100,
        widget=forms.Select(choices=DEPARTMENTS, attrs={'class':'form-control'}),
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        if email.split('@')[-1] != "amadeus.com":
            raise  ValidationError("please enter amadeus email!")
        return email


