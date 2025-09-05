import os
from dotenv import load_dotenv

load_dotenv()

CRAWL_DELAY_SEC = float(os.getenv("CRAWL_DELAY_SEC", "1"))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

def _split_urls(env_key: str):
    raw = os.getenv(env_key, "").strip()
    if not raw:
        return []
    return [u.strip() for u in raw.split(",") if u.strip()]

SITES = [
    {
        "name": "thevape",
        "base_url": os.getenv("THEVAPE_BASE_URL", "https://xn--9k3b21rv1k.com"),
        "category_urls": _split_urls("THEVAPE_CATEGORY_URLS"),
    },
    {
        "name": "juice24",
        "base_url": os.getenv("JUICE24_BASE_URL", "https://m.juice24.kr"),
        "category_urls": _split_urls("JUICE24_CATEGORY_URLS"),
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; simple-crawler/1.0)",
    "Accept-Language": "ko-KR,ko;q=0.9",
}
