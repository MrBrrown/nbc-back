from fastapi import APIRouter
import asyncio
import aiohttp
import logging
import psutil
from typing import Dict, List
from starlette.responses import JSONResponse
from http import HTTPStatus

misc_router = APIRouter(tags=["Misc"])

async def check_db_availability(db_host: str, db_port: int, timeout: int = 5) -> bool:
    """
    Check if a database is available.

    Args:
    - db_host (str): Database host.
    - db_port (int): Database port.
    - timeout (int): Timeout in seconds. Defaults to 5.

    Returns:
    - bool: True if the database is available, False otherwise.
    """
    try:
        # Create a socket with a timeout
        reader, writer = await asyncio.wait_for(asyncio.open_connection(db_host, db_port), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except (ConnectionRefusedError, asyncio.TimeoutError):
        logging.error(f"Database at {db_host}:{db_port} is not available")
        return False

async def check_services_availability(services: List[Dict[str, str]]) -> None:
    async with aiohttp.ClientSession() as session:
        for service in services:
            try:
                async with session.get(service['url']) as response:
                    if response.status == 200:
                        print(f"{service['name']} is available")
                    else:
                        print(f"{service['name']} is not available")
            except aiohttp.ClientError:
                print(f"Failed to check {service['name']}")

async def check_resources_availability() -> Dict[str, bool]:
    # Get current system resource usage
    cpu_usage: float = psutil.cpu_percent()
    memory_usage: float = psutil.virtual_memory().percent
    disk_usage: float = psutil.disk_usage('/').percent

    # Define thresholds for resource availability
    cpu_threshold: int = 80
    memory_threshold: int = 90
    disk_threshold: int = 90

    # Check if resources are available
    cpu_available: bool = cpu_usage < cpu_threshold
    memory_available: bool = memory_usage < memory_threshold
    disk_available: bool = disk_usage < disk_threshold

    # Return a dictionary with resource availability status
    return {
        'cpu': cpu_available,
        'memory': memory_available,
        'disk': disk_available
    }


async def get_errors() -> list[str]:
    #TODO
    # Replace this with your actual error retrieval logic
    # For example, let's assume we're retrieving errors from a database
    # errors = await database.query("SELECT error_message FROM errors")
    # return [error["error_message"] for error in errors]
    return []

async def check_no_errors() -> None:
    errors = await get_errors()
    if errors:
        raise Exception("Errors found")

@misc_router.get("/healthcheck")
async def healthcheck() -> JSONResponse:
    try:
        db_status, services_status, resources_status, errors_status = await asyncio.gather(
            check_db_availability(),
            check_services_availability(),
            check_resources_availability(),
            check_no_errors(),
        )
    except Exception as e:
        logging.error(f"Healthcheck failed with exception: {e}")
        return JSONResponse({"error": "Internal error"}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    if not db_status:
        logging.warning("Database is not available")
        return JSONResponse({"error": "Database is not available"}, status_code=HTTPStatus.SERVICE_UNAVAILABLE)

    if not services_status:
        logging.warning("Services are not available")
        return JSONResponse({"error": "Services are not available"}, status_code=HTTPStatus.SERVICE_UNAVAILABLE)

    if not resources_status:
        logging.warning("Resources are not available")
        return JSONResponse({"error": "Resources are not available"}, status_code=HTTPStatus.SERVICE_UNAVAILABLE)

    if not errors_status:
        logging.warning("Errors are present")
        return JSONResponse({"error": "Errors are present"}, status_code=HTTPStatus.SERVICE_UNAVAILABLE)

    return JSONResponse({"status": "OK"}, status_code=HTTPStatus.OK)
