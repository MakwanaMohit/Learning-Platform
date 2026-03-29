from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from accounts.views import RoleRequiredMixin
from course.forms import UnitForm
from course.forms.createChapter import ChapterForm
from course.models import Course, Unit, Chapter
from course.views import is_course_owner
from django.views.generic import UpdateView, CreateView
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.http import HttpResponse

from course.views.mixins import UnitChangeAccessMixin, ChapterChangeAccessMixin


class ChapterCreateView(UnitChangeAccessMixin, CreateView):
    model = Chapter
    form_class = ChapterForm
    template_name = "course/chapter_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial['order'] = self.unit.chapters.count() + 1
        return initial

    def form_valid(self, form):
        form.instance.unit = self.unit
        response =  super().form_valid(form)
        messages.success(self.request, "Chapter created successfully")
        return response

    def get_success_url(self):
        return self.unit.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'unit': self.unit,'course':self.course})
        return context

class ChapterUpdateView(LoginRequiredMixin, RoleRequiredMixin, ChapterChangeAccessMixin, UpdateView):
    model = Chapter
    form_class = ChapterForm
    allowed_roles = ["mentor"]

    def get(self, request, *args, **kwargs):
        form = self.get_form()

        html = render_to_string(
            "course/partials/unit_form.html",
            {
                "form": form,
                "url" : reverse('course:chapter_change',kwargs={"course_slug":self.course.slug,"unit_slug":self.unit.slug,"chapter_slug":self.chapter.slug}),
                "page_redirect":request.GET.get("page-redirect",False)
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
        if self.request.POST.get("page-redirect"):
            return self.chapter.get_absolute_url()
        return self.unit.get_absolute_url()