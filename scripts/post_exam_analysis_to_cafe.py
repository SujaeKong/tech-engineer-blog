#!/usr/bin/env python3
"""
출제 적중률 분석 포스트를 네이버 카페 '출제예상문제' 게시판(menu 137)에 1회 게시.

post_to_cafe.py 의 인증/게시 함수를 재사용하되,
- 게시판은 EXAM_MENU_ID(기본 137)
- 본문은 분석 포스트 전용 요약(적중률·직접적중 카드·블로그 링크)로 구성한다.

naver.com 이 열려 있는 GitHub Actions(CI)에서 실행하는 것을 전제로 한다.
로컬(맥) 컨테이너는 naver 접속이 막혀 있어도 CI가 대신 게시한다.

사용법:
    python3 scripts/post_exam_analysis_to_cafe.py            # 실제 게시
    python3 scripts/post_exam_analysis_to_cafe.py --dry-run  # 미리보기
환경변수:
    ANALYSIS_POST  게시할 _posts 파일명 (기본: 2026-08-23-140회-기출-적중률-분석.md)
    EXAM_MENU_ID   게시판 menu id (기본: 137)
"""

import argparse
import os
import sys
import time

import post_to_cafe as P

BLOG_DIR = P.BLOG_DIR
BLOG_URL = P.BLOG_URL
DEFAULT_POST = "2026-08-23-140회-기출-적중률-분석.md"


def build_content(post_path):
    """분석 포스트 → 카페 본문(요약 + 블로그 링크). 이중인코딩 대비 특수문자 정리."""
    filename = os.path.basename(post_path).replace(".md", "")
    # 날짜 접두어(YYYY-MM-DD-) 제거 → 슬러그
    slug = "-".join(filename.split("-")[3:])
    post_url = f"{BLOG_URL}/posts/{slug}/"

    lines = [
        "[140회 적중률 분석] 정보관리 기출 vs 출제예상 10개 카드",
        "",
        "■ 종합",
        "- 카드 직접 5/10(50%), 직접+부분 9/10(90%)",
        "- 문항 직접 5/31(16%), 직접+부분 10/31(32%)",
        "- 139회(직접 40%) 대비 카드 직접 적중률 상승",
        "",
        "■ 직접 적중 카드 (5)",
        "- AI 데이터센터 → 4교시 AI DC",
        "- AI 안전성/레드팀 → 2교시 AI 보안",
        "- 고영향 AI → 3교시 인공지능기본법",
        "- 오픈웨이트 → 2교시 오픈웨이트 라이선스",
        "- 피지컬 AI → 1교시 Physical AI",
        "",
        "■ 미적중: NTN(위성/6G)",
        "■ 약점: CS 기본기(SW공학/시스템구조)/통계 슬롯 부족 (139회 동일 패턴)",
        "",
        f"원문 링크(전체 분석): {post_url}",
    ]
    result = "<br>".join(lines)
    # 이중인코딩에서 문제 되는 따옴표류 제거
    for ch in ['"', '"', '"', "'", "'", "'"]:
        result = result.replace(ch, "")
    return result


def main():
    parser = argparse.ArgumentParser(description="적중률 분석 포스트 카페 게시(menu 137)")
    parser.add_argument("--dry-run", action="store_true", help="게시하지 않고 미리보기")
    args = parser.parse_args()

    # 게시판 지정 (post_to_cafe 모듈 전역 MENU_ID 를 137로 오버라이드)
    P.MENU_ID = os.environ.get("EXAM_MENU_ID", "137")

    post_name = os.environ.get("ANALYSIS_POST", DEFAULT_POST)
    post_path = os.path.join(BLOG_DIR, "_posts", post_name)
    if not os.path.exists(post_path):
        print(f"[ERROR] 분석 포스트 없음: {post_path}")
        sys.exit(1)

    # 포스트 title(frontmatter) 추출 → 카페 제목
    title = ""
    with open(post_path, encoding="utf-8") as f:
        in_fm = False
        for line in f:
            s = line.strip()
            if s == "---":
                in_fm = not in_fm
                continue
            if in_fm and line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip("\"'")
                break

    cafe_title = f"[적중률 분석] {title}" if title else "[적중률 분석] 140회 출제예상 결산"
    cafe_content = build_content(post_path)

    print(f"[INFO] 게시판(menu): {P.MENU_ID}")
    print(f"[INFO] 제목: {cafe_title}")

    if args.dry_run:
        P.post_to_cafe(cafe_title, cafe_content, "", dry_run=True)
        print("\n----- 본문 미리보기 -----")
        print(cafe_content.replace("<br>", "\n"))
        return

    # 토큰 준비 (CI: refresh_token → access_token 갱신)
    creds = P.load_credentials()
    token_data = P.load_token()
    access_token = token_data.get("access_token", "")
    if not access_token:
        token_data = P.refresh_token(creds, token_data) or {}
        access_token = token_data.get("access_token", "")
        if not access_token:
            print("[ERROR] access_token 획득 실패 (refresh_token 확인 필요)")
            sys.exit(1)

    # 게시 시도 (999 연속등록 제한 대비 간단 재시도)
    max_retries = 4
    for attempt in range(1, max_retries + 1):
        ok = P.post_to_cafe(cafe_title, cafe_content, access_token)
        if ok:
            return
        # 토큰 만료면 갱신 후 재시도, 그 외(999 등)는 대기 후 재시도
        print(f"[INFO] 재시도 {attempt}/{max_retries} …")
        new_token = P.refresh_token(creds, token_data)
        if new_token:
            token_data = new_token
            access_token = new_token["access_token"]
        if attempt < max_retries:
            time.sleep(30 * attempt)

    print("[ERROR] 게시 최종 실패")
    sys.exit(1)


if __name__ == "__main__":
    main()
