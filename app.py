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
network_online = True  

# History for Graphs (Max 60 points)
history_entropy = [0] * 60
history_io = [0] * 60

system_status = {
    "status": "SECURE",
    "message": "System Protected. AI Neural Net Active.",
    "entropy": 0.0,
    "rate": 0,
    "ai_conf": 0.0,
    "attack_vector": "None",
    # NEW: Granular Scoring
    "ai_score_breakdown": {
        "heuristics": 10,  # Trust score (10 = Safe)
        "entropy": 0,      # Randomness score
        "behavior": 0      # Activity score
    }
}

def start_aegis_backend():
    global system_status, last_rollback_time, network_online, history_entropy, history_io
    
    def update_brain(data_packet):
        global system_status, last_rollback_time, network_online

        # COOLDOWN
        if time.time() - last_rollback_time < 10:
            system_status.update({"status": "SECURE", "message": "Restoring...", "ai_conf": 0.0})
            return 

        try:
            parts = data_packet.split('|')
            rate = int(parts[0].split(':')[1])
            entropy = float(parts[1].split(':')[1])
            trap = int(parts[2].split(':')[1])
            bad_header = int(parts[3].split(':')[1])
            filepath = data_packet.split('PATH:')[1].strip()

            # UPDATE HISTORY FOR GRAPHS
            history_entropy.pop(0)
            history_entropy.append(entropy)
            history_io.pop(0)
            history_io.append(rate)

            system_status["rate"] = rate
            system_status["entropy"] = entropy
            
            # --- SCORING LOGIC ---
            # Base score (Safe)
            score_heuristics = 10 # Baseline trust
            score_entropy = 0
            score_behavior = 0

            is_high_entropy = entropy > 7.0
            filename = os.path.basename(filepath)
            _, ext = os.path.splitext(filename)
            ext = ext.lower().strip() 
            low_entropy_extensions = ['.txt', '.py', '.c', '.cpp', '.java', '.html', '.css', '.js', '.md']
            
            # Priority Lock
            current_vector = system_status.get("attack_vector", "None")
            if "Honeypot" in current_vector:
                 # Don't overwrite high priority alerts
                 return

            confidence = 0.0
            status = "SECURE"
            msg = "System Protected."
            trigger_kill = False
            vector = "None"

            # 1. TRAP CHECK (Priority 3)
            if trap == 1:
                confidence = 100.0
                msg = "HONEYPOT TRIGGERED!"
                status = "DANGER"
                vector = "Honeypot Trap (config.sys)"
                trigger_kill = True
                score_behavior = 90 # Max bad behavior

            # 2. HEADER CORRUPTION (Priority 2)
            elif bad_header == 1:
                confidence = 95.0
                msg = "FILE CORRUPTION (Header Mismatch)"
                status = "DANGER"
                vector = "Magic Byte Corruption (Zero-Day)"
                trigger_kill = True
                score_heuristics = 95 # High heuristics violation

            # 3. STEALTH CHECK (Priority 1)
            elif ext in low_entropy_extensions and is_high_entropy:
                confidence = 99.0
                msg = f"ABNORMAL ENTROPY SPIKE ({ext})"
                status = "DANGER"
                vector = "High Entropy Anomaly (Stealth)"
                trigger_kill = True 
                score_entropy = 99 # High entropy violation

            # 4. SAFETY FILTER
            elif ext not in low_entropy_extensions and is_high_entropy and bad_header == 0:
                confidence = 10.0
                msg = "Verified Compressed File (Safe)"
                status = "SECURE"
                score_entropy = 30 # Normal high entropy
            
            elif rate > 50: 
                confidence = 40.0
                msg = "High System Activity..."
                status = "WARNING"
                score_behavior = 50
            
            # UPDATE SCORE BREAKDOWN
            system_status["ai_score_breakdown"] = {
                "heuristics": score_heuristics,
                "entropy": int(entropy * 10), # Scale 0-8 to 0-80
                "behavior": score_behavior
            }

            # --- EXECUTION ---
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
                system_status["ai_conf"] = round(confidence, 1)
                system_status["status"] = status
                system_status["message"] = msg

        except Exception as e:
            print(f"Error processing packet: {e}")

    if not os.path.exists(SAFE_ZONE_PATH): 
        os.mkdir(SAFE_ZONE_PATH)
    
    print(f"🛡️  AEGIS MONITORING: {SAFE_ZONE_PATH}")
    start_monitoring(SAFE_ZONE_PATH, update_brain)
    
    while True: time.sleep(1)

# --- FLASK ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/status')
def get_status(): 
    # Add graph data to the status packet
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
        # Do not clear vector yet (for report)
        return jsonify({"success": True, "message": "System Sanitized & Restored."})
    return jsonify({"success": False, "message": "Error during restoration."})

@app.route('/api/report', methods=['GET'])
def get_ai_report():
    stats = {
        "vector": system_status.get("attack_vector", "Unknown"),
        "entropy_avg": sum(history_entropy[-10:]) / 10, # Avg of last 10 ticks
        "io_peak": max(history_io)
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
    restore_connection()
    network_online = True 
    return jsonify({"success": True})

if __name__ == '__main__':
    print("--- 🛡️ AEGIS STARTUP SEQUENCE ---")
    if not os.path.exists(SAFE_ZONE_PATH): os.mkdir(SAFE_ZONE_PATH)
    vault.create_snapshot() 
    
    threading.Thread(target=start_aegis_backend, daemon=True).start()
    app.run(debug=True, use_reloader=False)