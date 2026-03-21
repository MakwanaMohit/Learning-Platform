from django.views.generic import ListView
from django.db.models import Q
from course.models import Course, Category, Tag


class CourseListView(ListView):
    model = Course
    template_name = "course/course_list.html"
    context_object_name = "courses"
    paginate_by = 9

    def get_queryset(self):
        queryset = (
            Course.objects.filter(status="published")
            .select_related("category", "mentor")
            .prefetch_related("keywords", "mentors")
        )

        # GET params
        search = self.request.GET.get("q")
        category = self.request.GET.getlist("category")
        tags = self.request.GET.getlist("tags")

        # Search (basic for now)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(short_description__icontains=search)
            )

        if category:
            queryset = queryset.filter(category__slug__in=category)

        if tags:
            queryset = queryset.filter(keywords__slug__in=tags).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["tags"] = Tag.objects.all()
        return context