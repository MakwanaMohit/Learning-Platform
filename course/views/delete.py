from http import HTTPMethod

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from accounts.views import RoleRequiredMixin
from course.models import Course
from course.views import is_course_owner
from course.views.mixins import UnitChangeAccessMixin, CourseChangeAccessMixin, ChapterChangeAccessMixin


class CourseDeleteView(LoginRequiredMixin, RoleRequiredMixin, CourseChangeAccessMixin, View):
    allowed_roles = ["mentor"]

    def get(self, request, course_slug, chapter_slug):
        return HttpResponseNotAllowed(['POST'])

    def post(self, request, course_slug):
        course = self.get_object()
        confirm_name = request.POST.get("confirm_name")

        if confirm_name != course.title:
            messages.error(request, "Please type the course name in the textfield to delete the course")
            return redirect(course.get_absolute_url())

        course.delete()
        messages.success(request, "Course deleted successfully.")

        return redirect("course:Index Page")

class UnitDeleteView(RoleRequiredMixin, LoginRequiredMixin, UnitChangeAccessMixin, View):
    allowed_roles = ["mentor"]

    def get(self, request, course_slug, chapter_slug):
        return HttpResponseNotAllowed(['POST'])

    def post(self, request, *args, **kwargs):

        confirm_name = request.POST.get("confirm_name")

        if confirm_name != self.unit.title:
            return JsonResponse({"error": "Name mismatch"}, status=400)

        self.unit.delete()

        return JsonResponse({"success": True})

class ChapterDeleteView(RoleRequiredMixin, LoginRequiredMixin, ChapterChangeAccessMixin, View):
    allowed_roles = ["mentor"]

    def get(self, request, course_slug, chapter_slug):
        return HttpResponseNotAllowed(['POST'])

    def post(self, request, *args, **kwargs):

        confirm_name = request.POST.get("confirm_name")

        if confirm_name != self.chapter.name:
            return JsonResponse({"error": "Name mismatch"}, status=400)

        self.chapter.delete()

        return JsonResponse({"success": True})