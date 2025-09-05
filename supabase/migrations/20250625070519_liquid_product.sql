CREATE TABLE liquid_product
(
    id              uuid PRIMARY KEY     DEFAULT uuid_generate_v4(), -- 제품 고유 식별자
    name            text        NOT NULL,                            -- 제품명
    brand           text        NOT NULL,                            -- 브랜드명
    image_url       text,                                            -- 제품 이미지 URL
    nicotine        NUMERIC,                                         -- 니코틴 함량(mg)
    volume          INT,                                             -- 용량(ml)
    pg_ratio        INT,                                             -- PG 비율(%)
    vg_ratio        INT,                                             -- VG 비율(%)
    description     text,                                            -- 상세 설명
    inhalation_type text,                                            -- 흡입 유형
    created_at      timestamptz NOT NULL DEFAULT now(),              -- 레코드 생성 시각
    updated_at      timestamptz NOT NULL DEFAULT now()               -- 레코드 수정 시각
);

CREATE TABLE product_price
(
    id             uuid PRIMARY KEY     DEFAULT uuid_generate_v4(), -- 가격 정보 고유 식별자
    product_id     uuid REFERENCES liquid_product (id),             -- 연관된 제품 식별자
    shop_name      text        NOT NULL,                            -- 판매처 이름
    price          INT         NOT NULL,                            -- 판매가(원)
    delivery_infos text[],                                          -- 배송정보
    shop_url       text        NOT NULL,                            -- 판매처 상품 페이지 URL
    created_at     timestamptz NOT NULL DEFAULT now(),              -- 레코드 생성 시각
    updated_at     timestamptz NOT NULL DEFAULT now()               -- 레코드 수정 시각
);


-- RLS 켜기
ALTER TABLE public.liquid_product enable ROW LEVEL SECURITY;
ALTER TABLE public.product_price enable ROW LEVEL SECURITY;

-- 모두 읽기 허용 (anon/authenticated 포함)
CREATE
policy "liquid_product read all"
ON PUBLIC.liquid_product
  AS PERMISSIVE
FOR
SELECT
    TO PUBLIC
    USING (TRUE);

CREATE
policy "product_price read all"
ON PUBLIC.product_price
  AS PERMISSIVE
FOR
SELECT
    TO PUBLIC
    USING (TRUE);