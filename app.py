import sys
import os
import threading
import time
from flask import Flask, render_template, jsonify, request

# --- PROJECT SETUP ---
sys.path.append(os.getcwd())

from sensor.monitor import start_monitoring
from sensor.ai_brain import predict_threat
from core.recovery import ShadowVault       
from core.network_kill import sever_connection, restore_connection, kill_malware_process
from core.reporter import generate_forensic_report

app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAFE_ZONE_PATH = os.path.join(BASE_DIR, "SafeZone")

vault = ShadowVault(SAFE_ZONE_PATH)

# --- GLOBAL STATE ---
last_rollback_time = 0
last_event_time = time.time()
network_online = True  

# History for Graphs
history_entropy = [0] * 60
history_io = [0] * 60

system_status = {
    "status": "SECURE",
    "message": "System Protected. AI Neural Net Active.",
    "entropy": 0.0,
    "rate": 0,
    "ai_conf": 0.0,
    "attack_vector": "None",
    "ai_score_breakdown": {
        "heuristics": 10,
        "entropy": 0,
        "behavior": 0
    }
}

def start_aegis_backend():
    global system_status, last_rollback_time, network_online, history_entropy, history_io, last_event_time
    
    def update_brain(data_packet):
        global system_status, last_rollback_time, network_online, last_event_time

        last_event_time = time.time()

        # COOLDOWN (Don't process packets immediately after a restore)
        if time.time() - last_rollback_time < 3:
            return 

        try:
            parts = data_packet.split('|')
            rate = int(parts[0].split(':')[1])
            entropy = float(parts[1].split(':')[1])
            trap = int(parts[2].split(':')[1])
            bad_header = int(parts[3].split(':')[1])
            filepath = data_packet.split('PATH:')[1].strip()

            # UPDATE HISTORY (Always update graph data)
            history_entropy.pop(0)
            history_entropy.append(entropy)
            history_io.pop(0)
            history_io.append(rate)

            system_status["rate"] = rate
            system_status["entropy"] = entropy
            
            # --- SCORING LOGIC ---
            score_heuristics = 10 
            score_entropy = int(entropy * 10)
            score_behavior = 0

            is_high_entropy = entropy > 7.0
            filename = os.path.basename(filepath)
            _, ext = os.path.splitext(filename)
            ext = ext.lower().strip() 
            low_entropy_extensions = ['.txt', '.py', '.c', '.cpp', '.java', '.html', '.css', '.js', '.md']

            confidence = 0.0
            status = "SECURE"
            msg = "System Protected."
            trigger_kill = False
            vector = "None"

            # --- THREAT DETECTION HIERARCHY ---
            
            # 1. HONEYPOT (Highest Priority)
            if trap == 1:
                confidence = 100.0
                msg = "HONEYPOT TRIGGERED!"
                status = "DANGER"
                vector = "Honeypot Trap (config.sys)"
                trigger_kill = True
                score_behavior = 99 # Max Danger

            # 2. HEADER CORRUPTION
            elif bad_header == 1:
                confidence = 95.0
                msg = "FILE CORRUPTION (Header Mismatch)"
                status = "DANGER"
                vector = "Magic Byte Corruption (Zero-Day)"
                trigger_kill = True
                score_heuristics = 95

            # 3. HIGH ENTROPY (Ransomware)
            elif ext in low_entropy_extensions and is_high_entropy:
                confidence = 99.0
                msg = f"ABNORMAL ENTROPY SPIKE ({ext})"
                status = "DANGER"
                vector = "High Entropy Anomaly (Stealth)"
                trigger_kill = True 
                score_entropy = 99 

            # 4. BENIGN HIGH ENTROPY (Zip files, etc)
            elif ext not in low_entropy_extensions and is_high_entropy and bad_header == 0:
                confidence = 10.0
                msg = "Verified Compressed File (Safe)"
                status = "SECURE"
                score_entropy = 30 
            
            # 5. HIGH I/O
            elif rate > 50: 
                confidence = 40.0
                msg = "High System Activity..."
                status = "WARNING"
                score_behavior = 50
            
            # UPDATE SCORE BREAKDOWN (Always)
            system_status["ai_score_breakdown"] = {
                "heuristics": score_heuristics,
                "entropy": score_entropy, 
                "behavior": score_behavior
            }

            # --- PRIORITY LOCK ---
            # If we are already in DANGER from a Honeypot, do NOT downgrade to a lesser threat
            current_vector = system_status.get("attack_vector", "None")
            if "Honeypot" in current_vector and status != "DANGER":
                 return

            # APPLY STATUS
            if status == "DANGER":
                system_status["ai_conf"] = round(confidence, 1)
                system_status["status"] = status
                system_status["message"] = msg
                system_status["attack_vector"] = vector

                if trigger_kill and network_online:
                    print(f"⚡ CONTAINMENT ACTIVATED: {vector}")
                    sever_connection() 
                    network_online = False 
            
            elif system_status["status"] != "DANGER":
                # Only update Safe/Warning if we aren't currently dying
                system_status["ai_conf"] = round(confidence, 1)
                system_status["status"] = status
                system_status["message"] = msg

        except Exception as e:
            print(f"Error processing packet: {e}")

    if not os.path.exists(SAFE_ZONE_PATH): 
        os.mkdir(SAFE_ZONE_PATH)
    
    print(f"AEGIS MONITORING: {SAFE_ZONE_PATH}")
    start_monitoring(SAFE_ZONE_PATH, update_brain)
    
    # --- IDLE DECAY LOOP ---
    while True: 
        time.sleep(1)
        # Only decay graphs if we are NOT in DANGER mode.
        if system_status["status"] != "DANGER" and (time.time() - last_event_time > 1.0):
            history_entropy.pop(0)
            history_entropy.append(0.0)
            history_io.pop(0)
            history_io.append(0)
            system_status["entropy"] = 0.0
            system_status["rate"] = 0
            system_status["ai_score_breakdown"] = {"heuristics": 10, "entropy": 0, "behavior": 0}

