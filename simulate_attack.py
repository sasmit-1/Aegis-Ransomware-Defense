import os
import time
import random
import shutil

# --- ABSOLUTE PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAFE_ZONE = os.path.join(BASE_DIR, "SafeZone")
HONEYPOT_FILE = os.path.join(SAFE_ZONE, "config.sys")

HEADERS = {
    'pdf': b'%PDF-1.4',
    'jpg': b'\xFF\xD8\xFF\xE0',
    'zip': b'PK\x03\x04'
}

def save_pid():
    """
    CRITICAL: SAVES THE MALWARE'S ID SO AEGIS CAN KILL IT.
    Real malware hides this, but for the demo, we broadcast it.
    """
    pid = os.getpid()
    with open("malware.pid", "w") as f:
        f.write(str(pid))
    print(f"👻 MALWARE PROCESS STARTED [PID: {pid}]")

def clean_safe_zone():
    """Helper to EMPTY the folder without deleting it."""
    if not os.path.exists(SAFE_ZONE):
        os.mkdir(SAFE_ZONE)
        return

    for filename in os.listdir(SAFE_ZONE):
        file_path = os.path.join(SAFE_ZONE, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def create_dummy_files():
    """OPTION 1: RESET & PREP"""
    print(f"🔄 Resetting {SAFE_ZONE}...")
    clean_safe_zone()

    # Create Honeypot
    with open(HONEYPOT_FILE, "w") as f:
        f.write("SYSTEM_CONFIGURATION_DO_NOT_TOUCH")

    # Create Text Files
    for i in range(10):
        with open(f"{SAFE_ZONE}/doc_{i}.txt", "w") as f:
            f.write(f"This is meaningful text file number {i}.\n" * 50)
            
    # Create Fake PDF/JPG
    for i in range(5):
        with open(f"{SAFE_ZONE}/image_{i}.pdf", "wb") as f:
            f.write(HEADERS['pdf'] + os.urandom(1024))
        with open(f"{SAFE_ZONE}/photo_{i}.jpg", "wb") as f:
            f.write(HEADERS['jpg'] + os.urandom(1024))

    print("✅ System Ready.")

def run_ransomware():
    """OPTION 2: THE NOISY ATTACK (Trap + Encryption)"""
    print("💀 RUNNING RANSOMWARE (Max Aggression)...")
    
    # 1. Trip the Trap
    print(f"🧨 Touching Honeypot: {HONEYPOT_FILE}")
    with open(HONEYPOT_FILE, "a") as f:
        f.write("INFECTED")
        
    # 2. Encrypt Everything
    files = [f for f in os.listdir(SAFE_ZONE) if os.path.isfile(os.path.join(SAFE_ZONE, f))]
    for file in files:
        if "config.sys" in file.lower(): continue
        
        try:
            path = os.path.join(SAFE_ZONE, file)
            with open(path, "rb") as f: data = f.read()
            
            # XOR Encryption
            encrypted = bytearray([b ^ 0xFF for b in data])
            
            with open(path, "wb") as f: f.write(encrypted)
            print(f"🔒 Encrypted: {file}")
            
            # SLOW DOWN TO BUILD TENSION (Was 0.05)
            # This allows the user to see the attack happening before killing it.
            time.sleep(0.3) 
        except: pass

def run_stealth_attack():
    """OPTION 3: STEALTH ATTACK (Entropy Only)"""
    print("🕵️ RUNNING STEALTH ATTACK...")
    files = [f for f in os.listdir(SAFE_ZONE) if f.endswith(".txt")]
    for file in files:
        try:
            path = os.path.join(SAFE_ZONE, file)
            # Overwrite with random bytes
            with open(path, "wb") as f: f.write(os.urandom(2048))
            print(f"⚠️  Corrupted: {file}")
            time.sleep(1.5) 
        except: pass

def run_header_attack():
    """OPTION 4: ZERO-DAY ATTACK (Header Corruption)"""
    print("🎭 RUNNING HEADER ATTACK...")
    files = [f for f in os.listdir(SAFE_ZONE) if f.endswith(".pdf") or f.endswith(".jpg")]
    for file in files:
        try:
            path = os.path.join(SAFE_ZONE, file)
            # Overwrite header
            with open(path, "r+b") as f:
                f.seek(0)
                f.write(b'GARBAGE!!!')
            print(f"🚫 Corrupted Header: {file}")
            time.sleep(1.0)
        except: pass

def run_safe_activity():
    """OPTION 5: SAFE USER SIMULATION"""
    print("😊 SIMULATING SAFE ACTIVITY...")
    for i in range(20, 30):
        with open(f"{SAFE_ZONE}/safe_doc_{i}.txt", "w") as f:
            f.write(f"Normal work data {i}.\n" * 100)
        print(f"📄 Created Safe Text: safe_doc_{i}.txt")
        time.sleep(0.1)

if __name__ == "__main__":
    save_pid() # <--- REGISTER AS MALWARE FIRST
    
    print("\n--- 🛡️ AEGIS ULTIMATE SIMULATOR 🛡️ ---")
    print("1. RESET SYSTEM")
    print("2. RANSOMWARE (Trap + Encryption)")
    print("3. STEALTH (Context-Aware)")
    print("4. ZERO-DAY (Header Attack)")
    print("5. SAFE ACTIVITY")
    
    choice = input("\nSelect (1-5): ")
    if choice == "1": create_dummy_files()
    elif choice == "2": run_ransomware()
    elif choice == "3": run_stealth_attack()
    elif choice == "4": run_header_attack()
    elif choice == "5": run_safe_activity()