# tech-engineer-blog

정보관리기술사 관점으로 뉴스를 분석해 블로그 포스트 + 네이버 카페 글을 자동 생성하는 Jekyll(Chirpy) 블로그.
전체 아키텍처와 PC 셋업 방법은 [SETUP.md](SETUP.md) 참고.

## 트리거: "수동작업가자"

사용자가 **"수동작업가자"** (또는 "수동작업", "오늘 작업 가자" 등 같은 의도)라고 하면,
아래 파이프라인을 실행한다 — 리포 루트에서:

```bash
bash scripts/auto-analyze.sh
```

`auto-analyze.sh`가 하는 일 (자세한 건 스크립트 주석 참고):
1. `git checkout -- . && git clean -fd && git pull` — GitHub Actions가 수집한 `_data/news_raw.json` 최신본 받기
2. `claude -p`로 뉴스 분석 → 카테고리 부족분 우선으로 포스트 3개 작성 → 오늘의 토픽을 `_data/today_topic.txt`에 저장 → commit + push
3. 로그: `~/.tech-engineer-blog-auto.log`

**링크 수정 + 카페 게시는 로컬이 아니라 CI가 전담한다.** 2단계에서 `today_topic.txt`가 push되면
GitHub Actions(`.github/workflows/cafe-post.yml`)가 자동으로:
- `scripts/fix_links.py` — 깨진 내부 링크 자동 수정 후 커밋
- `scripts/post_to_cafe.py` — 오늘의 토픽을 네이버 카페에 게시

를 수행한다. 로컬(맥)에서 돌리든 웹/클라우드에서 돌리든 **카페 게시는 CI 단일 경로로만** 일어나므로
이중 게시가 없다. 웹/클라우드 컨테이너는 naver.com 접속이 막혀 있어도 CI가 GitHub 서버에서 게시하므로 문제없다.
CI는 네이버 인증을 저장소 Secrets(`NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` / `NAVER_REFRESH_TOKEN`)에서 읽는다.

### 실행 전 확인할 것
- **경로 독립적**: 스크립트는 자기 위치 기준으로 리포 루트를 잡으므로 어디에 clone해도 동작한다.
- **이 기계의 1회성 세팅이 됐는지 확인** (없으면 사용자에게 안내):
  - Claude 토큰: `~/.claude/.credentials.json` (없으면 `claude setup-token`)
  - 네이버 카페 토큰: `~/.naver-cafe-api`, `~/.naver-cafe-token` (없으면 `python3 scripts/naver_auth.py` 또는 원본 PC에서 복사)
  - `gh auth status` 로 GitHub 인증
- **중첩 실행 주의**: 스크립트가 내부에서 `claude -p` 하위 세션을 띄운다. 이미 Claude 세션 안에서 돌릴 때는 이 점을 사용자에게 알리고, 필요하면 스크립트 대신 단계를 직접 수행해도 된다.

## 포스트 작성 규칙 (직접 작성 시)
- `_posts/YYYY-MM-DD-제목.md`, 구조: 뉴스 요약 → 핵심 개념 → 기술사 출제 포인트 → 관련 토픽 연계
- `categories`는 8개 중 **1개만** (소프트웨어공학/데이터베이스/네트워크/정보보안/IT경영/시스템구조/AI데이터분석/신기술융합)
- 기출 비중 대비 부족 카테고리 우선: 시스템구조 19% > AI데이터분석 19% > IT경영 10% > 소프트웨어공학 8% > 정보보안 8% > 네트워크 6% > 신기술융합 4% > 데이터베이스 2%
- 내부 링크는 Jekyll URL 형식 `[제목](/tech-engineer-blog/posts/슬러그/)` — 파일명(.md) 직접 쓰면 404
- 마크다운 표 위에는 빈 줄, 표 행 사이에는 빈 줄 금지
