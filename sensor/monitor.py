import time
import math
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# KNOWN FILE HEADERS
FILE_SIGNATURES = {
    '.pdf': b'%PDF', '.zip': b'PK', '.docx': b'PK', '.xlsx': b'PK',
    '.png': b'\x89PNG', '.jpg': b'\xFF\xD8', '.jpeg': b'\xFF\xD8'
}

class AegisHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.file_counter = 0
        self.start_time = time.time()
        
    def calculate_entropy(self, data):
        if not data: return 0
        entropy = 0
        for x in range(256):
            p_x = data.count(x) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
        return entropy

    def check_magic_bytes(self, filepath):
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        if ext not in FILE_SIGNATURES: return 0
        try:
            expected_header = FILE_SIGNATURES[ext]
            with open(filepath, 'rb') as f:
                file_header = f.read(len(expected_header))
            if file_header != expected_header: return 1 
        except: pass
        return 0 

    def on_modified(self, event):
        if event.is_directory: return

        try:
            # --- 1. WAIT FOR WRITE TO FINISH (CRITICAL) ---
            # We wait 0.1s so the file (Safe or Malicious) is fully written 
            # before we inspect it. This fixes the Race Condition.
            time.sleep(0.1)

            # --- 2. SMART TRAP DETECTION ---
            is_trap = 0
            if "config.sys" in event.src_path.lower():
                try:
                    # Read the content to see WHO touched it
                    with open(event.src_path, 'r', errors='ignore') as f:
                        content = f.read().strip()
                    
                    # If it matches our Safe String, it's just Option 1 (Reset).
                    if content == "SYSTEM_CONFIGURATION_DO_NOT_TOUCH":
                        is_trap = 0 # FALSE ALARM (It's us)
                    else:
                        # Content changed (e.g. "INFECTED" added) -> REAL ATTACK
                        print(f"🪤 TRAP TRIGGERED (Content Modified): {event.src_path}")
                        is_trap = 1 
                except:
                    # If locked or unreadable, assume Danger
                    is_trap = 1

            # --- 3. HEADER CHECK ---
            is_corrupted = self.check_magic_bytes(event.src_path)

            # --- 4. RATE CALCULATION ---
            self.file_counter += 1
            current_time = time.time()
            if current_time - self.start_time >= 1.0:
                rate = self.file_counter
                self.file_counter = 0
                self.start_time = current_time
            else:
                rate = self.file_counter

            # --- 5. ENTROPY CALCULATION ---
            entropy = 0.0
            try:
                with open(event.src_path, 'rb') as f:
                    data = f.read()
                    entropy = self.calculate_entropy(data)
            except PermissionError:
                print(f"🔒 FILE LOCKED: {event.src_path}")
                entropy = 8.0 
            except: pass

            data_packet = f"RATE:{rate}|ENTROPY:{entropy:.2f}|TRAP:{is_trap}|BAD_HEADER:{is_corrupted}|PATH:{event.src_path}"
            self.callback(data_packet)

        except Exception as e:
            print(f"❌ SENSOR ERROR: {e}")

def start_monitoring(path, callback):
    event_handler = AegisHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    return observer