import os
from datetime import datetime
from config import STORAGE_DIR

def save_file(file, filename):
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
        
    file_path = os.path.join(STORAGE_DIR, filename)
    file.save(file_path)
    
    return {
        'size': os.path.getsize(file_path),
        'created_at': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
    }

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False