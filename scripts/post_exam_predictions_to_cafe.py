#!/usr/bin/env python3
"""140회 출제예상 카드 10개를 네이버 카페 '출제예상문제' 게시판에 한 카드당 1글씩 게시.

일반 '오늘의 토픽'(post_to_cafe.py, menu 150)과는 다른 게시판(menu)에 올린다.
게시판 menu id는 --menu-id 인자 또는 EXAM_MENU_ID 환경변수로 지정한다.
(모르면 --list-menus로 카페 게시판 목록을 조회해 확인.)

이미 게시한 카드는 _data/exam_cafe_posted.json에 기록되어 재실행 시 건너뛴다.
naver.com 접속이 막힌 로컬/클라우드에서는 실행되지 않으니 CI(GitHub Actions)에서 돌린다.

사용법:
    python3 scripts/post_exam_predictions_to_cafe.py --list-menus
    python3 scripts/post_exam_predictions_to_cafe.py --menu-id 151 --dry-run
    python3 scripts/post_exam_predictions_to_cafe.py --menu-id 151
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

BLOG_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CRED_FILE = os.path.expanduser("~/.naver-cafe-api")
TOKEN_FILE = os.path.expanduser("~/.naver-cafe-token")
BLOG_URL = "https://sujaekong.github.io/tech-engineer-blog"

CLUB_ID = "19133896"
# 출제예상문제 게시판 menu id — 인자/환경변수로 주입 (게시판마다 다름)
DEFAULT_MENU_ID = os.environ.get("EXAM_MENU_ID", "")

# '[...]'는 glob 문자클래스로 오인되므로 전체를 훑고 문자열로 필터한다.
CARD_MARKER = "[출제예상-140회]"
STATE_FILE = os.path.join(BLOG_DIR, "_data", "exam_cafe_posted.json")

SOURCE_NOTE = "출처: KPC 정보관리기술사 기출·모의·합숙 통합 + 블로그 트렌드 (137~139 미출제 필터)"


# ── 크리덴셜/토큰 (post_to_cafe.py와 동일 방식) ──────────────────────────────
def load_credentials():
    if os.path.exists(CRED_FILE):
        creds = {}
        with open(CRED_FILE) as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    creds[k] = v
        return creds
    return {
        "NAVER_CLIENT_ID": os.environ.get("NAVER_CLIENT_ID", ""),
        "NAVER_CLIENT_SECRET": os.environ.get("NAVER_CLIENT_SECRET", ""),
    }


def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {
        "access_token": "",
        "refresh_token": os.environ.get("NAVER_REFRESH_TOKEN", ""),
    }


def refresh_token(creds, token_data):
    url = "https://nid.naver.com/oauth2.0/token?" + urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": creds["NAVER_CLIENT_ID"],
        "client_secret": creds["NAVER_CLIENT_SECRET"],
        "refresh_token": token_data["refresh_token"],
    })
    result = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
    new_token = json.loads(result.stdout)
    if "access_token" in new_token:
        if "refresh_token" not in new_token:
            new_token["refresh_token"] = token_data["refresh_token"]
        try:
            with open(TOKEN_FILE, "w") as f:
                json.dump(new_token, f, indent=2)
            os.chmod(TOKEN_FILE, 0o600)
        except OSError:
            pass  # CI: 파일 저장 불가해도 메모리 토큰으로 진행
        print("[INFO] 토큰 갱신 완료")
        return new_token
    print(f"[ERROR] 토큰 갱신 실패: {result.stdout}")
    return None


def get_access_token():
    creds = load_credentials()
    token_data = load_token()
    access_token = token_data.get("access_token", "")
    if not access_token:
        token_data = refresh_token(creds, token_data) or {}
        access_token = token_data.get("access_token", "")
    return access_token, creds, token_data


# ── 게시판 목록 조회 (menu id 확인용) ────────────────────────────────────────
def list_menus(token):
    url = f"https://openapi.naver.com/v1/cafe/{CLUB_ID}/menu"
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", url],
        capture_output=True, text=True,
    )
    print(result.stdout or result.stderr)


# ── 카드 파싱 ────────────────────────────────────────────────────────────────
def url_slug(path):
    """파일명(날짜 제외) → Jekyll permalink slug ('[',']','.' 제거)."""
    base = os.path.basename(path)[:-3]              # .md 제거
    after_date = "-".join(base.split("-")[3:])     # YYYY-MM-DD- 제거
    return after_date.replace("[", "").replace("]", "").replace(".", "")


def parse_card(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    title = ""
    category = ""
    in_fm = False
    for line in content.split("\n"):
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if in_fm:
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"\'')
            elif line.startswith("categories:"):
                category = line.split(":", 1)[1].strip().strip("[]").split(",")[0].strip()

    lines = content.split("\n")

    # 토픽 번호 + 선정 근거 (prompt-info 블록)
    topic_no = ""
    reason = ""
    for ln in lines:
        m = re.search(r"토픽\s*#(\d+)", ln)
        if m:
            topic_no = m.group(1)
        if ln.startswith("> 선정 근거:"):
            reason = ln[len("> 선정 근거:"):].strip()

    # 단답형 핵심 (### 단답형 ~ ### 논술형)
    short = []
    grab = False
    for ln in lines:
        if ln.startswith("### 단답형"):
            grab = True
            continue
        if grab:
            if ln.startswith("### "):
                break
            s = re.sub(r"\*\*(.+?)\*\*", r"\1", ln).strip()
            if s.startswith("- "):
                short.append(s[2:].strip())

    # 변형 문제 (## 7 ~ ## 8)
    questions = []
    grab = False
    for ln in lines:
        if re.match(r"^##\s*7\.", ln):
            grab = True
            continue
        if grab:
            if ln.startswith("## "):
                break
            s = ln.strip()
            if s.startswith("- "):
                questions.append(s[2:].strip().strip('"'))

    return {
        "path": path,
        "title": title,
        "category": category,
        "topic_no": topic_no,
        "reason": reason,
        "short": short,
        "questions": questions,
        "url": f"{BLOG_URL}/posts/{url_slug(path)}/",
    }


def make_content(card):
    lines = []
    lines.append(reason_line := f"▶ 선정 근거")
    lines.append(card["reason"])
    lines.append("")
    lines.append("▶ 출제 가능 문제")
    for i, q in enumerate(card["questions"][:3], 1):
        lines.append(f"{i}. {q}")
    lines.append("")
    lines.append("▶ 단답 핵심")
    for s in card["short"]:
        lines.append(f"- {s}")
    lines.append("")
    lines.append(f"▶ 상세 해설·답안 키워드·두음: {card['url']}")
    lines.append("")
    lines.append(SOURCE_NOTE)

    result = "<br>".join(lines)
    # 이중인코딩에서 문제되는 따옴표 제거
    for ch in ['"', '"', '"', "'", "'", "'"]:
        result = result.replace(ch, "")
    return result


# ── 게시 ─────────────────────────────────────────────────────────────────────
def post_article(menu_id, title, content, token, dry_run=False):
    if dry_run:
        print(f"\n[DRY-RUN] 게시판(menu)={menu_id}")
        print(f"[DRY-RUN] 제목: {title}")
        print(f"[DRY-RUN] 내용({len(content)}자):\n{content.replace('<br>', chr(10))}\n")
        return True, False

    import tempfile
    url = f"https://openapi.naver.com/v1/cafe/{CLUB_ID}/menu/{menu_id}/articles"
    subject_enc = urllib.parse.quote(urllib.parse.quote(title, safe=""), safe="")
    content_enc = urllib.parse.quote(urllib.parse.quote(content, safe=""), safe="")
    data_bytes = f"subject={subject_enc}&content={content_enc}".encode("utf-8")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".dat", mode="wb") as f:
        f.write(data_bytes)
        data_file = f.name
    try:
        result = subprocess.run(
            ["curl", "-s", "-S", "-X", "POST",
             "-H", f"Authorization: Bearer {token}",
             "-H", "Content-Type: application/x-www-form-urlencoded; charset=UTF-8",
             "--data-binary", f"@{data_file}", url],
            capture_output=True, text=True,
        )
    finally:
        os.unlink(data_file)

    response = result.stdout or result.stderr
    # 반환: (성공여부, 재시도가능여부). 네이버 '연속 등록' 제한은 잠시 후 재시도하면 풀린다.
    retryable = "연속" in response or '"code": "999"' in response or '"code":"999"' in response
    try:
        rj = json.loads(response)
        if rj.get("message", {}).get("status") == "200":
            print(f"[SUCCESS] {rj['message']['result'].get('articleUrl', '')}")
            return True, False
        print(f"[ERROR] 게시 실패: {response}")
        return False, retryable
    except json.JSONDecodeError:
        print(f"[ERROR] 응답 파싱 실패: {response}")
        return False, retryable


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return set(json.load(open(STATE_FILE)))
        except (json.JSONDecodeError, OSError):
            return set()
    return set()


def save_state(posted):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(posted), f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser(description="140회 출제예상 카드 카페 게시")
    ap.add_argument("--menu-id", default=DEFAULT_MENU_ID, help="출제예상문제 게시판 menu id")
    ap.add_argument("--dry-run", action="store_true", help="게시 없이 미리보기")
    ap.add_argument("--list-menus", action="store_true", help="카페 게시판 목록 조회")
    ap.add_argument("--force", action="store_true", help="이미 게시한 카드도 재게시")
    args = ap.parse_args()

    all_posts = glob.glob(os.path.join(BLOG_DIR, "_posts", "*.md"))
    card_paths = [p for p in all_posts if CARD_MARKER in os.path.basename(p)]
    cards = sorted(card_paths, key=lambda p: int(parse_card(p)["topic_no"] or 99))
    if not cards:
        print("[ERROR] 140회 출제예상 카드를 찾지 못했습니다.")
        sys.exit(1)

    # 게시판 목록 조회 모드
    if args.list_menus:
        token, _, _ = get_access_token()
        if not token:
            print("[ERROR] access_token 획득 실패")
            sys.exit(1)
        list_menus(token)
        return

    if not args.dry_run and not args.menu_id:
        print("[ERROR] --menu-id (또는 EXAM_MENU_ID)로 출제예상문제 게시판을 지정하세요.")
        print("        게시판 id를 모르면 --list-menus로 조회하세요.")
        sys.exit(1)

    posted = set() if args.force else load_state()

    token = ""
    if not args.dry_run:
        token, _, _ = get_access_token()
        if not token:
            print("[ERROR] access_token 획득 실패 (refresh_token 확인)")
            sys.exit(1)

    # 네이버는 연속 게시를 막으므로(에러 999) 게시 간 넉넉히 대기하고,
    # 제한에 걸리면 대기를 늘려가며 재시도한다. (환경변수로 조정 가능)
    post_delay = int(os.environ.get("POST_DELAY", "60"))    # 성공 후 다음 게시까지 대기(초)
    retry_wait = int(os.environ.get("RETRY_WAIT", "60"))    # 연속제한 시 재시도 기본 대기(초)
    max_retries = int(os.environ.get("MAX_RETRIES", "6"))   # 카드당 최대 재시도

    ok, skipped, failed = 0, 0, 0
    for path in cards:
        key = os.path.basename(path)
        if key in posted:
            print(f"[SKIP] 이미 게시됨: {key}")
            skipped += 1
            continue
        card = parse_card(path)
        cafe_title = f"[140회 출제예상 #{card['topic_no']}] {card['title'].replace('[출제예상 140회] ', '')}"
        cafe_content = make_content(card)
        print(f"[INFO] #{card['topic_no']} [{card['category']}] {card['title']}")

        attempt = 0
        while True:
            success, retryable = post_article(args.menu_id, cafe_title, cafe_content, token, dry_run=args.dry_run)
            if success:
                ok += 1
                if not args.dry_run:
                    posted.add(key)
                    save_state(posted)
                    time.sleep(post_delay)  # 다음 카드 전 대기
                break
            if retryable and attempt < max_retries and not args.dry_run:
                attempt += 1
                wait = retry_wait * attempt  # 재시도마다 대기 증가
                print(f"[RETRY] 연속 등록 제한 — {wait}s 대기 후 재시도 ({attempt}/{max_retries})")
                time.sleep(wait)
                continue
            failed += 1
            print(f"[FAIL] 게시 실패(재시도 소진/불가): {key}")
            break

    print(f"\n[DONE] 게시 {ok}건, 건너뜀 {skipped}건, 실패 {failed}건 (총 카드 {len(cards)}개)")
    if failed and not args.dry_run:
        sys.exit(1)  # 실패가 있으면 CI가 빨간불로 알림


if __name__ == "__main__":
    main()
