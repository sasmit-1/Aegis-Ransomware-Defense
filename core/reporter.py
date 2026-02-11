import os
import datetime
from groq import Groq

# --- CONFIGURATION ---
# (Ensure your key is set here or via os.getenv)
# API_KEY = os.getenv("GROQ_API_KEY") 
API_KEY = "INSERT your API key HERE :)" 

def generate_forensic_report(stats):
    """
    Sends attack statistics to Groq AI to generate a professional forensic report.
    Forces HTML formatting for the Dashboard UI.
    """
    try:
        client = Groq(api_key=API_KEY)
        
        # 1. Get Real-Time Timestamp
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. Construct the Prompt with HTML Instructions
        # We explicitly tell Llama to use <b> for bold and <br> for line breaks.
        system_prompt = f"""
        You are a Cybersecurity Forensic Analyst for AEGIS Defense Systems.
        
        DATA:
        - THREAT VECTOR: {stats.get('vector')}
        - DETECTED ENTROPY: {stats.get('entropy_avg')} (Normal < 5.0)
        - PEAK I/O RATE: {stats.get('io_peak')} ops/sec
        - TIME OF INCIDENT: {current_time}
        
        CRITICAL INSTRUCTION: 
        Return the response using HTML tags for formatting. 
        Do NOT use Markdown (like **bold**). Use <b> for bold and <br> for new lines.
        
        REQUIRED OUTPUT FORMAT:
        <b>INCIDENT SUMMARY:</b><br>
        [One sentence describing the attack type and time]<br><br>
        
        <b>TECHNICAL ANALYSIS:</b><br>
        [Explain why Entropy {stats.get('entropy_avg')} confirms malicious encryption. Mention the I/O spike.]<br><br>
        
        <b>COUNTERMEASURES TAKEN:</b><br>
        Threat process terminated. Network isolation protocols engaged. System snapshot restored.
        """

        # 3. Call the AI
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                }
            ],
            # Use Llama 3.3 for the best results, or 3.1-70b if 3.3 is unavailable
            model="llama-3.3-70b-versatile",
            temperature=0.3, # Lower temp keeps the formatting strict
            max_tokens=1024, 
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        # Fallback Logic (Returns HTML error message)
        return f"<b>⚠ UPLINK ERROR:</b><br>Could not reach Neural Net.<br><i>Error: {str(e)}</i>"