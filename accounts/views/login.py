from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.views.generic import RedirectView


class RoleBasedLoginView(LoginView):

    template_name = "accounts/login.html"

    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):

        redirect_url = self.get_redirect_url()

        if redirect_url:
            return redirect_url

        return self.request.user.get_dashboard_url()

# accounts/views.py


class AccountRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        next_url = self.request.GET.get("next")

        if next_url:
            return next_url
        user = self.request.user
        try:
            return user.get_dashboard_url()
        except:
            return reverse("core:home")