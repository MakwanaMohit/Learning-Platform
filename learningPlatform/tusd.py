import os
import json
import uuid

from django.http import JsonResponse
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from course.models import Course, VideoContent, ChapterContent
from course.models.chapter_content import Assignment, AssignmentFile
from course.views import is_course_owner
from learningPlatform.settings import MEDIA_ROOT

User = get_user_model()

file_fields = {
    "create-course": Course._meta.get_field("demo_video"),
    "update-course": Course._meta.get_field("demo_video"),
    "content-video": VideoContent._meta.get_field("video_file"),
    "content-assignment": AssignmentFile._meta.get_field("file"),
}


def get_upload_field(upload_type):
    return file_fields.get(upload_type)


# =========================
# RESPONSE HELPERS
# =========================

def reject_response(message="Unauthorized"):
    return JsonResponse({
        "HTTPResponse": {
            "StatusCode": 403,
            "Body": json.dumps({"error": message}),
            "Header": {
                "Content-Type": "application/json"
            }
        }
    })


def success_change_response(upload_id, relative_path):
    return JsonResponse({
        "ChangeFileInfo": {
            "ID": upload_id,
            "Storage": {
                "Path": relative_path
            }
        }
    })


# =========================
# AUTH HELPERS
# =========================

def extract_session_id(cookie_header: str):
    if not cookie_header:
        return None

    for cookie in cookie_header.split(";"):
        cookie = cookie.strip()
        if cookie.startswith("sessionid="):
            return cookie.split("=", 1)[1]
    return None


def get_user_from_session(session_id):
    try:
        session = Session.objects.get(session_key=session_id)
        session_data = session.get_decoded()
        user_id = session_data.get("_auth_user_id")
        return User.objects.get(id=user_id)
    except Exception:
        return None


# =========================
# INSTANCE RESOLVERS
# =========================

def get_instance_for_upload(upload_type, metadata, user):
    if upload_type == "create-course":
        return Course()

    if upload_type == "update-course":
        return Course.objects.select_related("mentor").only("id", "mentor__id").get(
            id=metadata.get("content_id"))

    if upload_type == "content-video" or upload_type == "content-assignment":
        return get_object_or_404(
            ChapterContent.objects.select_related("chapter__unit__course").only(
                "id", "content_type", "chapter_id",
                "chapter__id", "chapter__unit_id",
                "chapter__unit__id", "chapter__unit__course_id",
                "chapter__unit__course__id",
                "chapter__unit__course__mentor_id",
            ),
            id=metadata.get("content_id")
        )

    return None


def get_course_from_upload(upload_type, instance):
    if upload_type in ["create-course", "update-course"]:
        return instance

    return instance.chapter.unit.course


def is_authorized(user, upload_type, instance):
    if not user or not user.is_authenticated:
        return False

    if upload_type == "create-course":
        return getattr(user, "role", None) == "mentor"

    course = get_course_from_upload(upload_type, instance)
    if not course:
        return False

    return is_course_owner(user, course)


# =========================
# FILE GENERATION
# =========================

def generate_unique_path(field, instance, original_name):
    name, ext = os.path.splitext(original_name)

    while True:
        new_name = f"{name}-{uuid.uuid4().hex[:8]}{ext}"
        relative_path = field.generate_filename(instance, new_name)
        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        if not os.path.exists(absolute_path):
            return new_name, relative_path.replace("\\", "/")


def get_storage_folder(field):
    storage = field.storage

    base_location = os.path.abspath(storage.location)
    media_root = os.path.abspath(settings.BASE_DIR / 'media')

    if base_location.startswith(media_root):
        relative = os.path.relpath(base_location, media_root)
        return relative.replace("\\", "/")  # e.g. "private_media"

    return ""


def normalize_uploaded_path(field, upload_id):
    storage_folder = get_storage_folder(field)

    if storage_folder and upload_id.startswith(storage_folder + "/"):
        return upload_id[len(storage_folder) + 1:]

    return upload_id


# =========================
# PRE-CREATE HANDLER
# =========================

def handle_pre_create(data):
    event = data.get("Event", {})
    upload = event.get("Upload", {})
    http_request = event.get("HTTPRequest", {})

    metadata = upload.get("MetaData", {})
    headers = http_request.get("Header", {})

    # --- user extraction ---
    cookie_header = headers.get("Cookie", [""])[0]
    session_id = extract_session_id(cookie_header)
    user = get_user_from_session(session_id)

    if not user:
        return reject_response("Invalid session")

    # --- metadata ---
    upload_type = metadata.get("upload_type")
    filename = metadata.get("filename")

    if not upload_type or not filename:
        return reject_response("Missing metadata")

    field = get_upload_field(upload_type)

    if not field:
        return reject_response("Invalid upload type")

    # --- instance ---
    try:
        instance = get_instance_for_upload(upload_type, metadata, user)
    except Exception as e:
        print(e)
        return reject_response("Invalid resource reference")

    if not instance:
        return reject_response("Instance not found")

    # --- auth ---
    if not is_authorized(user, upload_type, instance):
        return reject_response("Permission denied")

    # --- generate path ---
    try:
        _, relative_path = generate_unique_path(field, instance, filename)

        storage_folder = get_storage_folder(field)

        # Final ID sent to tusd
        if storage_folder:
            upload_id = f"{storage_folder}/{relative_path}"
        else:
            upload_id = relative_path

        # print(upload_id)

    except Exception as e:
        print(e)
        return reject_response("Path generation failed")

    return success_change_response(upload_id, upload_id)


# =========================
# POST-FINISH HANDLER
# =========================

def handle_post_finish(data):
    event = data.get("Event", {})
    upload = event.get("Upload", {})
    metadata = upload.get("MetaData", {})

    upload_type = metadata.get("upload_type")
    upload_id = upload.get("ID")  # this is our relative path
    filename = metadata.get("filename")

    if not upload_type or not upload_id:
        return JsonResponse({})

    # Ignore course create/update
    if upload_type == "create-course":
        return JsonResponse({})

    try:
        instance = get_instance_for_upload(upload_type, metadata, None)
    except Exception:
        return JsonResponse({})

    if not instance:
        return JsonResponse({})

    # -------------------------
    # UPDATE COURSE
    # -------------------------
    if upload_type == "update-course":
        field = get_upload_field(upload_type)
        clean_path = normalize_uploaded_path(field, upload_id)

        instance.demo_video.name = clean_path
        instance.save(update_fields=["demo_video"])
        return JsonResponse({})

    # -------------------------
    # VIDEO
    # -------------------------
    if upload_type == "content-video":
        field = get_upload_field(upload_type)
        clean_path = normalize_uploaded_path(field, upload_id)

        video = instance.videocontent
        video.video_file = clean_path
        video.save(update_fields=["video_file"])
        return JsonResponse({})

    # -------------------------
    # ASSIGNMENT
    # -------------------------
    if upload_type == "content-assignment":
        field = get_upload_field(upload_type)
        clean_path = normalize_uploaded_path(field, upload_id)

        AssignmentFile.objects.create(
            assignment=instance.assignment,
            file=clean_path,
            file_name=filename or os.path.basename(clean_path)
        )
        return JsonResponse({})

    return JsonResponse({})


# =========================
# MAIN VIEW
# =========================

@csrf_exempt
def tus_hook_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return reject_response("Invalid JSON")

    hook_type = data.get("Type")

    if hook_type == "pre-create":
        return handle_pre_create(data)

    if hook_type == "post-finish":
        return handle_post_finish(data)

    return JsonResponse({})
