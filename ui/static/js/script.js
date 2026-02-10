function updateDashboard() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            // --- NEW: NETWORK KILL SWITCH VISUAL ---
            // If status is DANGER, we override the text to show the dramatic network cut
            const statusText = document.getElementById('status-text');
            if (data.status === "DANGER") {
                statusText.innerText = "NETWORK SEVERED";
                statusText.style.color = "red";
                statusText.style.animation = "blink 1s infinite"; // Optional: Make it blink
            } else {
                statusText.innerText = data.status;
                statusText.style.color = ""; // Reset color
                statusText.style.animation = ""; // Reset animation
            }
            // ---------------------------------------

            document.getElementById('entropy-val').innerText = data.entropy.toFixed(2);
            document.getElementById('rate-val').innerText = data.rate;
            document.getElementById('ai-val').innerText = data.ai_conf + "%";

            // Update Bars
            document.getElementById('entropy-bar').style.width = (data.entropy * 10) + "%";
            document.getElementById('rate-bar').style.width = Math.min(data.rate, 100) + "%";
            document.getElementById('ai-bar').style.width = data.ai_conf + "%";

            // Update Color Ring
            const ring = document.getElementById('big-status');
            ring.className = "status-ring " + data.status.toLowerCase(); // secure, warning, danger
        })
        .catch(error => console.error('Error:', error));
}

function resetSystem() {
    fetch('/api/reset', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("SYSTEM REBOOTED. Memory Cleared & Network Restored.");
                updateDashboard();
            }
        });
}

function rollbackSystem() {
    console.log("Attempting Rollback...");
    fetch('/api/rollback', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                alert("✅ TIME TRAVEL SUCCESSFUL\nFiles Restored & Network Reconnected.");
                updateDashboard();
            } else {
                alert("❌ ROLLBACK FAILED: " + (data.error || "Unknown Error"));
            }
        })
        .catch(err => alert("Server Error: Check Terminal"));
}

// Auto-refresh every 1 second
setInterval(updateDashboard, 1000);