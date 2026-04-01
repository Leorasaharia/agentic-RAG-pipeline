import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from backend.config import settings
from backend.utils.logger import get_logger
import uuid

logger = get_logger(__name__)


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


async def upload_file_to_s3(file: UploadFile, user_id: str) -> tuple[str, str]:
    """Upload file to S3 and return (s3_key, s3_url)."""
    ext = file.filename.split(".")[-1].lower()
    s3_key = f"documents/{user_id}/{uuid.uuid4()}.{ext}"

    s3 = get_s3_client()
    try:
        content = await file.read()
        s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Body=content,
            ContentType=file.content_type or "application/octet-stream",
        )
        s3_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        logger.info(f"Uploaded {s3_key} to S3")
        return s3_key, s3_url
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        raise


def download_file_from_s3(s3_key: str) -> bytes:
    """Download file bytes from S3."""
    s3 = get_s3_client()
    try:
        response = s3.get_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
        return response["Body"].read()
    except ClientError as e:
        logger.error(f"S3 download failed: {e}")
        raise


def delete_file_from_s3(s3_key: str) -> None:
    s3 = get_s3_client()
    try:
        s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
        logger.info(f"Deleted {s3_key} from S3")
    except ClientError as e:
        logger.error(f"S3 delete failed: {e}")
        raise
