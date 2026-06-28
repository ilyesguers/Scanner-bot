import re
from github import Github

def search_for_tokens(token):
    g = Github(token)
    
    # قائمة الكلمات المفتاحية الشاملة (لغات متعددة ومصطلحات شائعة)
    keywords = [
        'telegram_token', 'bot_token', 'api_token', 'bot_api',
        'token_telegram', 'telegram_bot', 'token_bot', 'TELEGRAM_BOT_TOKEN',
        'BOT_TOKEN', 'API_KEY', 'tg_token', 'api_telegram'
    ]
    
    found_tokens = []
    
    # البحث في كل كلمة مفتاحية لزيادة نطاق التغطية
    for word in keywords:
        try:
            # البحث عن النمط مع الكلمة المفتاحية
            query = f'"{word}" extension:py'
            result = g.search_code(query=query)
            
            # فحص النتائج
            for content_file in result[:5]: # نأخذ 5 نتائج لكل كلمة مفتاحية
                try:
                    content = content_file.decoded_content.decode('utf-8')
                    # نمط البحث (Regex)
                    tokens = re.findall(r'[0-9]{8,10}:[a-zA-Z0-9_-]{35}', content)
                    found_tokens.extend(tokens)
                except:
                    continue
        except:
            continue
            
    return list(set(found_tokens))
