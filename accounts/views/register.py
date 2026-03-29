from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login

from accounts.models import User
from accounts.forms import UserRegistrationForm


class UserRegistrationView(CreateView):

    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:redirect")

    def form_valid(self, form):

        response = super().form_valid(form)

        # Auto login after registration
        login(self.request, self.object)

        return response