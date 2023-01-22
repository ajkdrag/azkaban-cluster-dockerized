import os
import boto3
import requests


def get_bucket_obj(name, **kwargs):
    s3 = boto3.resource("s3", 
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            **kwargs
        ) 

    return s3.Bucket(name)


def upload_to_s3(url, bucket_obj, key):
    data = requests.get(url, stream=True)
    bucket_obj.upload_fileobj(data.raw, key)


if __name__=="__main__":
    env = os.environ["ENVIRONMENT"]
    target_key = os.environ["DATASET_RAW"]

    bucket_obj = get_bucket_obj(
                    name=env,
                    aws_session_token=None,
                    config=boto3.session.Config(signature_version='s3v4'),
                    endpoint_url="http://192.168.48.3:9000",
                    verify=False
                )

    upload_to_s3(os.environ["DATASET_URL"], bucket_obj, target_key)
    print(f"Uploaded dataset to: {target_key}")

