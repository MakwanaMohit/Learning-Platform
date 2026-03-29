from django.contrib import admin
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, include

from accounts.views import RoleBasedLoginView, AccountRedirectView, UserRegistrationView

app_name = 'accounts'
urlpatterns = [
    path("logout/", LogoutView.as_view(next_page="accounts:redirect"), name="logout"),
    path("login/", RoleBasedLoginView.as_view(), name="login"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("redirect/", AccountRedirectView.as_view(), name="redirect"),
]