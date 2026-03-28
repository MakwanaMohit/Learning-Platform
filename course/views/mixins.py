from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from course.models import Unit, Chapter, Course
from course.views import is_course_owner, can_access_course


class UnitPageMixin2:
    def get_object(self):
        return get_object_or_404(
            Unit.objects.select_related("course"),
            slug=self.kwargs.get("unit_slug"),
            course__slug=self.kwargs.get("course_slug"),
        )

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if not hasattr(self, "object"):
            self.object = self.get_object()

        self.unit = self.object
        self.course = self.unit.course

class ChapterPageMixin2:
    def get_object(self):
        return get_object_or_404(
            Chapter.objects.select_related("unit__course"),
            slug=self.kwargs.get("chapter_slug"),
            unit__slug=self.kwargs.get("unit_slug"),
            unit__course__slug=self.kwargs.get("course_slug"),
        )

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if not hasattr(self, "object"):
            self.object = self.get_object()

        self.chapter = self.object
        self.unit = self.chapter.unit
        self.course = self.unit.course

class CourseChangeAccessMixin:
    course_slug_url_kwarg = "course_slug"
    course_queryset = Course.objects.all()

    def get_object(self):
        slug = self.kwargs.get(self.course_slug_url_kwarg)
        course = get_object_or_404(self.course_queryset, slug=slug)
        if not is_course_owner(self.request.user, course):
            raise PermissionDenied("You do not have access to this course.")
        return course

class ChapterChangeAccessMixin:
    def handle_no_permissions(self,request):
        return PermissionDenied("You Don't have permissions to access")

    def get_object(self):
        self.chapter = get_object_or_404(
            Chapter.objects.select_related("unit__course").only(
                "id", "name", "slug", "unit_id",

                "unit__id", "unit__slug", "unit__course_id",

                "unit__course__id",
                "unit__course__slug",
                "unit__course__mentor_id",
            ),
            slug=self.kwargs["chapter_slug"],
            unit__slug=self.kwargs["unit_slug"],
            unit__course__slug=self.kwargs["course_slug"],
        )

        self.unit = self.chapter.unit
        self.course = self.unit.course

        return self.chapter

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not is_course_owner(request.user, self.course):
            self.handle_no_permissions(request)

        return super().dispatch(request, *args, **kwargs)

class UnitChangeAccessMixin:
    def handle_no_permissions(self,request):
        return PermissionDenied("You Don't have permissions to access")

    def get_object(self):
        self.unit = get_object_or_404(
            Unit.objects.select_related("course").only(
                "id", "slug", "course_id",
                "course__id", "course__slug", "course__mentor_id"
            ),
            slug=self.kwargs["unit_slug"],
            course__slug=self.kwargs["course_slug"],
        )
        self.course = self.unit.course

        return self.unit
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not is_course_owner(request.user, self.course):
            self.handle_no_permissions(request)
        return super().dispatch(request, *args, **kwargs)
