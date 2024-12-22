from fastapi import APIRouter, UploadFile, File, Depends
from app import crud, schemas
from app.db import get_db, get_current_user

router = APIRouter()

@router.post("/upload", response_model=schemas.FileResponse)
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    file_url = crud.upload_file(db, file, user)
    return {"url": file_url}

@router.get("/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return crud.download_file(db, file_id, user)

@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    crud.delete_file(db, file_id, user)
    return {"detail": "File deleted"}

@router.get("/all")
def list_files(db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return crud.list_files(db, user)
