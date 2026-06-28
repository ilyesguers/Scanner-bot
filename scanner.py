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
    try:
        g = Github(token)
        # التحقق من معدل الاستهلاك قبل البدء
        rate_limit = g.get_rate_limit().search
        print(f"[*] معدل طلبات البحث المتبقي: {rate_limit.remaining}")
        if rate_limit.remaining == 0:
            print("[!] تم استهلاك كامل الطلبات، يرجى الانتظار...")
            return []
    except Exception as e:
        print(f"[!] خطأ في الاتصال بـ GitHub: {e}")
        return []

    found_tokens = []
    # استخدام تنسيق التاريخ YYYY-MM-DD لتجنب أخطاء التوقيت الدقيق
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    queries = [
        f'bot_token pushed:>{today}',
        f'telebot pushed:>{today}',
        f'telegram_token pushed:>{today}'
    ]
    
    for query in queries:
        print(f"[>] جاري تنفيذ استعلام البحث: {query}")
        try:
            results = g.search_code(query=query, sort='indexed', order='desc')
            
            # التحقق من وجود نتائج أولاً
            total_count = results.totalCount
            print(f"[*] تم العثور على {total_count} ملف مطابق.")
            
            if total_count > 0:
                found_count = 0
                # التكرار عبر النتائج بأمان
                for i in range(min(total_count, 30)): 
                    try:
                        file = results[i]
                        content = file.decoded_content.decode('utf-8')
                        matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                        
                        for token in matches:
                            if token not in found_tokens:
                                found_tokens.append(token)
                                found_count += 1
                    except Exception:
                        continue
                print(f"[+] تم استخراج {found_count} توكن جديد من هذا الاستعلام.")
            
        except Exception as e:
            print(f"[!] خطأ أثناء معالجة الاستعلام {query}: {e}")
            
    print(f"[*] انتهت عملية المسح. إجمالي التوكنات الجديدة التي تم رصدها: {len(found_tokens)}")
    return found_tokens
