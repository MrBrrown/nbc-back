import os.path
import pathlib
from fastapi import APIRouter, UploadFile
from fastapi.params import Body
from app.models.users_model import User
from app.models.files_model import StoredFile
from app.models.bucket_model import Bucket
from app.core.config import settings
from app.schemas.file import StoredFileResponse, StoredFileBase

file_router = APIRouter(tags=["StoredFiles"])

root_dir = settings.fileStorage.root_dir


@file_router.get("/{bucket_name}")
async def get_files_metadata(bucket_name: str):

    pass

def create_dirs(path):
    dir_path = pathlib.Path(path).parent

    if not dir_path.exists():
        dir_path.mkdir(parents=True)

@file_router.post("/{bucket_name}/{file_key}")
async def upload_file (bucket_name: str, file_key: str, file: StoredFileBase):
    full_uploaded_filename_with_extension = file.filename
    extension_without_dot = full_uploaded_filename_with_extension.split(".")[1]
    path = os.path.join(root_dir,bucket_name, f'{file_key}.{extension_without_dot}')
    create_dirs(path)
    with open(path, "wb") as f:
        f.write(await file.read())
    return {"detail": f"StoredFile '{file_key}' in bucket '{bucket_name}' uploaded successfully. Path to uploaded file: {path}"}


def read_file_content(path):
    with open(path, "rb") as f:
        f.read()

@file_router.get("/{bucket_name}/{file_key}")
async def download_file (bucket_name: str, file_key: str):
    path = f'{root_dir}\\{bucket_name}\\{file_key}'
    return StoredFileResponse(path)

@file_router.head("/{bucket_name}/{file_key}")
async def get_file_metadata (bucket_name: str, file_key: str):
    pass

@file_router.delete("/{bucket_name}/{file_key}")
async def delete_file (bucket_name: str, file_key: str):
    pass
