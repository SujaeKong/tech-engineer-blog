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

수동 실행 (bash scripts/auto-analyze.sh)  — 로컬(맥)/웹(claude.ai/code) 어디서든
  ├─ git pull
  └─ Claude 분석 (claude -p)
      ├─ 포스트 3개 생성 (서로 다른 카테고리, 부족 카테고리 우선)
      ├─ 오늘의 토픽 1개 선정 → _data/today_topic.txt
      └─ git commit + push  ──┐
                             │  today_topic.txt push가 트리거
GitHub Actions (cafe-post.yml)  ◀──┘  ← 링크수정 + 카페게시는 CI가 전담
  ├─ scripts/fix_links.py (깨진 내부 링크 자동 수정 → 커밋)
  └─ scripts/post_to_cafe.py
      ├─ today_topic.txt 읽기
      ├─ 요약 + 출제 포인트 + 원문 링크 조합
      ├─ 이중 URL 인코딩 (한글 깨짐 방지)
      └─ 네이버 카페 API 게시 (인증: 저장소 Secrets)
```

> **왜 카페 게시를 로컬이 아니라 CI가 하나?**
> `auto-analyze.sh`를 웹/클라우드(claude.ai/code)에서 돌리면 컨테이너가 naver.com 접속을 못 해
> 로컬 게시가 실패한다. GitHub Actions 러너는 naver 접속이 되므로 게시를 CI가 전담한다.
> 로컬(맥)에서 돌려도 `today_topic.txt` push가 CI를 트리거해 CI가 게시하므로,
> **어디서 돌리든 카페 게시는 CI 한 경로로만 1번** 일어난다 (로컬+CI 이중 게시 방지).
> CI는 네이버 인증을 저장소 Secrets(`NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` / `NAVER_REFRESH_TOKEN`)에서 읽는다.

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

### 3. GitHub Secrets 등록 (카페 게시용 · 저장소당 1회)
카페 게시는 CI(`cafe-post.yml`)가 전담하므로, 네이버 인증정보를 **저장소 Secrets**에 등록해야 한다.
GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret 에서 3개:
- `NAVER_CLIENT_ID` — 네이버 개발자센터 앱의 Client ID
- `NAVER_CLIENT_SECRET` — 앱의 Client Secret
- `NAVER_REFRESH_TOKEN` — `~/.naver-cafe-token`의 `refresh_token` 값 (아래 4번으로 발급)

> refresh_token은 갱신해도 바뀌지 않아 한 번 등록하면 계속 유효하다.
> 네이버 비밀번호 변경·앱 연동 해제 시에만 재발급 후 갱신하면 된다.

### 4. (선택) 로컬 네이버 토큰 — 수동 테스트용
자동 파이프라인은 위 Secrets만 있으면 되고, 로컬 파일은 `post_to_cafe.py`를 직접 돌려볼 때만 필요하다.
원본 PC에서 두 파일(`~/.naver-cafe-api`, `~/.naver-cafe-token`)을 복사하거나 새로 발급:
```bash
# ~/.naver-cafe-api 파일 생성 (네이버 개발자 센터에서 앱 등록 필요)
echo 'NAVER_CLIENT_ID=xxx' > ~/.naver-cafe-api
echo 'NAVER_CLIENT_SECRET=xxx' >> ~/.naver-cafe-api
chmod 600 ~/.naver-cafe-api

# OAuth 인증 (브라우저 열림) — 여기서 나온 refresh_token을 위 3번 Secret에 등록
python3 scripts/naver_auth.py
```

### 5. 실행
```bash
bash scripts/auto-analyze.sh
```
분석·포스트 push까지 로컬이 하고, 링크수정·카페게시는 push 직후 CI가 자동으로 수행한다.

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
