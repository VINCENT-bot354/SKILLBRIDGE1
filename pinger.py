import threading, time, requests
from flask import Flask

app = Flask(__name__)

# URL of the other site
PINGER_URL = "https://254kenyasafaris.africa/health"

def ping_other_site():
    while True:
        try:
            r = requests.get(PINGER_URL, timeout=10)
            print(f"Pinged 254 Kenya Safaris -> {r.status_code}")
        except Exception as e:
            print(f"Error pinging 254 Kenya Safaris: {e}")
        time.sleep(660)  # every 11 minutes

# Start background thread
threading.Thread(target=ping_other_site, daemon=True).start()

@app.route("/health")
def health():
    return "OK from SkillBridge"
