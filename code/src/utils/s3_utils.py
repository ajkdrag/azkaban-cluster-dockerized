import os
import boto3
import pathlib
from urllib.parse import urlparse


def get_s3_client():
    kwargs = {}
    if os.environ.get("USE_MINIO", "false").lower() == "true":
        kwargs = {
              "aws_session_token": None,
              "config": boto3.session.Config(signature_version='s3v4'),
              "endpoint_url": os.environ["MINIO_ENDPOINT"],
              "verify": False 
        }
        
    return boto3.client("s3", **kwargs)


def get_bucket_and_key(s3_path):
    s3_uri = urlparse(s3_path)
    return s3_uri.netloc, s3_uri.path


def download_file(s3_path, folder=None):
    if folder is None:
        folder = os.getcwd()
    folder = pathlib.Path(folder)

    bucket, key = get_bucket_and_key(s3_path) 
    filename = pathlib.Path(key).name
    local_path = folder / filename

    s3c = get_s3_client()
    s3c.download_file(Bucket=bucket, Key=key, Filename=local_path)

    return local_path


def upload_file(local_path, s3_path):
    bucket, key = get_bucket_and_key(s3_path) 
    s3c = get_s3_client()
    s3c.upload_file(local_path, bucket, key)


def stream_file(s3_path):
    bucket, key = get_bucket_and_key(s3_path)
    s3c = get_s3_client()
    obj = s3c.get_object(Bucket=bucket, Key=key)
    return obj["Body"]
