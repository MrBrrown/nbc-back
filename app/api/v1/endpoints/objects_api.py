import pathlib

from fastapi import APIRouter, UploadFile
from fastapi.responses import Response
from starlette.responses import FileResponse

object_router = APIRouter()

root_dir = f'C:\\Users\\novna\\OneDrive\\Рабочий стол\\'

@object_router.get("/{bucket_name}")
async def get_objects_metadata(bucket_name: str):
    pass


def create_dirs(path):
    # Получите директорию из пути к файлу
    dir_path = pathlib.Path(path).parent

    # Если директория не существует, создайте ее
    if not dir_path.exists():
        # Создайте все директории в пути
        dir_path.mkdir(parents=True)


@object_router.put("/{bucket_name}")
async def upload_object (bucket_name: str, file: UploadFile):
    object_name = file.filename
    path = f'{root_dir}\\{bucket_name}\\{object_name}'
    create_dirs(path)
    with open(path, "wb") as f:
        f.write(await file.read())


def read_object_content(path):
    with open(path, "rb") as f:
        f.read()
    pass


@object_router.get("/{bucket_name}/{object_name}")
async def download_object (bucket_name: str, object_name: str):
    path = f'{root_dir}\\{bucket_name}\\{object_name}'
    return FileResponse(path)



@object_router.head("/{bucket_name}/{object_name}")
async def get_object_metadata (bucket_name: str, object_name: str):
    pass

@object_router.delete("/{bucket_name}/{object_name}")
async def delete_object (bucket_name: str, object_name: str):
    pass