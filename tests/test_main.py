import os
# Set env vars BEFORE importing main
os.environ["CLOUDFLARE_ACCOUNT_ID"] = "test"
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["R2_BUCKET_NAME"] = "test"

import pytest
from unittest.mock import MagicMock, patch
from main import main

@patch("main.asyncio")
@patch("main.RTSPRecorder")
@patch("main.R2Uploader")
@patch("main.settings")
def test_main_init_no_cameras(mock_settings, mock_uploader, mock_recorder, mock_asyncio):
    # Configure mock
    mock_settings.cameras = []
    
    # Test that it exits if no cameras are configured
    with pytest.raises(SystemExit):
        main()
