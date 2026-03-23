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
        return None


def find_today_topic():
    """오늘 포스트 중 출제 확률 높은 토픽 선택."""
    today = datetime.now().strftime("%Y-%m-%d")
    posts = glob.glob(os.path.join(BLOG_DIR, f"_posts/{today}-*.md"))

    if not posts:
        print(f"[WARN] 오늘({today}) 포스트가 없습니다.")
        return None

    # 카테고리 우선순위로 정렬
    scored = []
    for post_path in posts:
        with open(post_path, encoding="utf-8") as f:
            content = f.read()

        # frontmatter에서 제목, 카테고리 추출
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

        priority = len(CATEGORY_PRIORITY)
        if category in CATEGORY_PRIORITY:
            priority = CATEGORY_PRIORITY.index(category)

        scored.append({
            "path": post_path,
            "title": title,
            "category": category,
            "tags": tags,
            "content": content,
            "priority": priority,
        })

    # 우선순위 높은 것 선택
    scored.sort(key=lambda x: x["priority"])
    return scored[0]


def make_cafe_content(topic):
    """카페 게시글 HTML 생성."""
    # frontmatter 제거하고 본문만 추출
    content = topic["content"]
    parts = content.split("---", 2)
    if len(parts) >= 3:
        body = parts[2].strip()
    else:
        body = content

    # 마크다운을 간단한 HTML로 변환
    lines = body.split("\n")
    html_lines = []
    in_code = False
    in_table = False

    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                html_lines.append("</pre>")
                in_code = False
            else:
                html_lines.append("<pre>")
                in_code = True
            continue

        if in_code:
            html_lines.append(line)
            continue

        # 표 처리
        if line.strip().startswith("|"):
            if line.strip().startswith("|--") or line.strip().startswith("| --"):
                continue  # 구분선 건너뛰기
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                html_lines.append("<table border='1' cellpadding='5' cellspacing='0'>")
                html_lines.append("<tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr>")
                in_table = True
            else:
                html_lines.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
            continue
        elif in_table:
            html_lines.append("</table>")
            in_table = False

        # 제목
        if line.startswith("## "):
            html_lines.append(f"<h3>{line[3:]}</h3>")
        elif line.startswith("### "):
            html_lines.append(f"<h4>{line[4:]}</h4>")
        elif line.startswith("- **"):
            html_lines.append(f"<li>{line[2:]}</li>")
        elif line.startswith("- "):
            html_lines.append(f"<li>{line[2:]}</li>")
        elif line.startswith("> "):
            html_lines.append(f"<blockquote>{line[2:]}</blockquote>")
        elif line.strip():
            # bold 처리
            import re
            line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
            html_lines.append(f"<p>{line}</p>")
        else:
            html_lines.append("<br>")

    if in_table:
        html_lines.append("</table>")
    if in_code:
        html_lines.append("</pre>")

    # 블로그 링크 추가
    filename = os.path.basename(topic["path"]).replace(".md", "")
    # 날짜 부분 제거하고 slug 추출
    slug = "-".join(filename.split("-")[3:])
    post_url = f"{BLOG_URL}/posts/{urllib.parse.quote(slug)}/"

    blog_link = (
        f'<br><hr>'
        f'<p><b>전체 분석 보기:</b> <a href="{post_url}">{post_url}</a></p>'
        f'<p><b>기술사 뉴스 블로그:</b> <a href="{BLOG_URL}">{BLOG_URL}</a></p>'
    )

    return "\n".join(html_lines) + blog_link


def post_to_cafe(title, content, token, dry_run=False):
    """네이버 카페에 게시글 작성."""
    if dry_run:
        print(f"\n[DRY-RUN] 제목: {title}")
        print(f"[DRY-RUN] 내용 길이: {len(content)}자")
        print(f"[DRY-RUN] 카페: {CLUB_ID}, 게시판: {MENU_ID}")
        return True

    import tempfile

    url = f"https://openapi.naver.com/v1/cafe/{CLUB_ID}/menu/{MENU_ID}/articles"

    # 특수문자로 인한 curl 오류 방지: 임시 파일 사용
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(content)
        content_file = f.name

    try:
        result = subprocess.run(
            [
                "curl", "-s", "-S",
                "-X", "POST",
                "-H", f"Authorization: Bearer {token}",
                "-F", f"subject={title}",
                "-F", f"content=<{content_file}",
                url,
            ],
            capture_output=True, text=True,
        )
    finally:
        os.unlink(content_file)

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
