import time
import os
import math
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sensor.entropy import calculate_entropy

MAGIC_NUMBERS = {
    '.pdf': b'%PDF', '.zip': b'PK', '.xlsx': b'PK', '.docx': b'PK',
    '.jar': b'PK', '.png': b'\x89PNG', '.jpg': b'\xFF\xD8\xFF', '.db': b'SQLite format 3'
}

def is_valid_header(filepath):
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    if ext not in MAGIC_NUMBERS: return True
    try:
        if os.path.getsize(filepath) == 0: return True
        with open(filepath, 'rb') as f:
            header = f.read(len(MAGIC_NUMBERS[ext]))
            return header.startswith(MAGIC_NUMBERS[ext])
    except: return True 

class AegisHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.last_scan = {}

    def on_modified(self, event):
        if event.is_directory: return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        if time.time() - self.last_scan.get(filepath, 0) < 1.0: return
        self.last_scan[filepath] = time.time()
        time.sleep(0.1)

        trap = 1 if "config.sys" in filename else 0
        entropy = calculate_entropy(filepath)
        
        bad_header = 0
        if not is_valid_header(filepath):
            bad_header = 1

        # NOTE: Removed 'rate' calculation here. app.py does it for real now.
        packet = f"ENTROPY:{entropy:.2f}|TRAP:{trap}|BADHEADER:{bad_header}|PATH:{filepath}"
        self.callback(packet)

def start_monitoring(path, callback):
    event_handler = AegisHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print(f"👁️ WATCHDOG ACTIVE: Scanning {path}...")