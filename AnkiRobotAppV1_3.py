import os
import sys
import webview
import AnkiGeneratorRobustV1_3App as AnkiGeneratorBackend
import threading
import shutil

class Api:
    def __init__(self, window=None):
        self._window = window

    def check_api_key(self):
        if os.environ.get("MISTRAL_API_KEY"):
            return True
        user_home = os.path.expanduser("~")
        env_path = os.path.join(user_home, "Anki_Generated_Decks", ".env")
        if not os.path.exists(env_path):
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith("MISTRAL_API_KEY="):
                            key = line.split("=", 1)[1].strip()
                            if key:
                                os.environ["MISTRAL_API_KEY"] = key
                                return True
            except Exception as e:
                print(f"Error reading .env: {e}")
        return False

    def save_api_key(self, key):
        if not key:
            return False
        os.environ["MISTRAL_API_KEY"] = key
        user_home = os.path.expanduser("~")
        env_dir = os.path.join(user_home, "Anki_Generated_Decks")
        if not os.path.exists(env_dir):
            os.makedirs(env_dir, exist_ok=True)
        env_path = os.path.join(env_dir, '.env')
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(f"MISTRAL_API_KEY={key}\n")
            return True
        except Exception as e:
            print(f"Error saving API key: {e}")
            return False

    def delete_deck_folder(self, folder_name):
        try:
            user_home = os.path.expanduser("~")
            master_folder = os.path.join(user_home, "Anki_Generated_Decks")
            folder_path = os.path.join(master_folder, folder_name)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting folder: {e}")
            return False

    def choose_file(self):
        file_types = ('PDF Files (*.pdf)', 'All files (*.*)')
        result = self._window.create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=False,
            file_types=file_types
        )
        if result and len(result) > 0:
            return result[0]
        return None

    def start_processing(self, file_path, learning_depth):
        # Run in a separate thread to avoid blocking the UI
        def run():
            try:
                run_folder = AnkiGeneratorBackend.process_course(file_path, learning_depth)
                if run_folder and self._window:
                    self._window.evaluate_js(f"if (window.onProcessingComplete) window.onProcessingComplete('{run_folder}'); void(0);")
            except Exception as e:
                print(f"Error processing course: {e}")
                error_msg = str(e).replace('\\', '\\\\').replace("'", "\\'")
                if self._window:
                    self._window.evaluate_js(f"if (window.onProcessingError) window.onProcessingError('{error_msg}'); void(0);")
        
        threading.Thread(target=run, daemon=True).start()
        return True

    def get_library_books(self):
        try:
            user_home = os.path.expanduser("~")
            master_folder = os.path.join(user_home, "Anki_Generated_Decks")
            if not os.path.exists(master_folder):
                return []
            
            books = []
            folders = []
            for f in os.listdir(master_folder):
                full_path = os.path.join(master_folder, f)
                if os.path.isdir(full_path):
                    has_apkg = False
                    for root, dirs, files in os.walk(full_path):
                        if any(file.endswith('.apkg') for file in files):
                            has_apkg = True
                            break
                    if has_apkg:
                        ctime = os.path.getctime(full_path)
                        folders.append((f, ctime))
            
            # Sort folders by creation time ascending (sequentially)
            folders.sort(key=lambda x: x[1])
            
            colors = [
                '#B80035', '#0051D5', '#FACC15', '#22C55E', 
                '#8B5CF6', '#EC4899', '#3B82F6', '#10B981',
                '#F97316', '#EF4444', '#06B6D4', '#6366F1'
            ]
            
            for idx, (folder_name, ctime) in enumerate(folders):
                # Deterministic color choice based on name length/hash
                color = colors[hash(folder_name) % len(colors)]
                position = idx % 15
                books.append({
                    "id": folder_name,
                    "color": color,
                    "title": folder_name,
                    "position": position
                })
            return books
        except Exception as e:
            print(f"Error getting library books: {e}")
            return []

    def open_deck_folder(self, folder_name):
        try:
            user_home = os.path.expanduser("~")
            master_folder = os.path.join(user_home, "Anki_Generated_Decks")
            folder_path = os.path.join(master_folder, folder_name)
            if os.path.exists(folder_path):
                os.startfile(folder_path)
                return True
            return False
        except Exception as e:
            print(f"Error opening folder: {e}")
            return False

WEBVIEW_LOCK = threading.Lock()

def on_log(msg):
    with WEBVIEW_LOCK:
        try:
            escaped_msg = msg.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
            if window:
                window.evaluate_js(f"if (window.receiveLog) window.receiveLog(`{escaped_msg}`); void(0);")
        except Exception:
            pass

def on_progress(stage, status_text, progress_ratio):
    with WEBVIEW_LOCK:
        try:
            escaped_status = status_text.replace('\\', '\\\\').replace("'", "\\'")
            if window:
                window.evaluate_js(f"if (window.receiveProgress) window.receiveProgress({stage}, '{escaped_status}', {progress_ratio}); void(0);")
        except Exception:
            pass

if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        os.chdir(os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    dist_path = os.path.join(base_path, 'AnkiApp', 'dist')
    html_path = os.path.join(dist_path, 'index.html')
    
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found. Please build the Vite app first.")
        sys.exit(1)

    api = Api()
    
    window = webview.create_window(
        'Anki Robot AI V1.3 (Backend V1.3)', 
        url=html_path, 
        js_api=api,
        width=1280,
        height=800,
        min_size=(1024, 768)
    )
    api._window = window
    
    AnkiGeneratorBackend.UI_CALLBACK = on_log
    AnkiGeneratorBackend.PROGRESS_CALLBACK = on_progress

    webview.start(debug=False)
