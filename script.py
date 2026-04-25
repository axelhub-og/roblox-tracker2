import requests
import os
import time
from datetime import datetime, timezone # เพิ่ม timezone เข้ามา

# --- ตั้งค่า Webhook ของคุณตรงนี้ ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1497704650743222385/c5dBNfiIVZZRe-XxFOcyMjAaUEImmx-vL1ogMj1-Pyt8Ldb_eYC9y0nMtap9TcNZnZ91"
HEADERS = {"User-Agent": "WEAO-3PService"}

def get_unix_timestamp(date_str):
    """แปลงวันที่จาก API เป็น Unix Timestamp โดยระบุว่าเป็นเวลา UTC"""
    try:
        # ตัดคำว่า UTC ออกเพื่อให้ Python อ่านง่ายขึ้น
        clean_date = date_str.replace(" UTC", "")
        # อ่านข้อความวันเวลา
        dt = datetime.strptime(clean_date, "%m/%d/%Y, %I:%M:%S %p")
        
        # *** สำคัญมาก: ต้องบอก Python ว่าเลขนี้คือเวลามาตรฐาน (UTC) นะ ***
        dt = dt.replace(tzinfo=timezone.utc)
        
        # แปลงเป็นเลข Unix (เลขชุดนี้ Discord จะเอาไปคำนวณเป็นเวลาเครื่องคนดูให้เอง)
        return int(dt.timestamp())
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None

def check_version(name, api_url, history_file, color):
    try:
        response = requests.get(api_url, headers=HEADERS)
        if response.status_code != 200:
            return

        data = response.json()
        current_hash = data.get("Windows", "")
        raw_date = data.get("WindowsDate", "N/A")
        
        # แปลงเป็นเลข Timestamp
        timestamp = get_unix_timestamp(raw_date)

        # อ่านประวัติเก่าเพื่อเช็คอัปเดต
        last_hash = ""
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                last_hash = f.read().strip()

        if current_hash and current_hash != last_hash:
            # สร้างข้อความเวลาแบบ Discord Dynamic Timestamp
            # <t:12345678:F> = วันและเวลาเต็ม
            # <t:12345678:R> = (กี่นาทีที่แล้ว)
            discord_time = f"<t:{timestamp}:F> (<t:{timestamp}:R>)" if timestamp else raw_date

            payload = {
                "content": "@everyone" if name == "LIVE" else "",
                "embeds": [{
                    "title": "Roblox Update Detected!",
                    "description": f"This is a **{name.lower()}** update, Cosmic is **patched**.",
                    "color": color,
                    "fields": [
                        {"name": "Platform", "value": "Windows", "inline": False},
                        {"name": "Version Hash", "value": f"`{current_hash}`", "inline": False},
                        {"name": "Date", "value": discord_time, "inline": False}
                    ],
                    "footer": {"text": "Axel Hub Auto-Tracker"}
                }]
            }
            
            requests.post(WEBHOOK_URL, json=payload)
            
            # บันทึกประวัติ
            with open(history_file, "w") as f:
                f.write(current_hash)
        else:
            print(f"[{name}] No changes.")

    except Exception as e:
        print(f"[{name}] Error: {e}")

if __name__ == "__main__":
    # เช็คทั้ง Live และ Future
    check_version("LIVE", "https://weao.xyz/api/versions/current", "last_hash.txt", 10181046)
    check_version("FUTURE", "https://weao.xyz/api/versions/future", "last_future_hash.txt", 15277667)
