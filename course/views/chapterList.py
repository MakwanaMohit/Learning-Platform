from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from course.forms.createChapter import ChapterForm
from course.models import Chapter, Unit
from course.views import can_access_unit, is_course_owner


class ChapterListView(ListView):
    model = Chapter
    context_object_name = "chapters"
    template_name = 'course/chapter_list.html'

    def get_queryset(self):
        user = self.request.user

        self.unit = get_object_or_404(
            Unit.objects.select_related("course").only(
                "id",
                "is_locked",
                "course__id",
                "course__status",
                "course__slug",
                "course__mentor_id",
            ),
            slug=self.kwargs["unit_slug"],
            course__slug=self.kwargs["course_slug"],
        )

        course = self.unit.course

        has_access = can_access_unit(user, self.unit)

        filters = {
            "unit_id": self.unit.id,
            "is_locked": False,
        }

        if not has_access:
            filters["is_preview"] = True

        return Chapter.objects.filter(**filters).only(
            "id",
            "name",
            "slug",
            "is_preview",
            "is_locked",
            'description',
            'duration',
            "unit_id",
            'order',
        ).order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unit"] = self.unit
        context["course"] = self.unit.course
        context['is_mentor'] = is_course_owner(self.request.user, self.unit.course)
        context['chapter_form'] = ChapterForm()
        context['chapter_form'].initial['order'] = self.unit.chapters.count() + 1
        return context