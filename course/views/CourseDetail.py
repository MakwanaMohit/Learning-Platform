from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from django.db.models import Prefetch

from accounts.views import RoleRequiredMixin
from course.forms.createUnit import UnitForm
from course.models import Course, Unit, Chapter
from course.views import is_course_owner
from course.views.mixins import CourseChangeAccessMixin


class CourseDetailView(CourseChangeAccessMixin,DetailView):
    model = Course
    slug_url_kwarg = "course_slug"
    context_object_name = "course"
    template_name = "course/course_detail.html"
    allowed_roles = ["mentor"]

    def get_queryset(self):
        return (
            Course.objects
            .select_related("category", "mentor")
            .prefetch_related("mentors")
        )


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        is_mentor = is_course_owner(user,course)

        units = (
            Unit.objects
            .filter(course=course)
            .only("id", "title", "slug", "order", "is_locked")
            .prefetch_related(
                Prefetch(
                    "chapters",
                    queryset=(
                        Chapter.objects
                        .only("id", "name", "slug", "order")
                        .order_by("order")
                    )
                )
            )
            .order_by("order")
        )

        context["units"] = units

        context["is_mentor"] = is_mentor

        if is_mentor:
            next_order = units.count() + 1
            context["unit_form"] = UnitForm(initial={"order": next_order})

        return context