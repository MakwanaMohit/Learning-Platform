from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View

from accounts.views.mixins import RoleRequiredMixin


class IndexView(View):
    # allowed_roles = ['student','mentor']
    def get(self, request):
        return HttpResponse('Hello World! <br> <a href="'+ reverse_lazy('accounts:login')+'">Login</a>')