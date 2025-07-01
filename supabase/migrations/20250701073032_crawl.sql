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

CREATE TABLE crawl_schedule
(
    id              bigserial PRIMARY KEY,              -- 스케줄 고유 식별자
    site_id         bigint      NOT NULL                -- 연관된 사이트 식별자
        REFERENCES crawl_site (id) ON DELETE CASCADE,
    schedule_name   text        NOT NULL UNIQUE,        -- 스케줄 이름 (유니크)
    cron_expression text        NOT NULL,               -- 실행 주기(CRON 표현식)
    cron_job_id     INT,                                -- 외부 스케줄러에 등록된 작업 ID
    invocation      jsonb       NOT NULL,               -- 실행 시 전달할 파라미터(JSONB)
    is_enabled      boolean     NOT NULL DEFAULT TRUE,  -- 스케줄 활성화 여부
    created_at      timestamptz NOT NULL DEFAULT now(), -- 레코드 생성 시각
    updated_at      timestamptz NOT NULL DEFAULT now()  -- 레코드 수정 시각
);
