from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.exceptions import PermissionDenied


# class RoleRequiredMixin(LoginRequiredMixin):
#
#     allowed_roles = []
#
#     def dispatch(self, request, *args, **kwargs):
#
#         if request.user.role not in self.allowed_roles:
#             raise PermissionDenied
#
#         return super().dispatch(request, *args, **kwargs)
class RoleRequiredMixin(AccessMixin):

    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if self.allowed_roles and request.user.role not in self.allowed_roles:
            raise PermissionDenied("You do not have permission to access this page.")

        return super().dispatch(request, *args, **kwargs)