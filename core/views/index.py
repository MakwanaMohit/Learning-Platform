from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View

from accounts.views.mixins import RoleRequiredMixin


class IndexView(View):
    # allowed_roles = ['student','mentor']
    def get(self, request):
        return render(request,"core/home.html")