-- 확장 (없으면 생성)
create extension if not exists pgcrypto;  -- gen_random_uuid()

-- 1) 공개 프로필 (공식 문서의 profiles 테이블 패턴)
create table if not exists public.user_profile (
    id           uuid not null references auth.users on delete cascade,
    user_name    text not null,
    primary key (id)
);

-- RLS
ALTER TABLE public.user_profile enable ROW LEVEL SECURITY;

-- 2) 공개 읽기 (닉네임/아바타 공개)
CREATE
POLICY "user_profile select public"
  ON PUBLIC.user_profile
  AS PERMISSIVE
  FOR
SELECT
    TO PUBLIC
    USING (TRUE);

-- 3) 본인만 작성
CREATE
POLICY "user_profile insert self"
  ON PUBLIC.user_profile
       AS PERMISSIVE
  FOR INSERT
  WITH CHECK ((SELECT auth.uid()) = id);  -- PK가 id면 id로 변경

-- 4) 본인만 수정
CREATE
POLICY "user_profile update self"
  ON PUBLIC.user_profile
       AS PERMISSIVE
  FOR
UPDATE
    to PUBLIC
    USING (auth.uid() = id); -- PK가 id면 id로 변경


-- inserts a row into public.profiles
CREATE FUNCTION public.handle_new_user()
    RETURNS trigger
    LANGUAGE plpgsql
SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
INSERT INTO public.profiles (id, user_name)
VALUES (new.id, new.raw_user_meta_data ->> 'user_name');
RETURN new;
END;
$$;

-- trigger the function every time a user is created
CREATE TRIGGER on_auth_user_created
    AFTER INSERT
    ON auth.users
    FOR EACH ROW EXECUTE procedure PUBLIC.handle_new_user();
