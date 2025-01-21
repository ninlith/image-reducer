"""Image conversion tests."""

import asyncio
import io
import time
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from PIL import Image
from kollikissa.main import app, INVALID_MIME_ERROR, INVALID_IMAGE_ERROR

client = TestClient(app)


def create_test_image(image_format: str = "JPEG") -> io.BytesIO:
    """Helper function to create a test image in memory."""
    image = Image.new("RGB", (800, 600), color="red")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)
    return image_bytes


async def make_concurrent_requests(num_requests: int, image_bytes):
    """Helper function to make concurrent requests to the server."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    async_client.post(
                        "/process/",
                        files={"file": ("test_image.jpg", image_bytes, "image/jpeg")},
                    )
                )
                for _ in range(num_requests)
            ]
        return [task.result() for task in tasks]


@pytest.mark.asyncio
async def test_conversion():
    """Test the performance and correctness of the image conversion."""

    async def time_concurrent_requests(num_requests: int, image_bytes):
        start_time = time.perf_counter()
        responses = await make_concurrent_requests(num_requests, image_bytes)
        elapsed_time = time.perf_counter() - start_time
        print(f"{num_requests = }, {elapsed_time = }")
        return responses, elapsed_time

    image_bytes = create_test_image()
    print()
    responses_1, elapsed_time_1 = await time_concurrent_requests(1, image_bytes)
    responses_5, elapsed_time_5 = await time_concurrent_requests(5, image_bytes)
    assert elapsed_time_1*3 > elapsed_time_5

    for response in responses_1 + responses_5:
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/avif"
        output_image = Image.open(io.BytesIO(response.content))
        assert output_image.format == "AVIF"


def test_invalid_mime():
    """Simulate uploading an image with an invalid MIME type."""
    response = client.post(
        "/process/",
        files={"file": ("test_file.txt", create_test_image(), "text/plain")},
    )

    # Check the response status code and error message
    assert response.status_code == 422
    assert response.json()["detail"] == INVALID_MIME_ERROR


def test_invalid_image():
    """Simulate uploading an invalid image file."""
    response = client.post(
        "/process/",
        files={"file": ("test_image.invalid", b"invalid image data", "image/jpeg")},
    )

    # Check the response status code and error message
    assert response.status_code == 422
    assert response.json()["detail"] == INVALID_IMAGE_ERROR
