from django.core.files.storage import FileSystemStorage
from django.conf import settings


class PrivateMediaStorage(FileSystemStorage):
    location = settings.PRIVATE_MEDIA_ROOT
    base_url = settings.PRIVATE_MEDIA_URL