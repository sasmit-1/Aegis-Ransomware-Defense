import os
import time
import random
import sys

# --- CONFIGURATION ---
# Get the folder where this script lives (which is .../ADG/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# TARGET THE SAFE_ZONE DIRECTLY NEXT TO THE SCRIPT
SAFE_ZONE = os.path.join(BASE_DIR, "SafeZone")
TRAP_FILE = os.path.join(SAFE_ZONE, "config.sys")

def ensure_safezone_exists():
    """Just checks if the folder exists. Does NOT create files automatically."""
    if not os.path.exists(SAFE_ZONE):
        os.makedirs(SAFE_ZONE)
        print(f"📁 Created SafeZone directory at: {SAFE_ZONE}")

def reset_files():
    """
    MANUAL RESET: Creates the clean files needed for the demo.
    """
    ensure_safezone_exists()
    print(f"🔄 SYSTEM RESET: Restoring clean files in {SAFE_ZONE}...")
    
    # Clean up old trap
    if os.path.exists(TRAP_FILE):
        try: os.remove(TRAP_FILE)
        except: pass

    # The Standard File Set
    files = {
        "financial_records.txt": "Account: 123456789\nBalance: $1,000,000\n" * 50, 
        "backend_code.py": "def connect_db():\n    return True\n" * 50,       
        "project_notes.md": "# Q1 Goals\n- Increase revenue\n- Fix bugs\n" * 50, 
        "family_photo.jpg": b"\xFF\xD8\xFF\xE0" + (b"\x00" * 1000), 
        "config.sys": "SYSTEM_BOOT_LOADER=1" 
    }
    
    for name, content in files.items():
        path = os.path.join(SAFE_ZONE, name)
        mode = "wb" if isinstance(content, bytes) else "w"
        with open(path, mode) as f:
            f.write(content)
    
    if os.path.exists("malware.pid"):
        try: os.remove("malware.pid")
        except: pass
        
    print("✅ SafeZone Restored.")

def safe_activity():
    print("🟢 MODE 1: SAFE ACTIVITY (User Working)...")
    if not os.path.exists(SAFE_ZONE):
        print("⚠ ERROR: SafeZone missing! Run '0' first.")
        return

    print(" -> Writing normal log files...")
    for i in range(5):
        with open(os.path.join(SAFE_ZONE, "app_log.txt"), "a") as f:
            f.write(f"Log entry {i}: System normal at {time.time()}\n")
        time.sleep(0.5)
        print(f" -> Log Update {i+1}/5")

def full_encryption_attack():
    print("💀 MODE 2: MASS ENCRYPTION (LockBit Style)...")
    
    # Only target existing files
    if not os.path.exists(SAFE_ZONE): return
    files = [f for f in os.listdir(SAFE_ZONE) if f != "config.sys" and f != "malware.pid"]
    
    if not files:
        print("⚠ No files found to encrypt. Run '0' to Reset first.")
        return

    for fname in files:
        fpath = os.path.join(SAFE_ZONE, fname)
        if os.path.isfile(fpath):
            print(f" -> Encrypting: {fname}")
            size = os.path.getsize(fpath)
            with open(fpath, "wb") as f:
                f.write(os.urandom(max(1024, size))) 
            time.sleep(0.2) 

def header_corruption_attack():
    print("🧬 MODE 3: ZERO-DAY MUTATION (Header Destroy)...")
    
    if not os.path.exists(SAFE_ZONE): return
    files = [f for f in os.listdir(SAFE_ZONE) if f.endswith(".jpg")]
    
    if not files:
        print("⚠ No JPGs found. Run '0' to Reset first.")
        return

    for fname in files:
        fpath = os.path.join(SAFE_ZONE, fname)
        print(f" -> Corrupting DNA: {fname}")
        with open(fpath, "wb") as f:
            f.write(b"\x00\x00\x00\x00" + os.urandom(100)) 
        time.sleep(0.5)

def stealth_honeypot_attack():
    print("🥷 MODE 4: STEALTH/WORM (Hunting for System Files)...")
    
    if not os.path.exists(SAFE_ZONE):
        print("⚠ SafeZone missing. Run '0' first.")
        return

    print(" -> Scanning directory for system configs...")
    time.sleep(0.5) 
    
    print(f" -> ⚡ INJECTING ROOTKIT: {TRAP_FILE}")
    with open(TRAP_FILE, "wb") as f:
        f.write(b"MALICIOUS_PAYLOAD_INJECTED")
            
    time.sleep(1.0)
    print(" -> Attempting to spread to other files...")

def main():
    # Save PID for the Assassin
    with open("malware.pid", "w") as f:
        f.write(str(os.getpid()))

    while True:
        print("\n--- 🛡️ AEGIS SIMULATION CONTROL 🛡️ ---")
        print(f"TARGET: {SAFE_ZONE}")
        print("0. Reset SafeZone (Restore Clean Files)")
        print("1. Safe Activity (Green Graphs)")
        print("2. Mass Encryption (Entropy Attack)")
        print("3. Header Corruption (Heuristic Attack)")
        print("4. Stealth Attack (Honeypot Trap)")
        print("Q. Quit")
        
        choice = input("\nSelect Command: ").lower()

        try:
            if choice == '0':
                reset_files()
            elif choice == '1':
                safe_activity()
            elif choice == '2':
                full_encryption_attack()
                break 
            elif choice == '3':
                header_corruption_attack()
                break
            elif choice == '4':
                stealth_honeypot_attack()
                break
            elif choice == 'q':
                break
            else:
                print("Invalid selection.")
                
        except KeyboardInterrupt:
            print("\n🛑 Simulation Stopped.")
            break
        except Exception as e:
            print(f"⚠ Error: {e}")

if __name__ == "__main__":
    main()