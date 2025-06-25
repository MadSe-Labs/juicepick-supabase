CREATE TABLE liquid_product
(
    id           uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name         text NOT NULL,
    brand        text,
    image_url    text,
    nicotine     NUMERIC,
    volume       INT,
    pg_ratio     INT,
    vg_ratio     INT,
    origin       text,
    manufacturer text,
    description  text,
    created_at   TIMESTAMP        DEFAULT now()
);

CREATE TABLE product_price
(
    id                uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id        uuid REFERENCES liquid_product (id),
    shop_name         text,
    price             INT,
    delivery_fee      INT,
    is_free_delivery  boolean,
    is_today_delivery boolean,
    shop_url          text,
    created_at        TIMESTAMP        DEFAULT now()
);

CREATE TABLE product_review
(
    id         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id uuid REFERENCES liquid_product (id),
    user_id    uuid REFERENCES auth.users (id),
    rating     INT,
    content    text,
    image_url  text[],
    tag        text[],
    created_at TIMESTAMP        DEFAULT now()
);
