#!/usr/bin/env python3
"""포스트 내부 링크를 검증/수정하는 스크립트.

auto-analyze.sh가 Claude로 포스트 생성 후 호출하여:
1. 잘못된 링크 패턴 자동 변환 (.md, /YYYY/MM/DD/ → /posts/슬러그/)
2. 존재하지 않는 슬러그 발견 시 경고
"""

import glob
import os
import re
import sys
import urllib.parse

POSTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_posts")
BASE_PATH = "/tech-engineer-blog/posts"


def normalize_slug(s):
    """Jekyll URL 생성 규칙에 맞춰 슬러그 정규화 — 대괄호 등 특수문자 제거 후 연속 하이픈 압축"""
    s = re.sub(r"[\[\]()]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def get_existing_slugs():
    slugs = set()
    for f in glob.glob(os.path.join(POSTS_DIR, "*.md")):
        name = os.path.basename(f).replace(".md", "")
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
        slugs.add(normalize_slug(slug))
    return slugs


def fix_post(filepath, valid_slugs):
    with open(filepath) as f:
        content = f.read()

    original = content

    # 패턴 1: [텍스트](2026-MM-DD-슬러그.md) → /posts/슬러그/
    def fix_md(m):
        text = m.group(1)
        filename = m.group(2)
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", filename).replace(".md", "")
        return f"[{text}]({BASE_PATH}/{slug}/)"

    content = re.sub(
        r"\[([^\]]+)\]\((\d{4}-\d{2}-\d{2}-[^)]+\.md)\)", fix_md, content
    )

    # 패턴 2: /YYYY/MM/DD/슬러그/ → /posts/슬러그/
    content = re.sub(
        r"\]\((/tech-engineer-blog)?/\d{4}/\d{2}/\d{2}/([^)]+)\)",
        rf"]({BASE_PATH}/\2)",
        content,
    )

    changed = content != original

    # 깨진 슬러그 검증
    broken = []
    for m in re.finditer(rf"\]\({re.escape(BASE_PATH)}/([^)]+?)/?\)", content):
        slug = urllib.parse.unquote(m.group(1).rstrip("/"))
        if normalize_slug(slug) not in valid_slugs:
            broken.append(slug)

    if changed:
        with open(filepath, "w") as f:
            f.write(content)

    return changed, broken


def main():
    valid_slugs = get_existing_slugs()
    fixed_count = 0
    warning_count = 0

    for f in sorted(glob.glob(os.path.join(POSTS_DIR, "*.md"))):
        changed, broken = fix_post(f, valid_slugs)
        name = os.path.basename(f)
        if changed:
            fixed_count += 1
            print(f"[FIX] {name}")
        for slug in broken:
            warning_count += 1
            print(f"[WARN] {name} → 존재하지 않는 슬러그: {slug}")

    print(f"\n총 {fixed_count}개 파일 수정, {warning_count}개 경고")
    return 0


if __name__ == "__main__":
    sys.exit(main())
