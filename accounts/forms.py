from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):

    ROLE_CHOICES = (
        ("student", "Student"),
        ("mentor", "Mentor"),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)

        # Prevent admin creation via public registration
        if user.role == "admin":
            raise forms.ValidationError("Invalid role")

        if commit:
            user.save()

        return user