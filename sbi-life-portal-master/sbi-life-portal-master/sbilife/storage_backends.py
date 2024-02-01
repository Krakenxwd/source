import os

from botocore.client import Config
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    bucket_name = os.getenv('S3_STATIC_BUCKET')
    region_name = os.getenv('S3_STATIC_BUCKET_REGION')
    default_acl = 'public-read'
    querystring_auth = False
    location = 'static'
    file_overwrite = True


class MediaStorage(S3Boto3Storage):
    bucket_name = os.getenv('S3_MEDIA_BUCKET')
    region_name = os.getenv('S3_MEDIA_BUCKET_REGION')
    default_acl = 'private'
    file_overwrite = False
    max_pool_connections = 100
