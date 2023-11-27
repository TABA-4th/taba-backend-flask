# _1_supload.py
import io
import boto3
from shared_data import Instance
from config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY

def upload():
    s3 = boto3.client(
        service_name='s3',
        region_name=AWS_S3_BUCKET_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    new_filename = Instance.url_time + '.jpeg'
    s3.upload_fileobj(io.BytesIO(Instance.file_data), AWS_S3_BUCKET_NAME, new_filename)
    Instance.image_url = f'https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{new_filename}'
