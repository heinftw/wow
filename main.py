import sys
import os
import time
import string
import random
import threading
from flask import Flask, render_template_string, jsonify, request
import requests
from requests.adapters import HTTPAdapter

app = Flask(__name__)

class TikTokSniper:
    def __init__(self):
        self.checking = False
        self.available = 0
        self.unavailable = 0
        self.counter = 0
        self.rps = 0
        self.last_counter = 0
        self.threads = []
        self.proxies = []  
        self.logs = []
        self.log_counter = 0  # Unique ID for incremental logs
        self.stop_event = threading.Event()
        
        # Hardcoded Telegram Credentials
        self.tg_token = "8483317474:AAHUVYutHsKh4OK6LaoEGKETYo1lyAb-EJ4"
        self.tg_chat_id = "6200686509"
        
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "*/*",
            "connection": "keep-alive"
        }
        
        self.session = requests.Session()
        adapter = HTTPAdapter(pool_connections=1000, pool_maxsize=1000, max_retries=0)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

    def get_username(self, mode):
        if mode == "4l":
            return "".join(random.choices(string.ascii_lowercase, k=4))
        else:
            letters = string.ascii_lowercase
            digits = string.digits
            all_chars = letters + digits
            res = [random.choice(digits)] + random.choices(all_chars, k=3)
            random.shuffle(res)
            return "".join(res)

    def add_log(self, status, message, color):
        self.log_counter += 1
        self.logs.append({
            "id": self.log_counter,
            "time": time.strftime("%H:%M:%S"),
            "status": status,
            "message": message,
            "color": color
        })
        # Keep internal log cache small to save memory
        if len(self.logs) > 300:
            self.logs.pop(0)

    def send_telegram(self, username):
        try:
            url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
            text = (
                f"🎯 *Hit Found!*\n\n"
                f"👤 *Username:* `@{username}`\n\n"
                f"_Developed by @pm7. | .gg/3char_"
            )
            self.session.post(url, json={
                "chat_id": self.tg_chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }, timeout=5)
        except:
            pass

    def check_loop(self, mode):
        while not self.stop_event.is_set():
            username = self.get_username(mode)
            proxy_str = random.choice(self.proxies) if self.proxies else None
            proxy = {"http": f"http://{proxy_str}", "https": f"http://{proxy_str}"} if proxy_str else None

            try:
                # Dropped timeout to 2 seconds to drop slow proxies instantly and boost speed
                r = self.session.get(
                    f"https://www.tiktok.com/@{username}", 
                    headers=self.headers, 
                    proxies=proxy, 
                    timeout=2, 
                    allow_redirects=False
                )
                
                if r.status_code == 404:
                    self.available += 1
                    self.add_log("Available", f"@{username}", "#00FF66")
                    self.send_telegram(username)
                else:
                    self.unavailable += 1
                    self.add_log("Taken", f"@{username}", "#FF3B30")
                
                self.counter += 1
            except Exception as e:
                err_msg = str(e)
                if "timeout" in err_msg.lower():
                    self.add_log("Proxy Timeout", f"Proxy {proxy_str} timed out.", "#FF9F0A")
                else:
                    self.add_log("Proxy Error", f"Bad Connection: {proxy_str}", "#FF3B30")
                # Drop delay to keep threads cycling fast
                time.sleep(0.05)

    def rps_calculator(self):
        while not self.stop_event.is_set():
            self.last_counter = self.counter
            time.sleep(1)
            self.rps = self.counter - self.last_counter

sniper = TikTokSniper()

