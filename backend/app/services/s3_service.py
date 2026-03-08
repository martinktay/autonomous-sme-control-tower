import boto3
from typing import Optional
from app.config import get_settings

settings = get_settings()


class S3Service:
    """S3 service for document storage"""
    
    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None
        )
        self.bucket = settings.documents_bucket
    
    def upload_file(self, file_content: bytes, key: str) -> str:
        """Upload file to S3 and return key"""
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_content
        )
        return key
    
    def get_file(self, key: str) -> bytes:
        """Retrieve file from S3"""
        response = self.client.get_object(
            Bucket=self.bucket,
            Key=key
        )
        return response["Body"].read()
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for file access"""
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expiration
        )


_s3_service: Optional[S3Service] = None


def get_s3_service() -> S3Service:
    """Get singleton S3 service"""
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service
