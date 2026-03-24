from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse



class RoleRequiredMixin(AccessMixin):
    allowed_roles = []

    def handle_no_permission(self):
        # 🔹 AJAX / fetch request
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {"error": "Authentication required"},
                status=401
            )

        return super().handle_no_permission()

    def dispatch(self, request, *args, **kwargs):

        # 🔐 Not authenticated
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # 🔐 Role check
        if self.allowed_roles and request.user.role not in self.allowed_roles:

            # AJAX response
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {"error": "Permission denied"},
                    status=403
                )

            raise PermissionDenied("You do not have permission to access this page.")

        return super().dispatch(request, *args, **kwargs)