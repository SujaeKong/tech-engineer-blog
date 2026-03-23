#!/usr/bin/env python3
"""
수집된 뉴스 데이터를 Jekyll 포스트 마크다운으로 변환하는 유틸리티.

이 스크립트는 _data/news_raw.json을 읽어 기본 포스트 템플릿을 생성합니다.
실제 토픽 분석과 포스트 작성은 Claude가 직접 수행합니다.

사용법:
    python3 scripts/generate_post.py                          # news_raw.json 요약 출력
    python3 scripts/generate_post.py --create --title "제목"   # 빈 포스트 템플릿 생성
"""

import argparse
import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(PROJECT_DIR, "_data", "news_raw.json")
POSTS_DIR = os.path.join(PROJECT_DIR, "_posts")

CATEGORIES = [
    "소프트웨어공학",
    "데이터베이스",
    "네트워크",
    "정보보안",
    "IT경영",
    "시스템구조",
    "AI데이터분석",
    "신기술융합",
]


def slugify(text: str) -> str:
    """한글 제목을 파일명으로 변환."""
    import re
    text = re.sub(r"[^\w가-힣-]", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:60]


def create_post(title: str, category: str, tags: list[str], content: str = ""):
    """Jekyll 포스트 마크다운 파일 생성."""
    if category not in CATEGORIES:
        print(f"[ERROR] 유효하지 않은 카테고리: {category}")
        print(f"  가능한 카테고리: {', '.join(CATEGORIES)}")
        sys.exit(1)

    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    filepath = os.path.join(POSTS_DIR, filename)

    frontmatter = f"""---
layout: post
title: "{title}"
date: {date_str}
categories: {category}
tags: [{', '.join(tags)}]
source_url: ""
---

"""
    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter + content)

    print(f"[INFO] 포스트 생성: {filepath}")
    return filepath


def show_summary():
    """수집된 뉴스 데이터 요약 출력."""
    if not os.path.exists(DATA_FILE):
        print("[INFO] 수집된 뉴스 데이터가 없습니다. 먼저 fetch_news.py를 실행하세요.")
        return

    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    print(f"수집 시각: {data['fetched_at']}")
    print(f"총 {data['total']}건의 뉴스\n")

    # 키워드별 그룹핑
    by_keyword = {}
    for a in data["articles"]:
        kw = a["keyword"]
        by_keyword.setdefault(kw, []).append(a)

    for kw, articles in by_keyword.items():
        print(f"[{kw}] ({len(articles)}건)")
        for a in articles[:3]:
            print(f"  - {a['title']} ({a['pub_date']})")
        if len(articles) > 3:
            print(f"  ... 외 {len(articles)-3}건")
        print()


def main():
    parser = argparse.ArgumentParser(description="기술사 뉴스 포스트 생성기")
    parser.add_argument("--create", action="store_true", help="새 포스트 템플릿 생성")
    parser.add_argument("--title", type=str, help="포스트 제목")
    parser.add_argument("--category", type=str, help=f"카테고리: {', '.join(CATEGORIES)}")
    parser.add_argument("--tags", type=str, default="", help="태그 (쉼표 구분)")
    args = parser.parse_args()

    if args.create:
        if not args.title or not args.category:
            print("[ERROR] --title과 --category는 필수입니다.")
            sys.exit(1)
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        create_post(args.title, args.category, tags)
    else:
        show_summary()


if __name__ == "__main__":
    main()
