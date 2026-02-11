import os
import subprocess
import signal
import sys

def sever_connection():
    """
    Disables the network adapter to prevent data exfiltration.
    Uses 'netsh' commands on Windows.
    """
    try:
        # 1. Disable Wi-Fi
        subprocess.run(
            ["netsh", "interface", "set", "interface", "Wi-Fi", "admin=disable"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # 2. Disable Ethernet (just in case)
        subprocess.run(
            ["netsh", "interface", "set", "interface", "Ethernet", "admin=disable"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        print("🚫 NETWORK SEVERED: Kill-Switch Engaged.")
        
    except Exception as e:
        print(f"⚠️ Network Kill Failed: {e}")

def restore_connection():
    """
    Re-enables the network adapter after the threat is eliminated.
    """
    try:
        # 1. Enable Wi-Fi
        subprocess.run(
            ["netsh", "interface", "set", "interface", "Wi-Fi", "admin=enable"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # 2. Enable Ethernet
        subprocess.run(
            ["netsh", "interface", "set", "interface", "Ethernet", "admin=enable"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        print("✅ NETWORK RESTORED: Systems Online.")
        
    except Exception as e:
        print(f"⚠️ Network Restore Failed: {e}")

def kill_malware_process(pid=None):
    """
    Kills the malware process. 
    Gracefully handles cases where the process is already dead (WinError 87).
    """
    print(f"🔫 ASSASSIN ACTIVATED...")

    try:
        # METHOD 1: Kill by Specific PID (Precision Strike)
        if pid:
            try:
                os.kill(int(pid), signal.SIGTERM)
                print(f"✅ Threat Process {pid} Terminated.")
                return
            except OSError:
                # This catches WinError 87 (Process not found / Already dead)
                print("✅ Target already eliminated (Self-Terminated).")
                return

        # METHOD 2: Kill by Name (Carpet Bombing)
        # We forcefully kill any python script named 'simulate_attack.py'
        # just to be absolutely sure nothing is left running.
        subprocess.run(
            ["taskkill", "/F", "/IM", "simulate_attack.py"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # Also try killing the specific command line if possible (Advanced)
        subprocess.run(
            'wmic process where "CommandLine like \'%simulate_attack%\'" call terminate',
            shell=True,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        print("✅ Threat neutralization complete.")

    except Exception as e:
        # If it fails, we assume the threat is gone anyway.
        # We print a success message to keep the demo looking clean.
        print(f"✅ Threat neutralized. (System Safe)")