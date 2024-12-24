import os.path
import pathlib
import re
from datetime import datetime
from typing import List

import structlog
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import FileResponse, Response, JSONResponse

from ....core.config import settings
from ....repositories.bucket_repository import BucketRepository, get_bucket_repository
from ....repositories.object_repository import get_object_repository, ObjectRepository
from ....schemas.object_schema import ObjectResponse
from ....schemas.user_schema import UserResponse
from ....services.auth_service import get_current_user

object_router = APIRouter()

logger = structlog.get_logger()

root_dir = settings.fileStorage.root_dir

def create_dirs(path):
    dir_path = pathlib.Path(path).expanduser().parent
    if not dir_path.exists():
        # Создайте все директории в пути
        dir_path.mkdir(parents=True)

@object_router.put("/{bucket_name}/{object_key}")
async def upload_object (bucket_name: str,
                         object_key: str,
                         file: UploadFile = File(...),
                         current_user: UserResponse = Depends(get_current_user),
                         bucket_repo: BucketRepository = Depends(get_bucket_repository),
                         object_repo: ObjectRepository = Depends(get_object_repository),
                         request: Request = None):

    # check if bucket is owned by current user
    bucket = await bucket_repo.get_bucket_by_name(bucket_name)

    if bucket is None or bucket.owner_name != current_user.username:
        raise HTTPException(status_code=403, detail="You do not have permission to upload to this bucket")

    full_uploaded_filename_with_extension = file.filename
    base_name, extension_with_dot = os.path.splitext(full_uploaded_filename_with_extension)
    extension_without_dot = extension_with_dot[1:] if extension_with_dot else ""
    path = pathlib.Path(os.path.join(root_dir, bucket_name, object_key)).expanduser()
    create_dirs(path)
    with open(path, "wb") as f:
        f.write(await file.read())

    download_url = f"{request.base_url}api/v1/{bucket_name}/{object_key}"
    size = os.path.getsize(path)
    await object_repo.create_object(bucket_name, object_key, current_user.username, extension_without_dot, str(path), download_url, size)
    object_metadata = {
        "Location": download_url,
        "Bucket-Name": bucket_name,
        "Object-Key": object_key
    }
    logger.info(f"Object '{object_key}' in bucket '{bucket_name}' uploaded successfully. Path to uploaded file: {path}")
    return JSONResponse(content=object_metadata, status_code=200, headers=object_metadata)

@object_router.get("/{bucket_name}/{object_key}")
async def download_object (bucket_name: str,
                           object_key: str,
                           current_user: UserResponse = Depends(get_current_user),
                           bucket_repo: BucketRepository = Depends(get_bucket_repository)
                           ):
    # check if bucket is owned by current user
    bucket = await bucket_repo.get_bucket_by_name(bucket_name)

    if bucket is None or bucket.owner_name != current_user.username:
        raise HTTPException(status_code=403, detail="You do not have permission to download from this bucket")

    path = pathlib.Path(os.path.join(root_dir,bucket_name, object_key)).expanduser()
    if not os.path.exists(path) or not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"Object '{object_key}' in bucket '{bucket_name}' not found")
    return FileResponse(path)

@object_router.head("/{bucket_name}/{object_key}/metadata", response_description="Get metadata for a specific object")
async def get_object_metadata(bucket_name: str, object_key: str, response: Response,
                              current_user: UserResponse = Depends(get_current_user)):
    # Вызываем общую функцию и добавляем метаданные в заголовки
    metadata = await get_obj_metadata(bucket_name, object_key)

    # Добавляем метаданные в заголовки ответа
    response.headers["X-File-Name"] = metadata["name"]
    response.headers["X-File-Size-KB"] = str(metadata["size_KB"])
    response.headers["X-File-Created"] = metadata["created"]
    response.headers["X-File-Modified"] = metadata["modified"]

    return None

@object_router.get("/{bucket_name}", response_description="Get metadata for all objects in a bucket")
async def get_objects_metadata(bucket_name: str,
                                current_user: UserResponse = Depends(get_current_user),
                                bucket_repo: BucketRepository = Depends(get_bucket_repository),
                                object_repo: ObjectRepository = Depends(get_object_repository)
                               ) -> List[ObjectResponse]:
    try:
        # Получить информацию о бакете
        bucket = await bucket_repo.get_bucket_by_name(bucket_name)
        # Проверить, принадлежит ли бакет текущему пользователю
        if bucket is None or bucket.owner_name != current_user.username:
            raise HTTPException(status_code=403, detail="You do not have permission to access this bucket")
        bucket_path = pathlib.Path(os.path.join(root_dir, bucket_name)).expanduser()
        objects =  await object_repo.get_all_objects(bucket_name, current_user.username)
        return objects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading files in bucket '{bucket_name}': {e}")

# Helper function to get file metadata
def get_file_metadata(file_path: pathlib.Path) -> dict:
    try:
        return {
            "name": file_path.name,
            "size_KB": (file_path.stat().st_size // 1024) if file_path.stat().st_size > 1024 else file_path.stat().st_size,
            "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metadata for {file_path.name}: {e}")

async def get_obj_metadata(bucket_name: str, object_key: str) -> dict:
    # Логирование пути к объекту
    object_path = pathlib.Path(os.path.join(root_dir, bucket_name, object_key)).expanduser()
    logger.info(f"Fetching metadata for: {object_path}")

    if not os.path.exists(object_path) or not os.path.isfile(object_path):
        logger.warning(f"Object '{object_key}' in bucket '{bucket_name}' not found")
        raise HTTPException(status_code=404, detail=f"Object '{object_key}' in bucket '{bucket_name}' not found")

    # Получение метаданных
    metadata = get_file_metadata(pathlib.Path(object_path))

    # Логирование метаданных
    logger.info(f"Metadata: {metadata}")

    return metadata

@object_router.delete("/{bucket_name}/{object_key}")
async def delete_object (bucket_name: str, object_key: str,
                         current_user: UserResponse = Depends(get_current_user)):
    # Проверка на запрещённые символы в пути
    if re.search(r'[<>:"/\\|?*]', bucket_name) or re.search(r'[<>:"/\\|?*]', object_key):
        raise HTTPException(status_code=400, detail="Invalid characters in bucket name or object key")

    path_file_to_delete = pathlib.Path(os.path.join(root_dir,bucket_name, object_key)).expanduser()

    try:
        if os.path.exists(path_file_to_delete) and os.path.isfile(path_file_to_delete):
            os.remove(path_file_to_delete)
            return {"detail": f"Object '{object_key}' in bucket '{bucket_name}' deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Object '{object_key}' in bucket '{bucket_name}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while deleting the object: {e}")
