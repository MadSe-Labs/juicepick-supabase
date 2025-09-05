import time, re
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
import requests
from bs4 import BeautifulSoup
from .settings import HEADERS, CRAWL_DELAY_SEC

def _soup(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")

def _ensure_page(url: str, page: int) -> str:
    u = urlparse(url)
    q = parse_qs(u.query, keep_blank_values=True)
    q["page"] = [str(page)]
    new_query = urlencode({k: v[0] for k, v in q.items()})
    return urlunparse((u.scheme, u.netloc, u.path, u.params, new_query, u.fragment))

def iter_detail_links_from_category(base_url: str, category_url: str, max_pages: int | None = None):
    cat_url = category_url
    if cat_url.startswith("/"):
        cat_url = urljoin(base_url, cat_url)

    seen = set()
    page = 1
    while True:
        if max_pages and page > max_pages:
            break
        page_url = _ensure_page(cat_url, page)
        soup = _soup(page_url)

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "product_no=" in href and "/product/detail" in href:
                full = urljoin(base_url, href)
                if full not in seen:
                    seen.add(full)
                    links.append(full)

        if not links:
            break

        for link in links:
            yield link

        page += 1
        time.sleep(CRAWL_DELAY_SEC)

def _text(t: str | None) -> str:
    return re.sub(r"\s+", " ", t).strip() if t else ""

def _num(text: str | None):
    if not text:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
    return float(m.group(1)) if m else None

def _pick_price(info: dict) -> int | None:
    """
    가격 우선순위: 할인판매가 > 판매가 > 소비자가
    """
    priority = ["할인판매가", "판매가", "소비자가"]
    # 정확 일치 우선
    for key in priority:
        for k, v in info.items():
            if key == k:
                n = _num(v)
                if n is not None:
                    return int(n)
    # 포함(부분일치) 보조
    for key in priority:
        for k, v in info.items():
            if key in k:
                n = _num(v)
                if n is not None:
                    return int(n)
    return None

def _pick_delivery(info: dict) -> list[str] | None:
    """
    배송/배송비 관련 텍스트를 배열로 수집(있을 때만)
    """
    candidates = []
    for k, v in info.items():
        lk = k.lower()
        if ("배송" in k) or ("delivery" in lk) or ("shipping" in lk):
            val = _text(v)
            if val:
                candidates.append(val)
    return candidates or None

def parse_detail(base_url: str, url: str) -> dict:
    soup = _soup(url)
    out = {}

    # 1) 제목(name/brand)
    title = None
    ogt = soup.find("meta", {"property": "og:title"})
    if ogt and ogt.get("content"):
        title = _text(ogt["content"])
    if not title:
        h = soup.find(["h1","h2","h3"])
        if h:
            title = _text(h.get_text())

    if title:
        m = re.match(r"^\[(?P<brand>.+?)\]\s*(?P<name>.+)$", title)
        if m:
            out["brand"] = _text(m.group("brand"))
            out["name"]  = _text(m.group("name"))
        else:
            out["name"]  = title

    # 2) 대표 이미지
    ogimg = soup.find("meta", {"property": "og:image"})
    if ogimg and ogimg.get("content"):
        out["image_url"] = _text(ogimg["content"])
    else:
        img = soup.select_one("img[src]")
        if img:
            out["image_url"] = img.get("src")

    # 3) 기본정보 표(th/td 또는 dt/dd)
    info = {}
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            th = tr.find(["th","dt"])
            td = tr.find(["td","dd"])
            if th and td:
                k = _text(th.get_text())
                v = _text(td.get_text())
                if k and v:
                    info[k] = v

    # 브랜드(제목 실패 시)
    if "brand" not in out:
        for k in info:
            if "브랜드" in k:
                out["brand"] = _text(info[k]); break

    # 니코틴
    for k in info:
        if "니코틴" in k:
            n = _num(info[k])
            if n is not None:
                out["nicotine"] = n
            break

    # 용량(ml)
    for k in info:
        if "용량" in k:
            v = _num(info[k])
            if v is not None:
                out["volume"] = int(v)
            break

    # PG/VG
    for k in info:
        lk = k.lower()
        if "pg" in lk:
            v = _num(info[k])
            if v is not None: out["pg_ratio"] = int(v)
        if "vg" in lk:
            v = _num(info[k])
            if v is not None: out["vg_ratio"] = int(v)

    # 흡입 타입
    for k in info:
        if "흡입" in k or "권장" in k:
            v = info[k]
            if "입호흡" in v: out["inhalation_type"] = "입호흡"
            elif "폐호흡" in v: out["inhalation_type"] = "폐호흡"
            else: out["inhalation_type"] = _text(v)
            break
    if "inhalation_type" not in out and "name" in out:
        if "입호흡" in out["name"]: out["inhalation_type"] = "입호흡"
        elif "폐호흡" in out["name"]: out["inhalation_type"] = "폐호흡"

    # 4) 가격/배송(있을 때만 메타키로 첨부)
    price = _pick_price(info)
    if price is not None:
        out["_price"] = price
    delivery = _pick_delivery(info)
    if delivery:
        out["_delivery_infos"] = delivery

    # 설명(있을 때만)
    detail = soup.select_one("#prdDetail, .xans-product-detail, .cont")
    if detail:
        out["description"] = _text(detail.get_text())[:2000]

    # 빈 값 제거
    return {k: v for k, v in out.items() if v not in (None, "", [])}
