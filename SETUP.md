# 기술사 뉴스 블로그 자동화 셋업

## 프로젝트 개요

Google News RSS에서 정보관리기술사 관련 뉴스를 수집하고, Claude AI가 기술사 출제분야 관점으로 분석하여 블로그 포스트와 네이버 카페 글을 자동 생성하는 파이프라인.

- **블로그**: https://sujaekong.github.io/tech-engineer-blog/
- **카페**: https://cafe.naver.com/kpcitpe
- **검색엔진**: https://kpcitpe-search.pages.dev/

## 아키텍처

```
GitHub Actions (07:00 KST)
  └─ scripts/fetch_news.py
     └─ Google News RSS 수집 (16개 키워드, 카테고리별 균등)
        └─ _data/news_raw.json 자동 커밋

수동 실행 (bash scripts/auto-analyze.sh)
  ├─ git pull
  ├─ Claude 분석 (claude -p)
  │   ├─ 포스트 3개 생성 (서로 다른 카테고리, 부족 카테고리 우선)
  │   ├─ 오늘의 토픽 1개 선정 → _data/today_topic.txt
  │   └─ git commit + push
  ├─ scripts/fix_links.py (깨진 내부 링크 자동 수정)
  └─ scripts/post_to_cafe.py
      ├─ today_topic.txt 읽기
      ├─ 요약 + 출제 포인트 + 원문 링크 조합
      ├─ 이중 URL 인코딩 (한글 깨짐 방지)
      └─ 네이버 카페 API 게시
```

## 다른 PC 셋업 방법

### 1. 필수 도구 설치
```bash
# Node.js + Claude Code
npm install -g @anthropic-ai/claude-code
claude setup-token  # 1년 유효 토큰 발급

# Python (curl, git은 Mac 기본)
python3 --version  # 3.10+ 권장

# GitHub CLI
brew install gh
gh auth login
```

### 2. 리포 clone
```bash
cd ~
git clone https://github.com/SujaeKong/tech-engineer-blog.git
cd tech-engineer-blog
```

### 3. 네이버 카페 토큰 복사
원본 PC에서 새 PC로 두 파일 복사:
- `~/.naver-cafe-api` (Client ID/Secret)
- `~/.naver-cafe-token` (OAuth 토큰)

또는 새로 발급:
```bash
# ~/.naver-cafe-api 파일 생성 (네이버 개발자 센터에서 앱 등록 필요)
echo 'NAVER_CLIENT_ID=xxx' > ~/.naver-cafe-api
echo 'NAVER_CLIENT_SECRET=xxx' >> ~/.naver-cafe-api
chmod 600 ~/.naver-cafe-api

# OAuth 인증 (브라우저 열림)
python3 scripts/naver_auth.py
```

### 4. 실행
```bash
bash scripts/auto-analyze.sh
```

## 카테고리 분포 (정보관리기술사 출제분야)

기출 분석(110~138회, 1457문제) 기반:

| 카테고리 | 기출 비중 | RSS 키워드 수 |
|---------|----------|--------------|
| 시스템구조 | 19% | 3개 |
| AI데이터분석 | 19% | 3개 |
| IT경영 | 10% | 2개 |
| 소프트웨어공학 | 8% | 2개 |
| 정보보안 | 8% | 1개 |
| 네트워크 | 6% | 1개 |
| 신기술융합 | 4% | 1개 |
| 데이터베이스 | 2% | 1개 |

## 주의사항

### ⚠️ 카페 테스트는 itposecret에서만
- 본번: `kpcitpe` (clubid: 19133896, menuid: 150) — 공용 게시판
- 테스트: `itposecret` (clubid: 30600947, menuid: 1)

### ⚠️ Claude 인증
- 일반 OAuth: 8~12시간 만료
- `claude setup-token`: 1년 유효 (자동화 필수)

### ⚠️ 네이버 카페 API
- **이중 URL 인코딩** 필수 (한글 깨짐 방지)
- 본문 이중인코딩 후 ~4000자 제한
- 카테고리는 8개 중 1개만 (Chirpy가 복수 카테고리를 부모-자식 계층으로 해석)

### ⚠️ 포스트 내부 링크
- 잘못된 형식: `[제목](2026-MM-DD-제목.md)` → 404
- 올바른 형식: `[제목](/tech-engineer-blog/posts/슬러그/)`
- `fix_links.py`가 자동 변환

## 운영 명령어

```bash
# 매일 수동 실행
bash scripts/auto-analyze.sh

# 로그 확인
cat ~/.tech-engineer-blog-auto.log | tail -30

# GitHub Actions 상태
gh run list --workflow="Daily News Fetch"

# 카페 토큰 만료 시
python3 scripts/naver_auth.py
```

## 자동화 시도와 결과

| 방식 | 결과 |
|------|------|
| crontab + claude -p | ❌ 키체인 접근 불가, 인증 실패 |
| launchd | ❌ Claude OAuth 토큰 만료 시 실패 |
| 백그라운드 스크립트 (sleep 루프) | ❌ Mac 잠자기 시 sleep 카운트 안 됨 |
| **수동 실행 (현재 방식)** | ✅ 안정적, Claude Code 세션에서 직접 실행 |
| 원격 제어 (`/remote-control`) | ✅ 폰에서 같은 세션 접근 가능 |