# Highly optimized HTML with Smooth Streaming JS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Sniper Cloud Dashboard</title>
    <style>
        :root {
            --bg-color: #0b0c10;
            --container-bg: #1f2833;
            --accent-neon: #45f3ff;
            --text-main: #c5c6c7;
            --hit-color: #00FF66;
            --fail-color: #FF3B30;
        }

        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { color: var(--accent-neon); margin: 0; font-size: 2.2rem; text-shadow: 0 0 10px rgba(69, 243, 255, 0.4); }
        .header p { margin: 5px 0 0 0; opacity: 0.7; font-size: 0.9rem; }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            width: 100%;
            max-width: 900px;
            margin-bottom: 20px;
        }

        .card {
            background-color: var(--container-bg);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .card h3 { margin: 0 0 5px 0; font-size: 0.8rem; text-transform: uppercase; opacity: 0.8; }
        .card p { margin: 0; font-size: 1.8rem; font-weight: bold; color: #fff; }
        .card.available p { color: var(--hit-color); }
        .card.rps p { color: var(--accent-neon); }

        .layout-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            width: 100%;
            max-width: 900px;
        }
        @media (min-width: 768px) {
            .layout-grid { grid-template-columns: 1fr 1fr; }
        }

        .section-box {
            background-color: var(--container-bg);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .section-box h3 { margin: 0; color: var(--accent-neon); border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }

        .control-group { display: flex; flex-direction: column; gap: 5px; }
        label { font-size: 0.85rem; font-weight: bold; }
        select, input, textarea {
            background-color: var(--bg-color);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            padding: 10px;
            border-radius: 4px;
            outline: none;
            font-family: inherit;
        }
        select:focus, input:focus, textarea:focus { border-color: var(--accent-neon); }

        .btn {
            background-color: var(--accent-neon);
            color: #000;
            border: none;
            padding: 12px;
            font-size: 1rem;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .btn:hover { transform: translateY(-1px); box-shadow: 0 0 15px rgba(69, 243, 255, 0.5); }
        .btn.stop { background-color: var(--fail-color); color: #fff; }

        .console-logs {
            height: 250px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 6px;
            background-color: #050508;
            padding: 10px;
            border-radius: 4px;
        }
        .log-item { display: flex; gap: 10px; }
        .log-time { color: #666; }
    </style>
</head>
<body>

    <div class="header">
        <h1>TIKTOK SNIPER (CLOUD HOSTED)</h1>
        <p>100% Remote | Running in Background</p>
    </div>

    <div class="dashboard">
        <div class="card available">
            <h3>Hits Saved</h3>
            <p id="stat-avail">0</p>
        </div>
        <div class="card">
            <h3>Total Checked</h3>
            <p id="stat-checked">0</p>
        </div>
        <div class="card rps">
            <h3>Speed (RPS)</h3>
            <p id="stat-rps">0</p>
        </div>
        <div class="card">
            <h3>Active Proxies</h3>
            <p id="stat-proxies">0</p>
        </div>
    </div>

    <div class="layout-grid">
        <div class="section-box">
            <h3>Controls</h3>
            
            <div class="control-group">
                <label for="mode">Mode:</label>
                <select id="mode">
                    <option value="4l">4L (aaaa-zzzz)</option>
                    <option value="4c">4C (a1bc-z67b)</option>
                </select>
            </div>

            <div class="control-group">
                <label for="threads">Threads:</label>
                <input type="number" id="threads" value="20" min="1" max="500">
            </div>

            <div class="control-group">
                <label for="proxies">Proxies (Format: ip:port or user:pass@ip:port):</label>
                <textarea id="proxies" placeholder="Paste proxies here... (one per line)" style="height: 120px; resize: none;"></textarea>
            </div>

            <button id="action-btn" class="btn" onclick="toggleSniper()">START SNIPING</button>
            <button onclick="testTelegram()" class="btn" style="background-color: #333; color: #fff;">Test Telegram Connection</button>
        </div>

        <div class="section-box">
            <h3>Live Activity Logs</h3>
            <div class="console-logs" id="logs-box">
                <div style="color: #666;">System ready. Paste proxies, configure, and hit start.</div>
            </div>
            <button onclick="copyLogs()" class="btn" style="background-color: #555; color: #fff; padding: 8px;">Copy Logs</button>
        </div>
    </div>

    <script>
        let running = false;
        let lastLogId = 0; // Tracks the last log we loaded to stream incrementally

        function updateStats() {
            fetch('/stats?last_id=' + lastLogId)
                .then(res => res.json())
                .then(data => {
                    // Update stats counters
                    document.getElementById('stat-avail').innerText = data.available;
                    document.getElementById('stat-checked').innerText = data.counter;
                    document.getElementById('stat-rps').innerText = data.rps;
                    document.getElementById('stat-proxies').innerText = data.proxies_count;

                    // Sync the button state directly with the backend status to fix the UI freeze bug!
                    const btn = document.getElementById('action-btn');
                    if (data.checking) {
                        running = true;
                        btn.innerText = "STOP SNIPER";
                        btn.className = "btn stop";
                    } else {
                        running = false;
                        btn.innerText = "START SNIPING";
                        btn.className = "btn";
                    }

                    // Dynamically stream logs
                    const logsBox = document.getElementById('logs-box');
                    if (data.logs.length > 0) {
                        // If logs box currently contains the system boot text, clear it
                        if (logsBox.innerText.includes("System ready")) {
                            logsBox.innerHTML = '';
                        }

                        data.logs.forEach(log => {
                            const item = document.createElement('div');
                            item.className = 'log-item';
                            item.innerHTML = '<span class="log-time">[' + log.time + ']</span> ' +
                                             '<span style="color: ' + log.color + '">[' + log.status + ']</span> ' +
                                             '<span>' + log.message + '</span>';
                            logsBox.appendChild(item);
                            lastLogId = log.id; // Update our tracker to the absolute newest ID
                        });

                        // Prune elements to keep DOM memory incredibly light and lag-free
                        while (logsBox.children.length > 150) {
                            logsBox.removeChild(logsBox.firstChild);
                        }

                        // Instant autoscroll
                        logsBox.scrollTop = logsBox.scrollHeight;
                    }
                });
        }

        // Fast update loop: requests data 4 times a second (250ms) for high-speed live streams!
        setInterval(updateStats, 250);

        function toggleSniper() {
            const btn = document.getElementById('action-btn');
            const mode = document.getElementById('mode').value;
            const threads = document.getElementById('threads').value;
            const proxiesRaw = document.getElementById('proxies').value;

            if (!running) {
                // Instantly update button while the server configures itself in background
                btn.innerText = "STARTING...";
                btn.className = "btn stop";
                
                fetch('/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode: mode, threads: parseInt(threads), proxies: proxiesRaw })
                });
            } else {
                btn.innerText = "STOPPING...";
                btn.className = "btn";
                
                fetch('/stop', { method: 'POST' });
            }
        }

        function testTelegram() {
            fetch('/test-telegram', { method: 'POST' })
                .then(res => res.json())
                .then(data => alert(data.message));
        }

        function copyLogs() {
            const logsBox = document.getElementById('logs-box');
            const textToCopy = logsBox.innerText;
            
            navigator.clipboard.writeText(textToCopy).then(() => {
                alert("Logs copied to clipboard!");
            }).catch(err => {
                alert("Failed to copy logs: " + err);
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/stats', methods=['GET'])
def get_stats():
    # Read the last ID the client saw
    last_id = int(request.args.get('last_id', 0))
    
    # Filter only newer logs
    new_logs = [log for log in sniper.logs if log['id'] > last_id]
    
    return jsonify({
        "checking": sniper.checking,
        "available": sniper.available,
        "counter": sniper.counter,
        "rps": sniper.rps,
        "proxies_count": len(sniper.proxies),
        "logs": new_logs # Send ONLY new logs
    })

@app.route('/start', methods=['POST'])
def start_sniper():
    if sniper.checking:
        return jsonify({"status": "already running"})
    
    data = request.json
    mode = data.get("mode", "4l")
    threads_count = data.get("threads", 10)
    proxies_raw = data.get("proxies", "")
    
    # Clean up proxies input instantly
    raw_list = [line.strip() for line in proxies_raw.split("\n") if line.strip()]
    sniper.proxies = []
    for line in raw_list:
        cleaned = line
        for prefix in ["http://", "https://"]:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):]
        if cleaned:
            sniper.proxies.append(cleaned)
    
    sniper.checking = True
    sniper.stop_event.clear()
    
    # Run calculating thread
    threading.Thread(target=sniper.rps_calculator, daemon=True).start()
    
    # Spin up threads inside a single background manager to prevent HTTP blocking!
    def thread_launcher():
        for _ in range(threads_count):
            if sniper.stop_event.is_set():
                break
            t = threading.Thread(target=sniper.check_loop, args=(mode,), daemon=True)
            t.start()
            sniper.threads.append(t)
            
    threading.Thread(target=thread_launcher, daemon=True).start()
    
    sniper.add_log("System", f"Started remote sniper with {threads_count} threads.", "#45f3ff")
    return jsonify({"status": "started"})

@app.route('/stop', methods=['POST'])
def stop_sniper():
    sniper.checking = False
    sniper.stop_event.set()
    sniper.threads.clear()
    sniper.add_log("System", "Sniper process stopped.", "#FF3B30")
    return jsonify({"status": "stopped"})

@app.route('/test-telegram', methods=['POST'])
def test_telegram_route():
    try:
        url = f"https://api.telegram.org/bot{sniper.tg_token}/sendMessage"
        text = (
            f"🔔 *Telegram Bot Connection Test*\n\n"
            f"✅ Your cloud-hosted TikTok Sniper dashboard is online!\n\n"
            f"_Developed by @pm7. | .gg/3char_"
        )
        r = sniper.session.post(url, json={
            "chat_id": sniper.tg_chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }, timeout=5)
        
        if r.status_code == 200:
            return jsonify({"message": "Success! Test message sent to your Telegram bot."})
        else:
            return jsonify({"message": f"Error: Code {r.status_code}."})
    except Exception as e:
        return jsonify({"message": f"Connection failed: {e}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host="0.0.0.0", debug=False)
