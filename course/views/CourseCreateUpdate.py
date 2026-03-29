import shutil
import uuid

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.context_processors import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView
from django.contrib import messages
from docutils.nodes import field

from chunked_upload.models import ChunkedUpload
from course.forms import CourseForm
from accounts.views import RoleRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from course.models import Course
from course.views import is_course_owner
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
import os
from django.core.files.base import File

from course.views.mixins import CourseChangeAccessMixin


class CreateTagCatView(View):
    model = None  # passed from urls

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")

        if not name:
            return JsonResponse({"error": "Name is required"}, status=400)

        obj, created = self.model.objects.get_or_create(
            name=name,
            defaults={"slug": slugify(name)}
        )

        return JsonResponse({
            "id": obj.id,
            "name": obj.name,
            "created": created
        })


class CourseCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "course/course_form.html"
    success_url = reverse_lazy("course:Index Page")
    allowed_roles = ['mentor']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.mentor = self.request.user

        upload_id = self.request.POST.get("upload_id")
        file_name = self.request.POST.get("uploaded_file_name")

        response = super().form_valid(form)

        instance = self.object

        if not upload_id:
            return response

        try:
            temp_obj = ChunkedUpload.objects.get(upload_id=upload_id)
        except ChunkedUpload.DoesNotExist:
            return response

        temp_file = temp_obj.file

        if not temp_file:
            temp_obj.delete()
            return response

        temp_file.close()

        old_path = temp_file.name
        original_name = file_name or os.path.basename(old_path)
        name, ext = os.path.splitext(original_name)

        field = instance._meta.get_field('demo_video')

        new_name = original_name
        new_rel_path = field.generate_filename(instance, new_name)
        new_abs = os.path.join(settings.MEDIA_ROOT, new_rel_path)

        old_abs = os.path.join(settings.MEDIA_ROOT, old_path)

        while os.path.exists(new_abs):
            new_name = f"{name}-{uuid.uuid4().hex[:6]}{ext}"
            new_rel_path = field.generate_filename(instance, new_name)
            new_abs = os.path.join(settings.MEDIA_ROOT, new_rel_path)

        os.makedirs(os.path.dirname(new_abs), exist_ok=True)

        try:
            os.rename(old_abs, new_abs)
        except Exception:
            shutil.move(old_abs, new_abs)

        instance.demo_video.name = new_rel_path
        instance.save(update_fields=["demo_video"])

        temp_obj.delete()

        return response

class CourseUpdateView(LoginRequiredMixin, RoleRequiredMixin, CourseChangeAccessMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "course/course_form.html"
    allowed_roles = ["mentor"]


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


    def form_valid(self, form):
        chunk_id = self.request.POST.get("upload_id")
        file_name = self.request.POST.get("uploaded_file_name")
        response = super().form_valid(form)
        instance = self.object
        if not chunk_id:
            return response

        try:
            temp_obj = ChunkedUpload.objects.get(upload_id=chunk_id)
        except ChunkedUpload.DoesNotExist:
            messages.error(self.request, "Invalid temporary video.")
            return self.form_invalid(form)

        temp_file = temp_obj.file

        if not temp_file:
            messages.error(self.request, "No file found.")
            return self.form_invalid(form)

        temp_file.close()

        old_path = temp_file.name
        original_name = file_name or os.path.basename(old_path)
        nm, ext = os.path.splitext(original_name)

        old_abs = os.path.join(settings.MEDIA_ROOT, old_path)

        field = self.object._meta.get_field('demo_video')
        new_relative = field.generate_filename(instance,f'{nm}{ext}')
        new_abs = os.path.join(settings.MEDIA_ROOT,new_relative)
        while os.path.exists(new_abs):
            new_relative = field.generate_filename(instance,f'{nm}-{uuid.uuid4().hex[:6]}{ext}')

            new_abs = os.path.join(settings.MEDIA_ROOT,new_relative)

        os.makedirs(os.path.dirname(new_abs), exist_ok=True)


        # ✅ MOVE file (fast + fallback safe)
        try:
            os.rename(old_abs, new_abs)
        except Exception:
            shutil.move(old_abs, new_abs)


        # ✅ delete old video if updating
        if self.object and self.object.demo_video:
            self.object.demo_video.delete(save=False)

        # ✅ assign moved file
        instance.demo_video.name = new_relative
        instance.save(update_fields=["demo_video"])


        # ✅ delete only DB entry (file already moved)
        temp_obj.delete()

        return response

    def get_success_url(self):
        # Redirect back to the course detail page using the slug
        return self.object.get_absolute_url()

class VideoUploadView(ChunkedUploadView):
    field_name = "file"

    def check_permissions(self, request):
        user = request.user
        if not user.is_authenticated or user.role != 'mentor':
            raise PermissionDenied("Not allowed")


class VideoCompleteView(ChunkedUploadCompleteView):
    do_md5_check = False
    response_data = {}

    def check_permissions(self, request):
        user = request.user
        if not user.is_authenticated or user.role != 'mentor':
            raise PermissionDenied("Not allowed")

    def on_completion(self, uploaded_file, request):
        uploaded_file.close()
        self.response_data.update({
            "file_name": uploaded_file.name,
            "file_size": uploaded_file.size,
        })
        print(self.response_data)
        pass

    def get_response_data(self, chunked_upload, request):
        data = self.response_data if self.response_data else {
            "file_name": chunked_upload.file.name,
            "file_size": chunked_upload.file.size,
        }
        data.update( {
            "upload_id": chunked_upload.upload_id,
            "file_url": chunked_upload.file.url,
        })
        return data
