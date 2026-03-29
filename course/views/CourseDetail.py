# views.py
from django.views import View
from django.http import HttpResponse

class CourseDetailView(View):
    def get(self, request, course_slug):
        return HttpResponse(f"Slug: {course_slug}")