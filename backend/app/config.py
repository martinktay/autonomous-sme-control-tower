from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration"""
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    
    # Bedrock Models
    nova_lite_model_id: str = "amazon.nova-lite-v1:0"
    nova_embeddings_model_id: str = "amazon.nova-embed-v1:0"
    nova_act_model_id: str = "amazon.nova-act-v1:0"
    nova_sonic_model_id: str = "amazon.nova-sonic-v1:0"
    
    # DynamoDB Tables
    signals_table: str = "autonomous-sme-signals"
    nsi_scores_table: str = "autonomous-sme-nsi-scores"
    strategies_table: str = "autonomous-sme-strategies"
    actions_table: str = "autonomous-sme-actions"
    
    # S3 Buckets
    documents_bucket: str = "autonomous-sme-documents"
    
    # Application
    app_name: str = "Autonomous SME Control Tower"
    debug: bool = False
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
