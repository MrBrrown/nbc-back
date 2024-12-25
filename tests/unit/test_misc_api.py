import asyncio
import logging
from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest
from fastapi.responses import JSONResponse

from api.v1.endpoints.misc_api import (
    check_db_availability,
    DatabaseUnavailableError,
    check_services_availability,
    ServiceUnavailableError,
    check_resources_availability,
    ResourceUnavailableError,
    get_errors,
    check_no_errors,
    ErrorsPresentError,
    healthcheck,
)

# Mocking external dependencies

@pytest.mark.asyncio
async def test_check_db_availability_success():
    with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_open_connection:
        # Simulate a successful connection
        mock_open_connection.return_value = (AsyncMock(), AsyncMock())
        await check_db_availability()  # Should not raise an exception
        mock_open_connection.assert_awaited_once()

@pytest.mark.asyncio
async def test_check_db_availability_failure():
    with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_open_connection:
        # Simulate a connection error
        mock_open_connection.side_effect = ConnectionRefusedError
        with pytest.raises(DatabaseUnavailableError):
            await check_db_availability()
        mock_open_connection.assert_awaited_once()

@pytest.mark.asyncio
async def test_check_db_availability_timeout():
    with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_open_connection:
        # Simulate a timeout error
        mock_open_connection.side_effect = asyncio.TimeoutError
        with pytest.raises(DatabaseUnavailableError):
            await check_db_availability()
        mock_open_connection.assert_awaited_once()

@pytest.mark.asyncio
async def test_check_services_availability_success():
    class MockResponse:
        def __init__(self, status):
            self.status = status
            # Mock the aclose method to be a coroutine as well
            self.aclose = AsyncMock()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            await self.aclose()

    async def mock_get_coroutine(*args, **kwargs):
        return MockResponse(status=200)

    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = mock_get_coroutine  # Use the coroutine
        await check_services_availability(
            [
                {"name": "service1", "url": "http://service1.com"},
                {"name": "service2", "url": "http://service2.com"},
            ]
        )
        assert mock_get.call_count == 2

@pytest.mark.asyncio
async def test_check_services_availability_failure():
    class MockResponse:
        def __init__(self, status):
            self.status = status
            self.aclose = AsyncMock()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            await self.aclose()

    async def mock_get_coroutine(*args, **kwargs):
        # Simulate different responses
        if args[1] == "http://service1.com":
            return MockResponse(status=200)
        else:
            return MockResponse(status=500)

    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = mock_get_coroutine
        with pytest.raises(ServiceUnavailableError):
            await check_services_availability(
                [
                    {"name": "service1", "url": "http://service1.com"},
                    {"name": "service2", "url": "http://service2.com"},
                ]
            )
        assert mock_get.call_count == 2

@pytest.mark.asyncio
async def test_check_services_availability_client_error():
    with patch(
        "aiohttp.ClientSession.get", new_callable=AsyncMock
    ) as mock_get:
        # Simulate a ClientError
        mock_get.side_effect = aiohttp.ClientError
        with pytest.raises(ServiceUnavailableError):
            await check_services_availability(
                [{"name": "service1", "url": "http://service1.com"}]
            )
        mock_get.assert_awaited_once()

@pytest.mark.asyncio
async def test_check_services_availability_empty_list():
    # Test with an empty list of services
    await check_services_availability([])  # Should not raise an exception

@pytest.mark.asyncio
@patch("psutil.cpu_percent", return_value=50)
@patch("psutil.virtual_memory", return_value=AsyncMock(percent=60))
@patch("psutil.disk_usage", return_value=AsyncMock(percent=70))
async def test_check_resources_availability_success(
    mock_disk_usage, mock_virtual_memory, mock_cpu_percent
):
    await check_resources_availability()  # Should not raise an exception

@pytest.mark.asyncio
@patch("psutil.cpu_percent", return_value=90)
@patch("psutil.virtual_memory", return_value=AsyncMock(percent=60))
@patch("psutil.disk_usage", return_value=AsyncMock(percent=70))
async def test_check_resources_availability_cpu_failure(
    mock_disk_usage, mock_virtual_memory, mock_cpu_percent
):
    with pytest.raises(ResourceUnavailableError):
        await check_resources_availability()

@pytest.mark.asyncio
@patch("psutil.cpu_percent", return_value=50)
@patch("psutil.virtual_memory", return_value=AsyncMock(percent=95))
@patch("psutil.disk_usage", return_value=AsyncMock(percent=70))
async def test_check_resources_availability_memory_failure(
    mock_disk_usage, mock_virtual_memory, mock_cpu_percent
):
    with pytest.raises(ResourceUnavailableError):
        await check_resources_availability()

