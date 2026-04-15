#!/bin/bash
# 매일 7:30 crontab에서 실행되는 자동 분석 스크립트
# 1) git pull (GitHub Actions가 수집한 최신 데이터)
# 2) Claude Code로 분석 + 포스트 생성
# 3) 커밋 + 푸시

# 개별 실패가 전체를 중단하지 않도록 set -e 사용 안 함

BLOG_DIR="$HOME/tech-engineer-blog"
LOG_FILE="$HOME/.tech-engineer-blog-auto.log"

# crontab 환경에서 PATH 설정
export PATH="$HOME/.nvm/versions/node/v22.17.0/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 자동 분석 시작 =====" >> "$LOG_FILE"

cd "$BLOG_DIR"

# 로컬 변경사항 초기화 후 pull (로그파일은 리포 밖이므로 안전)
git checkout -- . >> "$LOG_FILE" 2>&1 || true
git clean -fd >> "$LOG_FILE" 2>&1 || true
git pull >> "$LOG_FILE" 2>&1

# Claude Code로 분석 및 포스트 생성
echo "$(date '+%Y-%m-%d %H:%M:%S') Claude 분석 시작..." >> "$LOG_FILE"
cat <<'PROMPT' | claude -p --allowedTools "Read Write Edit Glob Grep Bash(git:*) Bash(ls:*)" >> "$LOG_FILE" 2>&1
~/tech-engineer-blog/_data/news_raw.json 파일을 읽고, 기술사 출제분야 8개 카테고리(소프트웨어공학/데이터베이스/네트워크/정보보안/IT경영/시스템구조/AI데이터분석/신기술융합) 관점에서 의미있는 뉴스를 선별하여 토픽 분석 포스트를 작성해줘.

**뉴스 선별 기준 (엄격하게 적용)**:
- ✅ 채택: 정부/공공기관 정책·표준 발표, 국제 표준 제정, 보안 사고/취약점, 신기술 출시, 학술 연구 성과, 기업의 의미있는 기술 발표
- ❌ 제외: 단순 칼럼/오피니언, 업체 홍보·마케팅 자료, 브랜드평판/순위 기사, 일반 비즈니스 팁, 단일 출처의 칼럼성 글
- 한 토픽이 **여러 출처에서 다뤄지는 뉴스**일수록 우선순위 높음 (실제 사건성)
- 단일 칼럼·홍보 글은 토픽으로 채택하지 말 것

포스트는 반드시 3개 작성하되, 3개 모두 다른 카테고리로 작성해줘. 기존 _posts/ 폴더에서 카테고리별 포스트 수를 확인하고, 포스트가 적은 카테고리를 우선 선택해줘.

각 포스트는 _posts/ 폴더에 YYYY-MM-DD-제목.md 형식으로 생성하고, 구조는: 뉴스 요약 → 핵심 개념 → 기술사 출제 포인트 → 관련 토픽 연계. 이미 _posts/에 있는 포스트와 중복되는 주제는 제외해줘.

중요: categories는 8개 중 1개만 넣어줘. 복수 카테고리 금지.
올바른 예: categories: 정보보안
잘못된 예: categories: [정보보안, IT경영]

중요: 마크다운 표 작성 시 반드시 표 위에 빈 줄을 넣고, 표 내부 행 사이에는 빈 줄을 넣지 마.

완료 후, 오늘 작성한 포스트 중 다음 회차 정보관리기술사 시험에 출제될 확률이 가장 높은 토픽 1개를 선정해서 _data/today_topic.txt 파일에 해당 포스트의 파일명(예: 2026-03-31-제목.md)만 한 줄로 저장해줘.

**오늘의 토픽 선정 기준**:
1. 뉴스의 실제성 - 사건/표준/정책 발표 등 구체적 이벤트 (단순 칼럼/홍보 X)
2. 출처 다양성 - 여러 언론사가 다룬 토픽 우선
3. 시사성 - 최근 1-2주 내 이슈
4. 시험 출제 가능성 - 기술사 출제분야와의 연관성, 최근 기출 트렌드

그 다음 git add, commit, push까지 해줘.
PROMPT
echo "$(date '+%Y-%m-%d %H:%M:%S') Claude 종료 코드: $?" >> "$LOG_FILE"

# 오늘의 토픽을 네이버 카페에 자동 게시
echo "$(date '+%Y-%m-%d %H:%M:%S') 카페 게시 시작..." >> "$LOG_FILE"
python3 "$BLOG_DIR/scripts/post_to_cafe.py" >> "$LOG_FILE" 2>&1 || true

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 자동 분석 완료 =====" >> "$LOG_FILE"
