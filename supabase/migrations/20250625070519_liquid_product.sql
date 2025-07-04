CREATE TABLE liquid_product
(
    id               uuid PRIMARY KEY DEFAULT uuid_generate_v4(), -- 제품 고유 식별자
    name             text NOT NULL,                               -- 제품명
    brand            text NOT NULL,                               -- 브랜드명
    image_url        text,                                        -- 제품 이미지 URL
    nicotine         NUMERIC,                                     -- 니코틴 함량(mg)
    volume           INT,                                         -- 용량(ml)
    pg_ratio         INT,                                         -- PG 비율(%)
    vg_ratio         INT,                                         -- VG 비율(%)
    origin           text,                                        -- 원산지
    manufacturer     text,                                        -- 제조사
    description      text,                                        -- 상세 설명
    inhalation_types text,                                        -- 상세 설명
    flavors          text,                                        -- 상세 설명
    created_at       TIMESTAMP        DEFAULT now()               -- 레코드 생성 시각
);

CREATE TABLE product_price
(
    id                uuid PRIMARY KEY DEFAULT uuid_generate_v4(), -- 가격 정보 고유 식별자
    product_id        uuid REFERENCES liquid_product (id),         -- 연관된 제품 식별자
    shop_name         text NOT NULL,                               -- 판매처 이름
    price             INT  NOT NULL,                               -- 판매가(원)
    delivery_fee      INT,                                         -- 배송비(원)
    is_free_delivery  boolean,                                     -- 무료 배송 여부
    is_today_delivery boolean,                                     -- 당일 배송 가능 여부
    shop_url          text NOT NULL,                               -- 판매처 상품 페이지 URL
    created_at        TIMESTAMP        DEFAULT now()               -- 레코드 생성 시각
);
