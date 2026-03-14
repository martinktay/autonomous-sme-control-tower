import boto3
import time
import threading
from typing import Optional
from botocore.exceptions import ClientError
from app.config import get_settings

settings = get_settings()


class S3Service:
    """S3 service for document storage with error handling and retry logic"""
    
    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None
        )
        self.bucket = settings.documents_bucket
    
    def _retry_with_backoff(self, func, *args, max_retries: int = 3, **kwargs):
        """Retry logic with exponential backoff for S3 operations"""
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                
                # Don't retry on validation errors
                if error_code in ["NoSuchBucket", "InvalidBucketName", "AccessDenied"]:
                    raise e
                
                # Retry on throttling and service errors
                if error_code in ["SlowDown", "ServiceUnavailable", "RequestTimeout"]:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + (time.time() % 1)  # Exponential backoff with jitter
                        time.sleep(wait_time)
                    else:
                        raise e
                else:
                    raise e
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + (time.time() % 1)
                    time.sleep(wait_time)
                else:
                    raise e
    
    def upload_file(self, file_content: bytes, s3_key: str) -> str:
        """Upload file to S3 with retry logic"""
        def _upload():
            self.client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=file_content
            )
            return s3_key
        
        return self._retry_with_backoff(_upload)
    
    def download_file(self, s3_key: str) -> bytes:
        """Download file from S3 with retry logic"""
        def _download():
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=s3_key
            )
            return response["Body"].read()
        
        return self._retry_with_backoff(_download)
    
    def delete_file(self, s3_key: str) -> None:
        """Delete file from S3 with retry logic"""
        def _delete():
            self.client.delete_object(
                Bucket=self.bucket,
                Key=s3_key
            )
        
        self._retry_with_backoff(_delete)
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for file access with retry logic"""
        def _generate():
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": s3_key},
                ExpiresIn=expiration
            )
            return url
        
        return self._retry_with_backoff(_generate)


_s3_service: Optional[S3Service] = None
_s3_lock = threading.Lock()


def get_s3_service() -> S3Service:
    """Get singleton S3 service (thread-safe)"""
    global _s3_service
    if _s3_service is None:
        with _s3_lock:
            if _s3_service is None:
                _s3_service = S3Service()
    return _s3_service
