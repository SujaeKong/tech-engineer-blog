#!/bin/bash
# 매일 7:30 crontab에서 실행되는 자동 분석 스크립트
# 1) git pull (GitHub Actions가 수집한 최신 데이터)
# 2) Claude Code로 분석 + 포스트 생성
# 3) 커밋 + 푸시

set -e

BLOG_DIR="$HOME/tech-engineer-blog"
LOG_FILE="$BLOG_DIR/scripts/auto-analyze.log"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 자동 분석 시작 =====" >> "$LOG_FILE"

cd "$BLOG_DIR"

# 최신 데이터 pull (GitHub Actions가 커밋한 news_raw.json)
git pull --rebase >> "$LOG_FILE" 2>&1

# Claude Code로 분석 및 포스트 생성
claude -p "
~/tech-engineer-blog/_data/news_raw.json 파일을 읽고,
기술사 출제분야 8개 카테고리(소프트웨어공학/데이터베이스/네트워크/정보보안/IT경영/시스템구조/AI데이터분석/신기술융합) 관점에서
의미있는 뉴스를 선별하여 토픽 분석 포스트를 작성해줘.

각 포스트는 _posts/ 폴더에 YYYY-MM-DD-제목.md 형식으로 생성하고,
구조는: 뉴스 요약 → 핵심 개념 → 기술사 출제 포인트 → 관련 토픽 연계.
이미 _posts/에 있는 포스트와 중복되는 주제는 제외해줘.

완료 후 git add, commit, push까지 해줘.
" >> "$LOG_FILE" 2>&1

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 자동 분석 완료 =====" >> "$LOG_FILE"
