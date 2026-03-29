from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View

from accounts.views.mixins import RoleRequiredMixin

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from accounts.views.mixins import RoleRequiredMixin


class StudentDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """
    Student Dashboard View
    """

    template_name = "student/index.html"

    allowed_roles = ["student"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["page_title"] = "Student Dashboard"
        context["user"] = self.request.user

        return context

    def dispatch(self, request, *args, **kwargs):

        # Optional welcome message
        if request.user.is_authenticated:
            messages.success(request, f"Welcome, {request.user.first_name or request.user.username}!")

        return super().dispatch(request, *args, **kwargs)