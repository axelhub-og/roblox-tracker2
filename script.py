import requests
import os

# --- ตั้งค่า Webhook ของคุณตรงนี้ ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1497704650743222385/c5dBNfiIVZZRe-XxFOcyMjAaUEImmx-vL1ogMj1-Pyt8Ldb_eYC9y0nMtap9TcNZnZ91"
HEADERS = {"User-Agent": "WEAO-3PService"}

def check_version(name, api_url, history_file, color, title_prefix):
    """ฟังก์ชันหลักสำหรับเช็คเวอร์ชัน"""
    try:
        response = requests.get(api_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"[{name}] API Error: {response.status_code}")
            return

        data = response.json()
        current_hash = data.get("Windows", "")
        update_date = data.get("WindowsDate", "N/A")

        # อ่านประวัติเก่า
        last_hash = ""
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                last_hash = f.read().strip()

        # ถ้ามีการอัปเดต
        if current_hash and current_hash != last_hash:
            print(f"[{name}] New version detected!")
            
            payload = {
                "content": "@everyone" if name == "LIVE" else "", # @everyone เฉพาะตัว Live
                "embeds": [{
                    "title": f"🚀 {title_prefix} Update Detected!",
                    "color": color,
                    "fields": [
                        {"name": "Version-Hash", "value": f"`{current_hash}`", "inline": False},
                        {"name": "Update Date", "value": f"`{update_date}`", "inline": True},
                        {"name": "Channel", "value": f"`{name}`", "inline": True}
                    ],
                    "footer": {"text": "Axel Hub Auto-Tracker"}
                }]
            }
            
            requests.post(WEBHOOK_URL, json=payload)
            # บันทึกประวัติใหม่
            with open(history_file, "w") as f:
                f.write(current_hash)
        else:
            print(f"[{name}] No changes.")

    except Exception as e:
        print(f"[{name}] Error: {e}")

if __name__ == "__main__":
    # 1. เช็คตัว Live (ปัจจุบัน)
    check_version("LIVE", "https://weao.xyz/api/versions/current", "last_hash.txt", 2829617, "Roblox Windows")
    
    # 2. เช็คตัว Future (อนาคต)
    check_version("FUTURE", "https://weao.xyz/api/versions/future", "last_future_hash.txt", 16766720, "Upcoming Windows")
