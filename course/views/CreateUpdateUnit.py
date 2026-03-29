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

from course.views.mixins import UnitPageMixin


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




class UnitUpdateView(LoginRequiredMixin, RoleRequiredMixin,  UnitPageMixin, UpdateView):
    model = Unit
    form_class = UnitForm
    allowed_roles = ["mentor"]

    def get_object(self, queryset=None):
        return super().get_object()

    def dispatch(self, request, *args, **kwargs):

        if not is_course_owner(request.user, self.course):
            raise PermissionDenied("Not allowed")

        return super().dispatch(request, *args, **kwargs)

    # 🔹 AJAX GET → return rendered form
    def get(self, request, *args, **kwargs):
        form = self.get_form()

        html = render_to_string(
            "course/partials/unit_form.html",
            {
                "form": form,
                "url" : reverse('course:unit_change',kwargs={"course_slug":self.course.slug,"unit_slug":self.unit.slug}),
                "unit_page_redirect":request.GET.get("unit-page-redirect",False)
            },
            request=request
        )
        return HttpResponse(html)

    # 🔹 POST → normal update
    def form_valid(self, form):
        messages.success(self.request, "Unit updated successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error updating unit")
        return super().form_invalid(form)

    def get_success_url(self):
        if self.request.POST.get("unit-page-redirect"):
            return self.unit.get_absolute_url()
        return self.course.get_absolute_url()