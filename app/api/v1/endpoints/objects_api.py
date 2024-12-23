import os.path
import pathlib
from fastapi import APIRouter, UploadFile, File
from fastapi.params import Body
from starlette.responses import FileResponse
from app.models.users_model import User
from app.models.object import Object
from app.models.bucket import Bucket
from app.core.config import settings

object_router = APIRouter()

root_dir = settings.fileStorage.root_dir


@object_router.get("/{bucket_name}")
async def get_objects_metadata(bucket_name: str):

    pass

def create_dirs(path):
    dir_path = pathlib.Path(path).parent

    if not dir_path.exists():
        # Создайте все директории в пути
        dir_path.mkdir(parents=True)

@object_router.put("/{bucket_name}/{object_key}")
async def upload_object (bucket_name: str, object_key: str, file: UploadFile = File(...)):
    full_uploaded_filename_with_extension = file.filename
    extension_without_dot = full_uploaded_filename_with_extension.split(".")[1]
    path = os.path.join(root_dir,bucket_name, f'{object_key}.{extension_without_dot}')
    create_dirs(path)
    with open(path, "wb") as f:
        f.write(await file.read())
    return {"detail": f"Object '{object_key}' in bucket '{bucket_name}' uploaded successfully. Path to uploaded file: {path}"}


def read_object_content(path):
    with open(path, "rb") as f:
        f.read()

@object_router.get("/{bucket_name}/{object_key}")
async def download_object (bucket_name: str, object_key: str):
    path = f'{root_dir}\\{bucket_name}\\{object_key}'
    return FileResponse(path)

@object_router.head("/{bucket_name}/{object_key}")
async def get_object_metadata (bucket_name: str, object_key: str):
    pass

@object_router.delete("/{bucket_name}/{object_key}")
async def delete_object (bucket_name: str, object_key: str):
    pass