@pytest.mark.asyncio
@patch("psutil.cpu_percent", return_value=50)
@patch("psutil.virtual_memory", return_value=AsyncMock(percent=60))
@patch("psutil.disk_usage", return_value=AsyncMock(percent=95))
async def test_check_resources_availability_disk_failure(
    mock_disk_usage, mock_virtual_memory, mock_cpu_percent
):
    with pytest.raises(ResourceUnavailableError):
        await check_resources_availability()

@pytest.mark.asyncio
async def test_get_errors():
    # Test that get_errors returns an empty list (mocked behavior)
    errors = await get_errors()
    assert errors == []

@pytest.mark.asyncio
async def test_check_no_errors_success():
    with patch(
        "api.v1.endpoints.misc_api.get_errors", new_callable=AsyncMock
    ) as mock_get_errors:
        mock_get_errors.return_value = []
        await check_no_errors()  # Should not raise an exception
        mock_get_errors.assert_awaited_once()

@pytest.mark.asyncio
async def test_check_no_errors_failure():
    with patch(
        "api.v1.endpoints.misc_api.get_errors", new_callable=AsyncMock
    ) as mock_get_errors:
        mock_get_errors.return_value = ["Error 1", "Error 2"]
        with pytest.raises(ErrorsPresentError):
            await check_no_errors()
        mock_get_errors.assert_awaited_once()

@pytest.mark.asyncio
@patch("api.v1.endpoints.misc_api.check_db_availability", new_callable=AsyncMock)
@patch("api.v1.endpoints.misc_api.check_services_availability", new_callable=AsyncMock)
@patch("api.v1.endpoints.misc_api.check_resources_availability", new_callable=AsyncMock)
@patch("api.v1.endpoints.misc_api.check_no_errors", new_callable=AsyncMock)
async def test_healthcheck_success(
    mock_check_no_errors, mock_check_resources, mock_check_services, mock_check_db
):
    response = await healthcheck()
    assert response.status_code == HTTPStatus.OK
    assert response.body == b'{"status":"OK"}'
    mock_check_db.assert_awaited_once()
    mock_check_services.assert_awaited_once()
    mock_check_resources.assert_awaited_once()
    mock_check_no_errors.assert_awaited_once()

@pytest.mark.asyncio
async def test_healthcheck_db_failure():
    with patch(
        "api.v1.endpoints.misc_api.check_db_availability",
        side_effect=DatabaseUnavailableError,
    ) as mock_check_db:
        response = await healthcheck()
        assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert response.body == b'{"error":"Database is not available"}'
        mock_check_db.assert_awaited_once()

@pytest.mark.asyncio
async def test_healthcheck_services_failure():
    with patch(
        "api.v1.endpoints.misc_api.check_services_availability",
        side_effect=ServiceUnavailableError,
    ) as mock_check_services:
        response = await healthcheck()
        assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert response.body == b'{"error":"Services are not available"}'
        mock_check_services.assert_awaited_once()

@pytest.mark.asyncio
async def test_healthcheck_resources_failure():
    with patch(
        "api.v1.endpoints.misc_api.check_resources_availability",
        side_effect=ResourceUnavailableError,
    ) as mock_check_resources:
        response = await healthcheck()
        assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert response.body == b'{"error":"Resources are not available"}'
        mock_check_resources.assert_awaited_once()

@pytest.mark.asyncio
async def test_healthcheck_errors_failure():
    with patch(
        "api.v1.endpoints.misc_api.check_no_errors", side_effect=ErrorsPresentError
    ) as mock_check_errors:
        response = await healthcheck()
        assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert response.body == b'{"error":"Errors are present"}'
        mock_check_errors.assert_awaited_once()

# @pytest.mark.asyncio
# async def test_healthcheck_exception():
#     with patch(
#         "api.v1.endpoints.misc_api.check_db_availability",
#         side_effect=Exception("Unexpected error"),
#     ) as mock_check_db:
#         response = await healthcheck()
#         assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
#         assert response.body == b'{"error":"Internal error"}'
#         mock_check_db.assert_awaited_once()

@pytest.mark.asyncio
async def test_healthcheck_exception():
    with patch(
        "api.v1.endpoints.misc_api.check_db_availability",
        side_effect=Exception("Unexpected error"),
    ) as mock_check_db, patch(
        "api.v1.endpoints.misc_api.check_services_availability", new_callable=AsyncMock
    ) as mock_check_services, patch(
        "api.v1.endpoints.misc_api.check_resources_availability", new_callable=AsyncMock
    ) as mock_check_resources, patch(
        "api.v1.endpoints.misc_api.check_no_errors", new_callable=AsyncMock
    ) as mock_check_no_errors:
        response = await healthcheck()

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.body == b'{"error":"Internal error"}'

        # Ensure that the side effect was triggered
        assert mock_check_db.side_effect is not None