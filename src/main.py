import time
import shutil
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from integrity import get_file_hash

# Ścieżki bezwzględne
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(BASE_DIR, "target_dir")
BACKUP = os.path.join(BASE_DIR, "backups")

reference_hashes = {}

def load_reference_hashes():
    # flush=True wymusza natychmiastowe pojawienie się tekstu w logach systemd
    print("--- Inicjalizacja: Ładowanie wzorcowych haszy ---", flush=True)
    if not os.path.exists(BACKUP):
        print(f"BŁĄD: Folder backupu {BACKUP} nie istnieje!", flush=True)
        return

    for filename in os.listdir(BACKUP):
        path = os.path.join(BACKUP, filename)
        if os.path.isfile(path):
            h = get_file_hash(path)
            if h:
                reference_hashes[filename] = h
                print(f"  [OK] Załadowano wzorzec: {filename}", flush=True)
    print("--- Inicjalizacja zakończona ---\n", flush=True)

class MonitorHandler(FileSystemEventHandler):
    def check_and_restore(self, filename, target_path):
        current_hash = get_file_hash(target_path)
        expected_hash = reference_hashes.get(filename)

        if current_hash == expected_hash:
            return 

        print(f"!!! ALARM: Wykryto zmianę lub brak pliku: {filename}", flush=True)
        backup_path = os.path.join(BACKUP, filename)
        
        if os.path.exists(backup_path):
            try:
                shutil.copy(backup_path, target_path)
                print(f"+++ Przywrócono poprawną wersję pliku: {filename}", flush=True)
            except Exception as e:
                print(f"BŁĄD podczas przywracania: {e}", flush=True)
        else:
            print(f"xxx Brak kopii zapasowej dla: {filename}", flush=True)

    def on_modified(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            self.check_and_restore(filename, event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            self.check_and_restore(filename, event.src_path)

if __name__ == "__main__":
    os.makedirs(TARGET, exist_ok=True)
    os.makedirs(BACKUP, exist_ok=True)

    load_reference_hashes()
    
    event_handler = MonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, TARGET, recursive=False)
    
    print(f"System aktywny. Obserwuję folder: {TARGET}", flush=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
