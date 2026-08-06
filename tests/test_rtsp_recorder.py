import pytest
import asyncio
from unittest.mock import MagicMock, patch
from src.rtsp_recorder import RTSPRecorder
from src.r2_uploader import R2Uploader
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.asyncio
async def test_rtsp_recorder_init():
    uploader = MagicMock(spec=R2Uploader)
    executor = MagicMock(spec=ThreadPoolExecutor)
    recorder = RTSPRecorder(
        camera_name="test-cam",
        rtsp_url="rtsp://test",
        segment_duration=10,
        temp_dir="./temp",
        uploader=uploader,
        executor=executor
    )
    assert recorder.camera_name == "test-cam"
