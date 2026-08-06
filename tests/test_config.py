import os
import pytest
from src.config import Settings

def test_r2_endpoint_url():
    # Setup env variables
    os.environ["CLOUDFLARE_ACCOUNT_ID"] = "test-account-id"
    os.environ["AWS_ACCESS_KEY_ID"] = "test-key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test-secret"
    os.environ["R2_BUCKET_NAME"] = "test-bucket"

    # Initialize settings
    settings = Settings()
    assert settings.r2_endpoint_url == "https://test-account-id.r2.cloudflarestorage.com"
