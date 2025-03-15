from flask import Blueprint, request, jsonify, send_from_directory, current_app
from models import FileRecord
from datetime import datetime

from file_handler import save_file, delete_file, STORAGE_DIR
from config import DOWNLOAD_DIR
from database import SessionLocal

import os

bp = Blueprint('files', __name__)

# Получение списка всех файлв
@bp.route('/files', methods=['GET'])
def get_all_files():
    session = SessionLocal()
    files = session.query(FileRecord).all()
    session.close()
    
    return jsonify([{
        'id': file.id,
        'name': file.name,
        'extension': file.extension,
        'size': file.size,
        'path': file.path,
        'created_at': file.created_at.isoformat(),
        'updated_at': file.updated_at.isoformat() if file.updated_at else None,
        'comment': file.comment
    } for file in files])

# Получение информации по конкретному файлу
@bp.route('/files/<int:file_id>', methods=['GET'])
def get_files(file_id):
    session = SessionLocal()
    file = session.query(FileRecord).get(file_id)
    session.close()
    
    if not file:
        return jsonify({'error': 'File not found'}), 404
    
    return jsonify({
        'name': file.name,
        'extension': file.extension,
        'size': file.size,
        'path': file.path,
        'created_at': file.created_at.isoformat(),
        'updated_at': file.updated_at.isoformat() if file.updated_at else None,
        'comment': file.comment
    })

# Загрузка файла
@bp.route('/files', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    comment = request.form.get('comment')
    
    if not file:
        return jsonify({'error': 'No file provided!'}), 400
    
    filename = file.filename
    name, extension = os.path.splitext(filename)
    
    file_info = save_file(file, filename)
    
    session = SessionLocal()
    new_file = FileRecord(
        name=name,
        extension=extension,
        size=file_info['size'],
        path=os.path.join(STORAGE_DIR, filename),
        created_at=datetime.utcnow(),
        comment=comment
    )
    
    session.add(new_file)
    session.commit()
    session.close()
    
    return jsonify({'message': 'File uploaded successfully'}), 201

# Удаление файла
@bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file_route(file_id):
    session = SessionLocal()
    file = session.query(FileRecord).get(file_id)
    
    if not file:
        return jsonify({'error': 'File not found'}), 404
    
    if delete_file(file.path):
        session.delete(file)
        session.commit()
        session.close()
        return jsonify({'msg': 'File deleted successfully'}), 200
    else:
        return jsonify({'error': 'Failed to delete file!'}), 500

import shutil

# Скачивание файлов в папку ./download, если ее нет то создается
@bp.route('/files/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    session = SessionLocal()
    file = session.query(FileRecord).get(file_id)
    session.close()
    
    if not file:
        return jsonify({'error': 'File not found'}), 404
    
    file_path = file.path
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File does not exist on server'}), 404
    
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    destination_path = os.path.join(DOWNLOAD_DIR, os.path.basename(file_path))
    shutil.copy(file_path, destination_path)
    
    return send_from_directory(DOWNLOAD_DIR, os.path.basename(file_path), as_attachment=True)

# Изменения данных в бд
@bp.route('/files/<int:file_id>', methods=['PUT'])
def update_file_info(file_id):
    session = SessionLocal()
    file = session.query(FileRecord).get(file_id)
    
    if not file:
        session.close()
        return jsonify({'error': 'File not found'}), 404
    
    data = request.json
    new_name = data.get('name', file.name)
    new_path = data.get('path', os.path.dirname(file.path))
    new_comment = data.get('comment', file.comment)

    old_file_path = file.path
    new_file_name = f"{new_name}{file.extension}"
    new_file_path = os.path.join(new_path, new_file_name)

    if new_path != os.path.dirname(file.path) or new_name != file.name:
        if not os.path.exists(new_path):
            os.makedirs(new_path)

        if os.path.exists(old_file_path):
            os.rename(old_file_path, new_file_path)
            file.path = new_file_path
            file.name = new_name
        else:
            session.close()
            return jsonify({'error': 'Original file not found in storage'}), 404
        
    if new_comment != file.comment:
        file.comment = new_comment

    file.updated_at = datetime.utcnow()

    session.commit()
    session.close()

    return jsonify({'message': 'File information updated successfully'})

# Поиск по части пути
@bp.route('/files/search', methods=['GET'])
def search_files_by_path():
    search_path = request.args.get('path')

    if not search_path:
        return jsonify({'error': 'Path parameter is required'}), 400

    session = SessionLocal()
    files = session.query(FileRecord).filter(FileRecord.path.like(f"%{search_path}%")).all()
    session.close()

    if not files:
        return jsonify({'message': 'No files found matching the given path'}), 404

    return jsonify([{
        'id': file.id,
        'name': file.name,
        'extension': file.extension,
        'size': file.size,
        'path': file.path,
        'created_at': file.created_at.isoformat(),
        'updated_at': file.updated_at.isoformat() if file.updated_at else None,
        'comment': file.comment
    } for file in files])
