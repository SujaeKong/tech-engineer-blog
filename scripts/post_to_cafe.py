#!/usr/bin/env python3
"""
오늘의 토픽을 네이버 카페에 자동 게시하는 스크립트.

사용법:
    python3 scripts/post_to_cafe.py              # 오늘 포스트 중 추천 토픽 자동 선택
    python3 scripts/post_to_cafe.py --dry-run    # 게시하지 않고 미리보기만

필요 파일:
    ~/.naver-cafe-api    — Client ID/Secret
    ~/.naver-cafe-token  — OAuth 토큰
"""

import argparse
import glob
import json
import os
import subprocess
import sys
import urllib.parse
from datetime import datetime

BLOG_DIR = os.path.expanduser("~/tech-engineer-blog")
CRED_FILE = os.path.expanduser("~/.naver-cafe-api")
TOKEN_FILE = os.path.expanduser("~/.naver-cafe-token")
BLOG_URL = "https://sujaekong.github.io/tech-engineer-blog"

CLUB_ID = "19133896"
MENU_ID = "150"

# 출제 빈도 높은 카테고리 우선순위
CATEGORY_PRIORITY = [
    "정보보안",
    "AI데이터분석",
    "소프트웨어공학",
    "네트워크",
    "데이터베이스",
    "IT경영",
    "시스템구조",
    "신기술융합",
]


def load_credentials():
    """API 크리덴셜 로드."""
    creds = {}
    with open(CRED_FILE) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                creds[k] = v
    return creds


def load_token():
    """OAuth 토큰 로드."""
    with open(TOKEN_FILE) as f:
        return json.load(f)


def refresh_token(creds, token_data):
    """토큰 갱신."""
    url = "https://nid.naver.com/oauth2.0/token?" + urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": creds["NAVER_CLIENT_ID"],
        "client_secret": creds["NAVER_CLIENT_SECRET"],
        "refresh_token": token_data["refresh_token"],
    })
    result = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
    new_token = json.loads(result.stdout)

    if "access_token" in new_token:
        # refresh_token은 갱신 응답에 없을 수 있음 (기존 유지)
        if "refresh_token" not in new_token:
            new_token["refresh_token"] = token_data["refresh_token"]
        with open(TOKEN_FILE, "w") as f:
            json.dump(new_token, f, indent=2)
        os.chmod(TOKEN_FILE, 0o600)
        print("[INFO] 토큰 갱신 완료")
        return new_token
    else:
        print(f"[ERROR] 토큰 갱신 실패: {result.stdout}")
        print("[ERROR] refresh_token이 만료되었을 수 있습니다. 'python3 scripts/naver_auth.py'로 재인증하세요.")
        return None


def find_today_topic():
    """Claude가 선정한 오늘의 토픽을 읽거나, 없으면 fallback."""
    today = datetime.now().strftime("%Y-%m-%d")
    topic_file = os.path.join(BLOG_DIR, "_data", "today_topic.txt")

    # Claude가 선정한 토픽 파일 확인
    target_filename = None
    if os.path.exists(topic_file):
        with open(topic_file, encoding="utf-8") as f:
            target_filename = f.read().strip()
        if target_filename:
            target_path = os.path.join(BLOG_DIR, "_posts", target_filename)
            if os.path.exists(target_path):
                print(f"[INFO] Claude 선정 토픽: {target_filename}")
            else:
                print(f"[WARN] Claude 선정 파일 없음: {target_filename}, fallback")
                target_filename = None

    # fallback: 오늘 포스트 중 첫 번째
    if not target_filename:
        posts = glob.glob(os.path.join(BLOG_DIR, f"_posts/{today}-*.md"))
        if not posts:
            print(f"[WARN] 오늘({today}) 포스트가 없습니다.")
            return None
        target_path = sorted(posts)[0]
        target_filename = os.path.basename(target_path)

    # 포스트 파일 읽기
    post_path = os.path.join(BLOG_DIR, "_posts", target_filename)
    with open(post_path, encoding="utf-8") as f:
        content = f.read()

    title = ""
    category = ""
    tags = []
    in_frontmatter = False
    for line in content.split("\n"):
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"\'')
            elif line.startswith("categories:"):
                category = line.split(":", 1)[1].strip()
            elif line.startswith("tags:"):
                tags_str = line.split(":", 1)[1].strip()
                tags = [t.strip().strip("[]") for t in tags_str.split(",")]

    return {
        "path": post_path,
        "title": title,
        "category": category,
        "tags": tags,
        "content": content,
    }


