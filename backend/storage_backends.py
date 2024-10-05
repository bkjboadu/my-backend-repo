from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings


class StaticStorage(GoogleCloudStorage):
    location = "static"
    default_acl = 'publicRead'


class MediaStorage(GoogleCloudStorage):
    location = "media"
    default_acl = 'publicRead'
