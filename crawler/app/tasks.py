import time
from urllib.parse import urlparse
from celery import Celery
from .settings import SITES, CRAWL_DELAY_SEC, REDIS_URL
from .crawler import iter_detail_links_from_category, parse_detail
from .supabase_db import upsert_liquid_product, upsert_product_price

app = Celery("shop_crawler", broker=REDIS_URL, backend=REDIS_URL)

def _shop_name(base_url: str) -> str:
    host = urlparse(base_url).netloc
    if "juice24" in host: return "juice24"
    if "xn--9k3b21rv1k" in host or "thevape" in host: return "thevape"
    return host

@app.task
def crawl_category(site_name: str, base_url: str, category_url: str, max_pages: int | None = None):
    """
    max_pages=None 이면 '모든 페이지'를 긁습니다.
    """
    seen = saved = priced = 0
    shop = _shop_name(base_url)

    for link in iter_detail_links_from_category(base_url, category_url, max_pages=max_pages):
        seen += 1
        try:
            data = parse_detail(base_url, link)
            if not data:
                continue

            # 가격/배송 메타 분리
            price = data.pop("_price", None)
            delivery_infos = data.pop("_delivery_infos", None)

            # 1) 제품 upsert → id 반환
            pid = upsert_liquid_product(data)
            if pid and price is not None:
                # 2) 가격 upsert
                upsert_product_price(pid, shop_name=shop, price=price, shop_url=link, delivery_infos=delivery_infos)
                priced += 1

            saved += 1
        except Exception as e:
            print(f"[WARN] {site_name} {link} -> {e}")
        time.sleep(CRAWL_DELAY_SEC)

    return {"site": site_name, "category": category_url, "seen": seen, "saved": saved, "priced": priced}

@app.task
def crawl_site(site_name: str, max_pages: int | None = None):
    target = next((s for s in SITES if s["name"] == site_name), None)
    if not target:
        return {"error": f"unknown site: {site_name}"}
    base = target["base_url"]
    results = []
    for cat in target["category_urls"]:
        # max_pages=None → 전체 페이지
        r = crawl_category.delay(site_name, base, cat, max_pages=max_pages)
        results.append(r.id)
    return {"site": site_name, "submitted": results}

@app.task
def crawl_all_sites(max_pages: int | None = None):
    submitted = []
    for s in SITES:
        r = crawl_site.delay(s["name"], max_pages=max_pages)
        submitted.append(r.id)
    return {"submitted": submitted}