def make_cafe_content(topic):
    """카페 게시글 생성. 이중인코딩 제한(~300자)에 맞춰 요약 + 블로그 링크."""
    import re

    # frontmatter 제거하고 본문만 추출
    content = topic["content"]
    parts = content.split("---", 2)
    if len(parts) >= 3:
        body = parts[2].strip()
    else:
        body = content

    # 뉴스 요약 섹션 추출
    summary = ""
    in_summary = False
    for line in body.split("\n"):
        if "뉴스 요약" in line:
            in_summary = True
            continue
        if in_summary:
            if line.startswith("## "):
                break
            clean = re.sub(r'\*\*(.+?)\*\*', r'\1', line).strip()
            if clean:
                summary += clean + " "

    summary = summary.strip()
    # 200자 이내에서 마지막 온전한 문장으로 끊기
    if len(summary) > 200:
        cut = summary[:200]
        # 마지막 마침표/다 위치 찾기
        last_end = max(cut.rfind("."), cut.rfind("다."), cut.rfind("다 "))
        if last_end > 50:
            summary = cut[:last_end + 1].rstrip()
        else:
            summary = cut.rsplit(" ", 1)[0] + "..."

    # 출제 포인트 추출
    points = []
    in_points = False
    for line in body.split("\n"):
        if "출제 포인트" in line or "출제포인트" in line:
            in_points = True
            continue
        if in_points:
            if line.startswith("## "):
                break
            line = line.strip()
            # "- " 또는 "1. " 등 리스트/번호 형식 모두 처리
            if line.startswith("- ") or re.match(r'^\d+\.\s', line):
                point = re.sub(r'^\d+\.\s*', '', line)  # 번호 제거
                point = re.sub(r'^-\s*', '', point)  # 대시 제거
                point = re.sub(r'\*\*(.+?)\*\*', r'\1', point).strip()
                # 짧게 줄이기: 콜론 이후 제거, 40자 초과 시 자르기
                if ":" in point:
                    point = point.split(":")[0].strip()
                if len(point) > 40:
                    point = point[:40].rsplit(" ", 1)[0] + "..."
                if point:
                    points.append(point)

    # 블로그 링크 (한글 URL 그대로 사용)
    filename = os.path.basename(topic["path"]).replace(".md", "")
    slug = "-".join(filename.split("-")[3:])
    post_url = f"{BLOG_URL}/posts/{slug}/"

    # 카페 게시글 조합
    lines = []
    lines.append(f"[{topic['category']}] 기술사 토픽 분석")
    lines.append("")
    lines.append(summary)
    lines.append("")
    lines.append("기술사 출제 포인트:")
    for p in points[:4]:
        lines.append(f"- {p}")
    lines.append("")
    lines.append(f"원문 링크: {post_url}")

    result = "<br>".join(lines)
    # 이중인코딩에서 문제 되는 특수문자 제거
    result = result.replace('"', '').replace('"', '').replace('"', '')
    result = result.replace("'", "").replace("'", "").replace("'", "")
    return result


def post_to_cafe(title, content, token, dry_run=False):
    """네이버 카페에 게시글 작성."""
    if dry_run:
        print(f"\n[DRY-RUN] 제목: {title}")
        print(f"[DRY-RUN] 내용 길이: {len(content)}자")
        print(f"[DRY-RUN] 카페: {CLUB_ID}, 게시판: {MENU_ID}")
        return True

    import tempfile

    url = f"https://openapi.naver.com/v1/cafe/{CLUB_ID}/menu/{MENU_ID}/articles"

    # 이중 URL 인코딩 (네이버 카페 API 한글 깨짐 방지)
    subject_enc = urllib.parse.quote(urllib.parse.quote(title, safe=""), safe="")
    content_enc = urllib.parse.quote(urllib.parse.quote(content, safe=""), safe="")
    data_str = f"subject={subject_enc}&content={content_enc}"
    data_bytes = data_str.encode("utf-8")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".dat", mode="wb") as f:
        f.write(data_bytes)
        data_file = f.name

    try:
        result = subprocess.run(
            [
                "curl", "-s", "-S",
                "-X", "POST",
                "-H", f"Authorization: Bearer {token}",
                "-H", "Content-Type: application/x-www-form-urlencoded; charset=UTF-8",
                "--data-binary", f"@{data_file}",
                url,
            ],
            capture_output=True, text=True,
        )
    finally:
        os.unlink(data_file)

    response = result.stdout or result.stderr
    try:
        resp_json = json.loads(response)
        if "message" in resp_json and resp_json["message"].get("status") == "200":
            article_url = resp_json["message"]["result"].get("articleUrl", "")
            print(f"[SUCCESS] 카페 게시 완료: {article_url}")
            return True
        else:
            print(f"[ERROR] 카페 게시 실패: {response}")
            return False
    except json.JSONDecodeError:
        print(f"[ERROR] 응답 파싱 실패: {response}")
        return False


def main():
    parser = argparse.ArgumentParser(description="오늘의 토픽 카페 자동 게시")
    parser.add_argument("--dry-run", action="store_true", help="게시하지 않고 미리보기")
    args = parser.parse_args()

    # 오늘의 토픽 선택
    topic = find_today_topic()
    if not topic:
        sys.exit(1)

    print(f"[INFO] 오늘의 토픽: [{topic['category']}] {topic['title']}")

    # 카페 게시글 제목/내용 생성
    cafe_title = f"[오늘의 토픽] {topic['title']}"
    cafe_content = make_cafe_content(topic)

    if args.dry_run:
        post_to_cafe(cafe_title, cafe_content, "", dry_run=True)
        return

    # 토큰 로드
    creds = load_credentials()
    token_data = load_token()
    access_token = token_data["access_token"]

    # 게시 시도
    success = post_to_cafe(cafe_title, cafe_content, access_token)

    # 토큰 만료 시 갱신 후 재시도
    if not success:
        print("[INFO] 토큰 갱신 시도...")
        new_token = refresh_token(creds, token_data)
        if new_token:
            post_to_cafe(cafe_title, cafe_content, new_token["access_token"])


if __name__ == "__main__":
    main()
