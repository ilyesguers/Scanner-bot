import requests

def get_bot_info(token):
    res = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
    return str(res)

def get_bot_messages(token):
    res = requests.get(f"https://api.telegram.org/bot{token}/getUpdates").json()
    # استخراج الرسائل الأخيرة فقط
    messages = res.get('result', [])
    return str(messages[-5:]) if messages else "لا توجد رسائل جديدة."
