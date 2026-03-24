"""
Application configuration loaded from environment variables and .env file.

Uses pydantic-settings to provide typed, validated configuration with sensible
defaults for local development.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Centralised application settings populated from environment / .env file."""

    # --- AWS credentials & region ---
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""       # Leave blank to use instance profile / env creds
    aws_secret_access_key: str = ""

    # --- Bedrock model identifiers ---
    nova_lite_model_id: str = "amazon.nova-lite-v1:0"          # Text generation
    nova_embeddings_model_id: str = "amazon.nova-embed-v1:0"   # Semantic embeddings
    nova_act_model_id: str = "amazon.nova-act-v1:0"            # Agentic actions
    nova_sonic_model_id: str = "amazon.nova-sonic-v1:0"        # Voice / audio

    # --- DynamoDB table names (existing) ---
    signals_table: str = "autonomous-sme-signals"
    bsi_scores_table: str = "autonomous-sme-bsi-scores"
    strategies_table: str = "autonomous-sme-strategies"
    actions_table: str = "autonomous-sme-actions"
    evaluations_table: str = "autonomous-sme-evaluations"
    embeddings_table: str = "autonomous-sme-embeddings"
    tasks_table: str = "autonomous-sme-tasks"

    # --- DynamoDB table names (Africa commercial readiness) ---
    businesses_table: str = "autonomous-sme-businesses"
    branches_table: str = "autonomous-sme-branches"
    transactions_table: str = "autonomous-sme-transactions"
    inventory_table: str = "autonomous-sme-inventory"
    counterparties_table: str = "autonomous-sme-counterparties"
    alerts_table: str = "autonomous-sme-alerts"
    insights_table: str = "autonomous-sme-insights"
    upload_jobs_table: str = "autonomous-sme-upload-jobs"

    # --- S3 bucket for uploaded documents ---
    documents_bucket: str = "autonomous-sme-documents"

    # --- Outbound invoices ---
    outbound_invoices_table: str = "autonomous-sme-outbound-invoices"

    # --- Subscriptions ---
    subscriptions_table: str = "autonomous-sme-subscriptions"
    paystack_secret_key: str = ""          # Paystack webhook HMAC secret
    flutterwave_secret_hash: str = ""      # Flutterwave webhook verification hash
    stripe_secret_key: str = ""            # Stripe API secret key

    # --- SES email sending ---
    ses_sender_email: str = ""         # Verified sender address (required for sending)
    ses_region: str = "us-east-1"

    # --- DynamoDB table for users ---
    users_table: str = "autonomous-sme-users"

    # --- JWT authentication ---
    jwt_secret: str = "change-me-in-production-use-a-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 8

    # --- Application-level settings ---
    app_name: str = "Autonomous SME Control Tower"
    debug: bool = False
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"  # Comma-separated
    rate_limit_rpm: int = 120          # Max requests per minute per client IP

    model_config = ConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once per process)."""
    return Settings()
