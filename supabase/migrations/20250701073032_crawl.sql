-- init sql로 서비스 실행시 넣을것.
CREATE TABLE crawl_site
(
    id             bigserial PRIMARY KEY,                       -- 사이트 정보 고유 식별자
    name           VARCHAR(100) NOT NULL,                       -- 사이트 이름
    base_url       text         NOT NULL,                       -- 크롤링 대상 기본 URL
    login_required boolean      NOT NULL         DEFAULT FALSE, -- 로그인 필요 여부
    status         VARCHAR(20)  NOT NULL                        -- 크롤링 활성 상태 ('active'/'inactive')
        CHECK (status IN ('active', 'inactive')) DEFAULT 'active',
    created_at     timestamptz  NOT NULL         DEFAULT now(), -- 레코드 생성 시각
    updated_at     timestamptz  NOT NULL         DEFAULT now()  -- 레코드 수정 시각
);
