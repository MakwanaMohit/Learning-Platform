from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from course.forms import CourseForm
from course.models import Course
from accounts.views import RoleRequiredMixin

from django.views import View
from django.http import JsonResponse
from django.utils.text import slugify


class CreateTagCatView(View):
    model = None  # passed from urls

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")

        if not name:
            return JsonResponse({"error": "Name is required"}, status=400)

        obj, created = self.model.objects.get_or_create(
            name=name,
            defaults={"slug": slugify(name)}
        )

        return JsonResponse({
            "id": obj.id,
            "name": obj.name,
            "created": created
        })

class CourseCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "course/course_form.html"
    success_url = reverse_lazy("course:Index Page")
    allowed_roles = ['mentor']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.mentor = self.request.user
        return super().form_valid(form)