#!/usr/bin/env python3
"""
Google News RSS에서 정보관리기술사 관련 뉴스를 수집하는 스크립트.

사용법:
    python3 scripts/fetch_news.py                    # 기본 키워드로 수집
    python3 scripts/fetch_news.py --days 3           # 최근 3일 뉴스
    python3 scripts/fetch_news.py --keyword "클라우드"  # 특정 키워드 추가

출력: _data/news_raw.json (수집된 원본 뉴스 데이터)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timedelta
from html import unescape
from xml.etree import ElementTree

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(PROJECT_DIR, "_data", "news_raw.json")

# 기술사 출제분야 관련 검색 키워드
# 카테고리별 균등 배분 (공통 + 8개 분야 × 2개 키워드)
DEFAULT_KEYWORDS = [
    # 공통
    "정보관리기술사",
    # 소프트웨어공학
    "소프트웨어공학 개발방법론",
    "DevOps MLOps 플랫폼",
    # 데이터베이스
    "데이터베이스 데이터모델링",
    "데이터 레이크하우스 파이프라인",
    # 네트워크
    "5G 6G 네트워크 기술",
    "SDN NFV 네트워크 가상화",
    # 정보보안
    "사이버보안 침해사고",
    "제로트러스트 보안 정책",
    # IT경영
    "IT거버넌스 디지털전환",
    "EA 정보전략계획 ISP",
    # 시스템구조
    "클라우드 인프라 아키텍처",
    "마이크로서비스 컨테이너 쿠버네티스",
    # AI데이터분석
    "인공지능 AI 기술",
    "생성형AI LLM",
    # 신기술융합
    "블록체인 양자컴퓨팅",
    "디지털트윈 메타버스 IoT",
]

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"


def fetch_rss(keyword: str, days: int = 7) -> list[dict]:
    """Google News RSS에서 키워드로 뉴스를 검색하여 반환. curl 사용 (Zscaler 호환)."""
    params = urllib.parse.urlencode({
        "q": keyword,
        "hl": "ko",
        "gl": "KR",
        "ceid": "KR:ko",
    })
    url = f"{GOOGLE_NEWS_RSS}?{params}"

    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "15", url],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            print(f"  [WARN] '{keyword}' curl 실패: {result.stderr}", file=sys.stderr)
            return []
        xml_data = result.stdout
    except Exception as e:
        print(f"  [WARN] '{keyword}' 수집 실패: {e}", file=sys.stderr)
        return []

    root = ElementTree.fromstring(xml_data)
    cutoff = datetime.now() - timedelta(days=days)
    items = []

    for item in root.findall(".//item"):
        title = unescape(item.findtext("title", "").strip())
        link = item.findtext("link", "").strip()
        pub_date_str = item.findtext("pubDate", "").strip()
        source = item.findtext("source", "").strip()

        # 날짜 파싱
        try:
            pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            pub_date = datetime.now()

        if pub_date < cutoff:
            continue

        # 언론사명 제거
        clean_title = re.sub(r"\s*-\s*[^-]+$", "", title)

        items.append({
            "title": clean_title,
            "full_title": title,
            "link": link,
            "source": source,
            "pub_date": pub_date.strftime("%Y-%m-%d"),
            "keyword": keyword,
        })

    return items


def deduplicate(articles: list[dict]) -> list[dict]:
    """제목 기준 중복 제거."""
    seen = set()
    unique = []
    for a in articles:
        key = re.sub(r"\s+", "", a["title"])[:30]
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


def main():
    parser = argparse.ArgumentParser(description="기술사 뉴스 RSS 수집기")
    parser.add_argument("--days", type=int, default=7, help="최근 N일 뉴스 수집 (기본: 7)")
    parser.add_argument("--keyword", type=str, help="추가 검색 키워드")
    args = parser.parse_args()

    keywords = DEFAULT_KEYWORDS[:]
    if args.keyword:
        keywords.append(args.keyword)

    print(f"[INFO] {len(keywords)}개 키워드로 최근 {args.days}일 뉴스 수집 시작...")

    all_articles = []
    for kw in keywords:
        print(f"  검색: '{kw}'")
        articles = fetch_rss(kw, days=args.days)
        all_articles.extend(articles)
        print(f"    -> {len(articles)}건")

    unique = deduplicate(all_articles)
    print(f"\n[INFO] 총 {len(all_articles)}건 수집, 중복 제거 후 {len(unique)}건")

    # 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "days": args.days,
            "total": len(unique),
            "articles": unique,
        }, f, ensure_ascii=False, indent=2)

    print(f"[INFO] 저장 완료: {OUTPUT_FILE}")
    return unique


if __name__ == "__main__":
    main()
