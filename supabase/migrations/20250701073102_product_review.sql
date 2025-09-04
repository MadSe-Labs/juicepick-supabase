CREATE TABLE product_review
(
    id           uuid PRIMARY KEY DEFAULT uuid_generate_v4(),                -- 리뷰 고유 식별자
    product_id   uuid REFERENCES liquid_product (id),                        -- 연관된 제품 식별자
    user_id      uuid NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE, -- 작성자(유저) 식별자
    total_rating INT,                                                        -- 평점(1~5)
    content      text,                                                       -- 리뷰 내용
    image_url    text[],                                                     -- 리뷰 이미지 URL 목록
    tag          text[],                                                     -- 리뷰 태그 목록
    created_at   TIMESTAMP        DEFAULT now()                              -- 레코드 생성 시각
);

CREATE TABLE review_rating
(
    review_id UUID REFERENCES product_review (id) ON DELETE CASCADE,
    category  TEXT NOT NULL, -- '단맛','멘솔','목긁음','바디감','상큼함'
    score     INT  NOT NULL, -- 1~5
    PRIMARY KEY (review_id, category)
);
