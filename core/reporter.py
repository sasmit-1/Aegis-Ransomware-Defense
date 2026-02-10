import os
from groq import Groq
from core.network_kill import restore_connection
import time

API_KEY = "insert API key here :)"  

def generate_forensic_report(stats):
    print("📝 ESTABLISHING SECURE UPLINK TO GROQ CLOUD...")
    
    # 1. Restore Internet so we can talk to the AI
    restore_connection()
    
    # 2. Handshake Wait
    time.sleep(2) 

    try:
        client = Groq(api_key=API_KEY)
        
        # New Shorter, Punchy Prompt
        prompt = f"""
        ACT AS: A Military-Grade Cybersecurity Analyst (Aegis System).
        TASK: Write a SHORT, punchy Incident Report (Max 150 words).
        
        DATA:
        - Detected Vector: {stats.get('vector')}
        - Peak Entropy: {stats.get('entropy_avg', 0)} (Normal < 5.0)
        - IO Spike: {stats.get('io_peak', 0)} ops/s
        
        REQUIRED SECTIONS (Use HTML <h3> for headers):
        1. <h3>Threat Identification</h3> (One sentence on what was caught, mention MITRE T-Code if applicable).
        2. <h3>Technical Analysis</h3> (Explain why the entropy or IO spike confirms the attack).
        3. <h3>Countermeasures</h3> (Confirm "Process Terminated" and "Network Severed").
        
        TONE: Clinical, urgent, professional. 
        FORMAT: HTML tags only (<h3>, <p>, <b>). No Markdown.
        """

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"<h3>CONNECTION ERROR</h3><p>Forensic AI Offline: {e}</p>"