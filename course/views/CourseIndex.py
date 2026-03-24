import threading

from django.views.generic import ListView
from django.db.models import Q

from course.course_seeder import main
from course.models import Course, Category, Tag
from accounts.models import User
class CourseListView(ListView):
    model = Course
    template_name = "course/course_list.html"
    context_object_name = "courses"
    paginate_by = 9
    catSet = set()
    tagSet = set()
    catqueryset = None
    tagqueryset = None
    def get_queryset(self):
        q = self.request.GET.get("sq")
        l = self.request.GET.get("sl")
        if q and l:
            l = int(l)
            threading.Thread(target=main, args=(q,l)).start()


        user = self.request.user
        queryset = (
            Course.objects.filter(Q(status="published") | Q(mentor = user) | Q(mentors = user))
            .select_related("category", "mentor")
            .prefetch_related("keywords", "mentors").distinct()
        ) if (user.is_authenticated and user.role == 'mentor') else (
            Course.objects.filter(status="published")
            .select_related("category", "mentor")
            .prefetch_related("keywords", "mentors").distinct()
        )

        # GET params
        search = self.request.GET.get("q")
        category = self.request.GET.getlist("category")
        tags = self.request.GET.getlist("tags")

        self.catSet = set(category)
        self.tagSet = set(tags)
        # Search (basic for now)

        queryset = queryset.filter(
            (
                    Q(title__icontains=search) |
                    Q(short_description__icontains=search)
            ) if search else Q(),
            (
                    Q(category__slug__in=category) |
                    Q(keywords__slug__in=tags)
            ) if (category or tags) else Q()
        ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["tags"] = Tag.objects.all()
        context['catset'] = self.catSet
        context['tagset'] = self.tagSet
        context['catqueryset'] = context['categories'].filter(slug__in=self.catSet)
        context['tagqueryset'] = context['tags'].filter(slug__in=self.tagSet)
        return context