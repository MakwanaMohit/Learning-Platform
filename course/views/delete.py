from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from accounts.views import RoleRequiredMixin
from course.models import Course
from course.views import is_course_owner
from course.views.mixins import UnitPageMixin, CourseChangeAccessMixin


class CourseDeleteView(LoginRequiredMixin, RoleRequiredMixin, CourseChangeAccessMixin, View):
    allowed_roles = ["mentor"]

    def post(self, request, course_slug):
        course = self.get_object()
        confirm_name = request.POST.get("confirm_name")

        if confirm_name != course.title:
            messages.error(request, "Please type the course name in the textfield to delete the course")
            return redirect(course.get_absolute_url())

        course.delete()
        messages.success(request, "Course deleted successfully.")

        return redirect("course:Index Page")

class UnitDeleteView(RoleRequiredMixin, LoginRequiredMixin, UnitPageMixin, View):
    allowed_roles = ["mentor"]

    def post(self, request, *args, **kwargs):


        if not is_course_owner(request.user,self.course):
            raise PermissionDenied("Not allowed")

        confirm_name = request.POST.get("confirm_name")

        if confirm_name != self.unit.title:
            return JsonResponse({"error": "Name mismatch"}, status=400)

        self.unit.delete()

        return JsonResponse({"success": True})