from typing import Dict, List, Optional
from supabase import create_client
from .settings import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_ANON_KEY

def _client():
    key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY
    if not SUPABASE_URL or not key:
        raise RuntimeError("Supabase 환경변수(SUPABASE_URL/KEY)가 비어있습니다.")
    return create_client(SUPABASE_URL, key)

ALLOWED = {
    "name","brand","image_url","nicotine","volume",
    "pg_ratio","vg_ratio","description","inhalation_type",
}

def upsert_liquid_product(data: Dict) -> Optional[str]:
    """
    - data: 파서가 '실제로 존재한 값'만 담은 dict
    - 기준키: (name, brand)
    - return: 제품 UUID (업데이트든 신규든)
    """
    payload = {k: v for k, v in data.items() if k in ALLOWED and v not in (None, "", [])}
    if not payload.get("name") or not payload.get("brand"):
        return None

    sb = _client()

    # 1) 존재 여부 조회
    sel = sb.table("liquid_product") \
        .select("id") \
        .eq("name", payload["name"]) \
        .eq("brand", payload["brand"]) \
        .limit(1) \
        .execute()

    if sel.data:
        pid = sel.data[0]["id"]
        # 2) UPDATE (name/brand 제외)
        update_fields = {k: v for k, v in payload.items() if k not in ("name","brand")}
        if update_fields:
            sb.table("liquid_product").update(update_fields).eq("id", pid).execute()
        return pid
    else:
        # 3) INSERT (있는 키만) + id 반환
        ins = sb.table("liquid_product").insert(payload).select("id").execute()
        if ins.data:
            return ins.data[0]["id"]
        # 혹시 select 미지원일 경우 재조회
        sel2 = sb.table("liquid_product") \
            .select("id") \
            .eq("name", payload["name"]) \
            .eq("brand", payload["brand"]) \
            .limit(1) \
            .execute()
        return sel2.data[0]["id"] if sel2.data else None

def upsert_product_price(product_id: str, shop_name: str, price: int, shop_url: str, delivery_infos: Optional[List[str]] = None):
    """
    product_price upsert:
      - 기준: (product_id, shop_url)
      - 있으면 price/배송정보 업데이트, 없으면 insert
    """
    if not product_id or price is None or shop_url is None:
        return

    sb = _client()

    sel = sb.table("product_price") \
        .select("id") \
        .eq("product_id", product_id) \
        .eq("shop_url", shop_url) \
        .limit(1) \
        .execute()

    payload = {
        "product_id": product_id,
        "shop_name": shop_name,
        "price": int(price),
        "shop_url": shop_url,
    }
    if delivery_infos:
        payload["delivery_infos"] = delivery_infos

    if sel.data:
        sb.table("product_price").update(payload).eq("id", sel.data[0]["id"]).execute()
    else:
        sb.table("product_price").insert(payload).execute()
