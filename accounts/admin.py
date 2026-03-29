
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Production-ready admin configuration for custom User model
    """

    model = User

    # Columns shown in user list
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )

    # Filters on right sidebar
    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )

    # Fields shown in user edit page
    fieldsets = (
        (None, {"fields": ("username", "password")}),

        (_("Personal info"), {
            "fields": ("first_name", "last_name", "email")
        }),

        (_("Role & Permissions"), {
            "fields": (
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),

        (_("Important dates"), {
            "fields": ("last_login", "date_joined")
        }),
    )

    # Fields shown when creating new user
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email",
                "role",
                "password1",
                "password2",
                "is_active",
                "is_staff",
            ),
        }),
    )

    # Search functionality
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    # Sorting
    ordering = ("username",)

    # Readonly fields
    readonly_fields = ("last_login", "date_joined")

    # Pagination
    list_per_page = 25