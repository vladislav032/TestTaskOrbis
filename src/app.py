from flask import Flask
from database import init_db
from routes import bp
from utils import sync_files
import threading

app = Flask(__name__)
app.register_blueprint(bp)

def start_sync_task():
    def sync_loop():
        while True:
            with app.app_context():
                try:
                    sync_files()
                except Exception as e:
                    print(f"Ошибка синхронизации: {e}")

    thread = threading.Thread(target=sync_loop, daemon=True)
    thread.start()

if __name__ == "__main__":
    with app.app_context():
        init_db()
        start_sync_task()
    
    app.run(debug=True, use_reloader=False)
