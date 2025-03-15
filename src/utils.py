from database import SessionLocal
from routes import STORAGE_DIR
from models import FileRecord
from datetime import datetime
import os

# Функция синхронизации
def sync_files():
    session = SessionLocal()
    
    db_files = {file.path: file for file in session.query(FileRecord).all()}
    
    storage_files = set(os.listdir(STORAGE_DIR))

    for file_path, file_record in list(db_files.items()):
        if not os.path.exists(file_path):
            session.delete(file_record)

    for filename in storage_files:
        file_path = os.path.join(STORAGE_DIR, filename)
        name, extension = os.path.splitext(filename)

        existing_file = db_files.get(file_path)

        file_size = os.path.getsize(file_path)
        created_at = datetime.fromtimestamp(os.path.getctime(file_path))

        if existing_file:
            if existing_file.size != file_size:
                existing_file.size = file_size
                existing_file.updated_at = datetime.utcnow()
            if existing_file.created_at != created_at:
                existing_file.created_at = created_at
        else:
            new_file = FileRecord(
                name=name,
                extension=extension,
                size=file_size,
                path=file_path,
                created_at=created_at
            )
            session.add(new_file)

    existing_paths = {}
    duplicates = []
    for file in session.query(FileRecord).all():
        if file.path in existing_paths:
            if file.comment:
                duplicates.append(existing_paths[file.path])
                existing_paths[file.path] = file
            else:
                duplicates.append(file)
        else:
            existing_paths[file.path] = file
    
    for duplicate in duplicates:
        session.delete(duplicate)

    session.commit()
    session.close()