# --- FLASK ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/status')
def get_status(): 
    response = system_status.copy()
    response["graph_entropy"] = history_entropy
    response["graph_io"] = history_io
    return jsonify(response)

@app.route('/api/eliminate', methods=['POST'])
def eliminate_threat():
    global system_status, network_online, last_rollback_time
    
    kill_malware_process()
    restore_connection()
    network_online = True 
    last_rollback_time = time.time()
    
    if vault.restore_snapshot():
        system_status["status"] = "SECURE"
        system_status["message"] = "Threat Eliminated. System Restored."
        system_status["ai_conf"] = 0.0
        return jsonify({"success": True, "message": "System Sanitized & Restored."})
    return jsonify({"success": False, "message": "Error during restoration."})

@app.route('/api/report', methods=['GET'])
def get_ai_report():
    stats = {
        "vector": system_status.get("attack_vector", "Unknown"),
        "entropy_avg": max(history_entropy) if history_entropy else 0, 
        "io_peak": max(history_io) if history_io else 0
    }
    report_text = generate_forensic_report(stats)
    return jsonify({"report": report_text.replace("\n", "<br>")})

@app.route('/api/reset', methods=['POST'])
def reset_system():
    global system_status, network_online
    
    system_status["status"] = "SECURE"
    system_status["message"] = "System Reset."
    system_status["ai_conf"] = 0.0
    system_status["attack_vector"] = "None"
    system_status["entropy"] = 0.0
    
    restore_connection()
    network_online = True 
    return jsonify({"success": True})

if __name__ == '__main__':
    print("--- AEGIS STARTUP SEQUENCE ---")
    if not os.path.exists(SAFE_ZONE_PATH): os.mkdir(SAFE_ZONE_PATH)
    vault.create_snapshot() 
    
    threading.Thread(target=start_aegis_backend, daemon=True).start()
    app.run(debug=True, use_reloader=False)