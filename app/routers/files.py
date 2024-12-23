from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.db import get_db, get_current_user
from app.models.files_model import StoredFile
from app.schemas.file import StoredFileResponse, StoredFileBase

router = APIRouter()

@router.post("/{bucket_name}/{file_key}")
async def upload_file(bucket_name: str, file_key: str, db: Session = Depends(get_db)):
    stored_file = StoredFileBase(
        filename="example.txt",
        url=f"/{bucket_name}/{file_key}",
        owner_id=1
    )
    db.add(stored_file)
    db.commit()
    db.refresh(stored_file)

    return stored_file.url


@router.get("/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return crud.download_file(db, file_id, user)

@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    crud.delete_file(db, file_id, user)
    return {"detail": "StoredFile deleted"}

@router.get("/all")
def list_files(db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return crud.list_files(db, user)
