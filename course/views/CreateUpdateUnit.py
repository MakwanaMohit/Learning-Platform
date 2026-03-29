from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from accounts.views import RoleRequiredMixin
from course.forms import UnitForm
from course.models import Course, Unit
from course.views import is_course_owner
from django.views.generic import UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.http import HttpResponse

from course.views.mixins import UnitChangeAccessMixin


class UnitCreateView(View):

    def post(self, request, course_slug):
        course = get_object_or_404(
            Course.objects.only("id", "mentor_id"),
            slug=course_slug
        )

        if not is_course_owner(request.user, course):
            return JsonResponse({"error": "Permission denied"}, status=403)

        form = UnitForm(request.POST)

        if form.is_valid():
            unit = form.save(commit=False)
            unit.course = course

            if unit.order is None:
                unit.order = (
                    Unit.objects
                    .filter(course=course)
                    .count() + 1
                )
            if unit.order < 0:
                unit.order = 0


            unit.save()

            return JsonResponse({
                "id": unit.id,
                "title": unit.title,
                "slug": unit.slug,
                "order": unit.order
            })

        return JsonResponse({"errors": form.errors}, status=400)




class UnitUpdateView(LoginRequiredMixin, RoleRequiredMixin, UnitChangeAccessMixin, UpdateView):
    model = Unit
    form_class = UnitForm
    allowed_roles = ["mentor"]

    # 🔹 AJAX GET → return rendered form
    def get(self, request, *args, **kwargs):
        form = self.get_form()

        html = render_to_string(
            "course/partials/unit_form.html",
            {
                "form": form,
                "url" : reverse('course:unit_change',kwargs={"course_slug":self.course.slug,"unit_slug":self.unit.slug}),
                "page_redirect":request.GET.get("page-redirect",False)
            },
            request=request
        )
        return HttpResponse(html)

    def get_success_url(self):
        if self.request.POST.get("page-redirect"):
            return self.unit.get_absolute_url()
        return self.course.get_absolute_url()