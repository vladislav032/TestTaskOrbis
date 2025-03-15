# File Management

### 1. Установка зависимостей
Убедитесь, что у вас установлен Python 3. Затем установите зависимости:
```bash
pip install -r requirements.txt
```

### 2. Запуск приложения
```bash
python app.py
```
Приложение запустится на `http://127.0.0.1:5000/`.

## Конфигурация
Конфигурационные параметры хранятся в файле `config.py`:
- `DOWNLOAD_DIR` – папка для загрузки файлов (`./download`).
- `DATABASE_URL` – путь к базе данных SQLite (`sqlite:///./storage.db`).
- `STORAGE_DIR` – папка для хранения загруженных файлов (`./file_storage`).

## Основные эндпоинты

### 1. Получение списка всех файлов
**GET** `/files`
#### cURL-запрос:
```bash
curl -X GET http://127.0.0.1:5000/files
```
#### Ответ:
```json
[
  {
    "id": 1,
    "name": "example",
    "extension": ".txt",
    "size": 1234,
    "path": "./file_storage/example.txt",
    "created_at": "2024-03-14T12:00:00",
    "updated_at": null,
    "comment": "Sample file"
  }
]
```

### 2. Получение информации о файле по ID
**GET** `/files/<int:file_id>`
#### cURL-запрос:
```bash
curl -X GET http://127.0.0.1:5000/files/1
```
#### Ответ:
```json
{
  "name": "example",
  "extension": ".txt",
  "size": 1234,
  "path": "./file_storage/example.txt",
  "created_at": "2024-03-14T12:00:00",
  "updated_at": null,
  "comment": "Sample file"
}
```

### 3. Загрузка файла
**POST** `/files`
#### cURL-запрос:
```bash
curl -X POST http://127.0.0.1:5000/files \
     -F "file=@/path/to/your/file.txt" \
     -F "comment=This is a test file"
```
#### Ответ:
```json
{
  "message": "File uploaded successfully"
}
```

### 4. Удаление файла
**DELETE** `/files/<int:file_id>`
#### cURL-запрос:
```bash
curl -X DELETE http://127.0.0.1:5000/files/1
```
#### Ответ:
```json
{
  "msg": "File deleted successfully"
}
```

### 5. Скачивание файла
**GET** `/files/download/<int:file_id>`
#### cURL-запрос:
```bash
curl -X GET http://127.0.0.1:5000/files/download/1 -o downloaded_file.txt
```
#### Ответ:
Файл будет скачан в указанное место (`downloaded_file.txt`).

### 6. Изменение информации о файле
**PUT** `/files/<int:file_id>`

Этот эндпоинт позволяет изменить путь хранения файла и его комментарий.

#### Параметры:
- `path` (опционально) — новый путь для перемещения файла.
- `comment` (опционально) — обновленный комментарий к файлу.
- `name` (опционально) — обновленное название файла.

#### cURL-запрос:
```bash
curl -X PUT "http://127.0.0.1:5000/files/1"
     -H "Content-Type: application/json"
     -d "{\"name\": \"new_filename\", \"path\": \"./new/path/\", \"comment\": \"Updated comment\"}"
```

### 7. Поиск файлов по части пути
**GET** `/files/search?path=<substring>`

Этот эндпоинт позволяет получить список файлов, путь которых содержит указанную подстроку.

#### Пример cURL-запроса:
```bash
curl -X GET "http://127.0.0.1:5000/files/search?path=subfolder"
```
#### Возможные применения:
- Поиск всех файлов, расположенных в определенной папке.
- Фильтрация файлов по их относительному пути.
- Упрощение поиска файлов при наличии глубокой структуры директорий.

#### Ответ:
```json
[
  {
    "id": 2,
    "name": "report",
    "extension": ".pdf",
    "size": 4567,
    "path": "./file_storage/subfolder/report.pdf",
    "created_at": "2024-03-14T15:30:00",
    "updated_at": null,
    "comment": "Annual report"
  }
]
```

## Функция синхронизации файлов
Фоновый процесс автоматически синхронизирует файлы в `STORAGE_DIR` с базой данных. Если файл отсутствует в папке, он удаляется из БД. Если новый файл появляется в `STORAGE_DIR`, он добавляется в БД.

## Структура проекта
```
src/
│── app.py          # Главный файл для запуска Flask API
│── config.py       # Конфигурационные параметры
│── database.py     # Инициализация базы данных
│── file_handler.py # Функции работы с файлами
│── models.py       # Определение таблиц базы данных
│── routes.py       # Определение API-маршрутов
│── utils.py        # Вспомогательные функции, включая синхронизацию
requirements.txt # Список зависимостей
storage.db      # SQLite база данных (создается автоматически)
file_storage/   # Директория для хранения загруженных файлов
download/       # Директория для скачивания файлов
```
