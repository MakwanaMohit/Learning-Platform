from django.http import HttpResponse
from django.views import View

class CourseIndexView(View):
    def get(self,request):
        return HttpResponse('Course Index Page')

