from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from prometheus_client import generate_latest
import logging
import app.models
import app.core.metrics

app = FastAPI()

@app.post("/users/")
def create_user(username: str):
    session = SessionLocal()
    try:
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = User(username=username)
        session.add(new_user)
        session.commit()
        logging.info(f"Created new user: {username}")
        return {"message": "User created successfully", "username": username}
    finally:
        session.close()

@app.get("/users/{username}")
def check_user(username: str):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {"username": user.username, "file_count": len(user.files)}
    finally:
        session.close()

@app.post("/upload/")
@upload_time_summary.time()
async def upload_file(username: str, file: UploadFile = File(...)):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        file_path = os.path.join(STORAGE_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)

        file_metadata = FileMetadata(
            filename=file.filename, filepath=file_path, size=file_size, owner=user
        )
        session.add(file_metadata)
        session.commit()
        uploaded_files_counter.inc()
        logging.info(f"Uploaded file: {file.filename} by user: {username}, size: {file_size} bytes")
    finally:
        session.close()

    return {"message": "File uploaded successfully", "filename": file.filename}

@app.get("/download/{file_id}")
async def download_file(file_id: int):
    session = SessionLocal()
    try:
        file_metadata = session.query(FileMetadata).filter(FileMetadata.id == file_id).first()
        if not file_metadata:
            raise HTTPException(status_code=404, detail="File not found")
        downloaded_files_counter.inc()
        logging.info(f"Downloaded file: {file_metadata.filename}")
        return FileResponse(file_metadata.filepath, filename=file_metadata.filename)
    finally:
        session.close()

@app.delete("/delete/{file_id}")
async def delete_file(file_id: int):
    session = SessionLocal()
    try:
        file_metadata = session.query(FileMetadata).filter(FileMetadata.id == file_id).first()
        if not file_metadata:
            raise HTTPException(status_code=404, detail="File not found")

        os.remove(file_metadata.filepath)
        session.delete(file_metadata)
        session.commit()
        deleted_files_counter.inc()
        logging.info(f"Deleted file: {file_metadata.filename}")
        return {"message": "File deleted successfully"}
    finally:
        session.close()

@app.put("/rename/file/{file_id}")
async def rename_file(file_id: int, new_name: str):
    session = SessionLocal()
    try:
        file_metadata = session.query(FileMetadata).filter(FileMetadata.id == file_id).first()
        if not file_metadata:
            raise HTTPException(status_code=404, detail="File not found")

        new_file_path = os.path.join(STORAGE_DIR, new_name)
        os.rename(file_metadata.filepath, new_file_path)
        file_metadata.filepath = new_file_path
        file_metadata.filename = new_name
        session.commit()
        logging.info(f"Renamed file ID {file_id} to {new_name}")
        return {"message": "File renamed successfully", "new_name": new_name}
    finally:
        session.close()

@app.put("/rename/folder/{folder_name}")
async def rename_folder(folder_name: str, new_folder_name: str):
    old_folder_path = os.path.join(STORAGE_DIR, folder_name)
    new_folder_path = os.path.join(STORAGE_DIR, new_folder_name)

    if not os.path.exists(old_folder_path) or not os.path.isdir(old_folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")

    os.rename(old_folder_path, new_folder_path)
    logging.info(f"Renamed folder {folder_name} to {new_folder_name}")
    return {"message": "Folder renamed successfully", "new_folder_name": new_folder_name}

@app.get("/files/")
def list_files():
    session = SessionLocal()
    try:
        files = session.query(FileMetadata).all()
        return [
            {
                "id": file.id,
                "filename": file.filename,
                "size": file.size,
                "upload_date": file.upload_date
            }
            for file in files
        ]
    finally:
        session.close()

@app.get("/metrics/")
def metrics():
    return generate_latest()

@app.get("/health/")
def health_check():
    try:
        session = SessionLocal()
        session.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return {"status": "unhealthy"}