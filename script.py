import requests
import os
import time
from datetime import datetime, timezone

# --- ตั้งค่า Webhook ของคุณตรงนี้ ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1497704650743222385/c5dBNfiIVZZRe-XxFOcyMjAaUEImmx-vL1ogMj1-Pyt8Ldb_eYC9y0nMtap9TcNZnZ91"
HEADERS = {"User-Agent": "Axel-Tracker-v2-Independent"}

def get_unix_timestamp(date_str):
    """แปลงวันที่จาก API เป็น Unix Timestamp สำหรับ Discord Dynamic Time"""
    try:
        clean_date = date_str.replace(" UTC", "")
        dt = datetime.strptime(clean_date, "%m/%d/%Y, %I:%M:%S %p")
        # กำหนดว่าเป็นเวลามาตรฐานสากล UTC
        dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None

def check_version(name, api_url, history_file, color):
    """ฟังก์ชันเช็คเวอร์ชัน แยกการทำงานอิสระต่อกัน"""
    try:
        response = requests.get(api_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"[{name}] API Error: {response.status_code}")
            return

        data = response.json()
        current_hash = data.get("Windows", "")
        raw_date = data.get("WindowsDate", "N/A")
        timestamp = get_unix_timestamp(raw_date)

        # อ่านประวัติเก่าจากไฟล์ (แยกไฟล์กันชัดเจน)
        last_hash = ""
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                last_hash = f.read().strip()

        # ถ้า Hash เปลี่ยน ให้ส่งแจ้งเตือนทันที ไม่ต้องรอกัน
        if current_hash and current_hash != last_hash:
            # ระบบ Tag: @everyone เฉพาะ LIVE เท่านั้น
            tag_content = ""
            if name == "LIVE":
                tag_content = "@Updated-roblox ⚠️ **Roblox Current Version Updated!**"
            else:
                tag_content = "📢 **Future Update Detected (Warning)**"

            # เวลาแบบ Discord Dynamic (เช่น วันนี้ เวลา... หรือ 2 นาทีที่แล้ว)
            discord_time = f"<t:{timestamp}:F> (<t:{timestamp}:R>)" if timestamp else f"`{raw_date}`"

            payload = {
                "content": tag_content,
                "embeds": [{
                    "title": f"🚀 Roblox {name} Update Detected!",
                    "description": f"A new version hash was found on the `{name.lower()}` channel.",
                    "color": color,
                    "fields": [
                        {"name": "Platform", "value": "Windows", "inline": True},
                        {"name": "Channel", "value": f"`{name}`", "inline": True},
                        {"name": "Version Hash", "value": f"`{current_hash}`", "inline": False},
                        {"name": "Update Date", "value": discord_time, "inline": False}
                    ],
                    "footer": {"text": "Axel Hub Auto Tracker"}
                }]
            }
            
            # ส่ง Webhook ทันทีที่เจอ
            res = requests.post(WEBHOOK_URL, json=payload)
            if res.status_code in [200, 204]:
                # บันทึกประวัติลงไฟล์ทันที
                with open(history_file, "w") as f:
                    f.write(current_hash)
                print(f"[{name}] Detected change and sent notification!")
            else:
                print(f"[{name}] Webhook error: {res.status_code}")
        else:
            print(f"[{name}] No update (Hash is still {current_hash})")

    except Exception as e:
        print(f"[{name}] Error: {e}")

if __name__ == "__main__":
    # บอทจะทำงานทีละอันต่อเนื่องกัน ไม่ต้องรอกัน
    # 1. เช็ค LIVE (ถ้าเปลี่ยนจะ Tag @everyone)
    check_version("LIVE", "https://weao.xyz/api/versions/current", "last_hash.txt", 10181046)
    
    # 2. เช็ค FUTURE (ถ้าเปลี่ยนจะส่งแจ้งเตือนเงียบๆ ก่อน)
    check_version("FUTURE", "https://weao.xyz/api/versions/future", "last_future_hash.txt", 15277667)
