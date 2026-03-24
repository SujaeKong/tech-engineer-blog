#!/bin/bash
# 매일 7:30 crontab에서 실행되는 자동 분석 스크립트
# 1) git pull (GitHub Actions가 수집한 최신 데이터)
# 2) Claude Code로 분석 + 포스트 생성
# 3) 커밋 + 푸시

set -o pipefail

BLOG_DIR="$HOME/tech-engineer-blog"
LOG_FILE="$BLOG_DIR/scripts/auto-analyze.log"

# crontab 환경에서 PATH 설정
export PATH="$HOME/.nvm/versions/node/v22.17.0/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 자동 분석 시작 =====" >> "$LOG_FILE"

cd "$BLOG_DIR"

# 로컬 변경사항 임시 저장 후 pull
git stash --include-untracked >> "$LOG_FILE" 2>&1 || true
git pull --rebase >> "$LOG_FILE" 2>&1
git stash pop >> "$LOG_FILE" 2>&1 || true

# Claude Code로 분석 및 포스트 생성
# --allowedTools: 권한 프롬프트 없이 필요한 도구만 허용
cat <<'PROMPT' | claude -p --allowedTools "Read Write Edit Glob Grep Bash(git:*) Bash(ls:*)"
~/tech-engineer-blog/_data/news_raw.json 파일을 읽고, 기술사 출제분야 8개 카테고리(소프트웨어공학/데이터베이스/네트워크/정보보안/IT경영/시스템구조/AI데이터분석/신기술융합) 관점에서 의미있는 뉴스를 선별하여 토픽 분석 포스트를 작성해줘.

각 포스트는 _posts/ 폴더에 YYYY-MM-DD-제목.md 형식으로 생성하고, 구조는: 뉴스 요약 → 핵심 개념 → 기술사 출제 포인트 → 관련 토픽 연계. 이미 _posts/에 있는 포스트와 중복되는 주제는 제외해줘.

중요: 마크다운 표 작성 시 반드시 표 위에 빈 줄을 넣고, 표 내부 행 사이에는 빈 줄을 넣지 마.

완료 후 git add, commit, push까지 해줘.
PROMPT

# 오늘의 토픽을 네이버 카페에 자동 게시
echo "$(date '+%Y-%m-%d %H:%M:%S') 카페 게시 시작..." >> "$LOG_FILE"
python3 "$BLOG_DIR/scripts/post_to_cafe.py" >> "$LOG_FILE" 2>&1 || true

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 자동 분석 완료 =====" >> "$LOG_FILE"
