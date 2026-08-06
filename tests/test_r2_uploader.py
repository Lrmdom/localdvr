import pytest
from unittest.mock import MagicMock, patch
from src.r2_uploader import R2Uploader

@patch("boto3.client")
def test_r2_uploader_init(mock_boto3_client):
    uploader = R2Uploader(
        account_id="test-account",
        access_key="test-key",
        secret_key="test-secret",
        bucket_name="test-bucket"
    )
    mock_boto3_client.assert_called_once()
