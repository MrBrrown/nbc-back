import asyncio
import logging
from http import HTTPStatus
from typing import Dict, List

import aiohttp
import psutil
from fastapi import APIRouter
from fastapi.responses import JSONResponse

misc_router = APIRouter()

class DatabaseUnavailableError(Exception):
    pass

class ServiceUnavailableError(Exception):
    pass

class ResourceUnavailableError(Exception):
    pass

class ErrorsPresentError(Exception):
    pass

async def check_db_availability(db_host: str = "localhost", db_port: int = 5432, timeout: int = 5) -> None:
    """
    Check if a database is available.

    Args:
    - db_host (str): Database host.
    - db_port (int): Database port.
    - timeout (int): Timeout in seconds. Defaults to 5.

    Raises:
    - DatabaseUnavailableError: If the database is not available.
    """
    try:
        # Create a socket with a timeout
        reader, writer = await asyncio.wait_for(asyncio.open_connection(db_host, db_port), timeout=timeout)
        writer.close()
        await writer.wait_closed()
    except (ConnectionRefusedError, asyncio.TimeoutError) as e:
        logging.error(f"Database at {db_host}:{db_port} is not available: {e}")
        raise DatabaseUnavailableError(f"Database at {db_host}:{db_port} is not available") from e

async def check_services_availability(services: List[Dict[str, str]] = None) -> None:
    """
    Check if services are available.

    Args:
    - services (List[Dict[str, str]]): List of services to check.

    Raises:
    - ServiceUnavailableError: If any of the services are not available.
    """
    if services is None:
        services = []
    async with aiohttp.ClientSession() as session:
        for service in services:
            try:
                async with session.get(service['url']) as response:
                    if response.status != 200:
                        logging.error(f"{service['name']} is not available (status code: {response.status})")
                        raise ServiceUnavailableError(f"{service['name']} is not available")
            except aiohttp.ClientError as e:
                logging.error(f"Failed to check {service['name']}: {e}")
                raise ServiceUnavailableError(f"Failed to check {service['name']}") from e

async def check_resources_availability() -> None:
    """
    Check if system resources are available.

    Raises:
    - ResourceUnavailableError: If any of the resources are not available.
    """
    # Get current system resource usage
    cpu_usage: float = psutil.cpu_percent()
    memory_usage: float = psutil.virtual_memory().percent
    disk_usage: float = psutil.disk_usage('/').percent

    # Define thresholds for resource availability
    cpu_threshold: int = 80
    memory_threshold: int = 90
    disk_threshold: int = 90

    # Check if resources are available
    if cpu_usage >= cpu_threshold:
        logging.error(f"CPU usage is too high: {cpu_usage}%")
        raise ResourceUnavailableError("CPU usage is too high")
    if memory_usage >= memory_threshold:
        logging.error(f"Memory usage is too high: {memory_usage}%")
        raise ResourceUnavailableError("Memory usage is too high")
    if disk_usage >= disk_threshold:
        logging.error(f"Disk usage is too high: {disk_usage}%")
        raise ResourceUnavailableError("Disk usage is too high")

async def get_errors() -> list[str]:
    # TODO
    # Replace this with your actual error retrieval logic
    # For example, let's assume we're retrieving errors from a database
    # errors = await database.query("SELECT error_message FROM errors")
    # return [error["error_message"] for error in errors]
    return []

async def check_no_errors() -> None:
    """
    Check if there are any errors.

    Raises:
    - ErrorsPresentError: If errors are found.
    """
    errors = await get_errors()
    if errors:
        logging.error(f"Errors found: {errors}")
        raise ErrorsPresentError("Errors found")

@misc_router.get("/healthcheck")
async def healthcheck() -> JSONResponse:
    # TODO healthcheck
    try:
        results = await asyncio.gather(
            check_db_availability(),
            check_services_availability([{"name": "example", "url": "http://example.com"}]), # пример сервиса
            check_resources_availability(),
            check_no_errors(),
            return_exceptions=True
        )
    except Exception as e:
        logging.error(f"Healthcheck failed with exception: {e}")
        return JSONResponse({"error": "Internal error"}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    for result in results:
        if isinstance(result, DatabaseUnavailableError):
            return JSONResponse({"error": "Database is not available"}, status_code=HTTPStatus.SERVICE_UNAVAILABLE)
        elif isinstance(result, ServiceUnavailableError):
            return JSONResponse({"error": "Services are not available"}, status_code=HTTPStatus.SERVICE_UNAVAILABLE)
        elif isinstance(result, ResourceUnavailableError):
            return JSONResponse({"error": "Resources are not available"}, status_code=HTTPStatus.SERVICE_UNAVAILABLE)
        elif isinstance(result, ErrorsPresentError):
            return JSONResponse({"error": "Errors are present"}, status_code=HTTPStatus.SERVICE_UNAVAILABLE)

    return JSONResponse({"status": "OK"}, status_code=HTTPStatus.OK)