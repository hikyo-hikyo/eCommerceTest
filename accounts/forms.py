
from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User


class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'role-radio'}),
        label="Register as"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']
