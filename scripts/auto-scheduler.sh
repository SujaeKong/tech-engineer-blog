#!/bin/bash
# 매일 08:00에 자동 분석을 실행하는 상주 스크립트
# 현재 로그인 세션에서 실행되므로 인증 문제 없음
#
# 실행: nohup ~/tech-engineer-blog/scripts/auto-scheduler.sh &
# 중지: kill $(cat ~/.tech-engineer-blog-scheduler.pid)

BLOG_DIR="$HOME/tech-engineer-blog"
PID_FILE="$HOME/.tech-engineer-blog-scheduler.pid"
LOG_FILE="$HOME/.tech-engineer-blog-auto.log"

echo $$ > "$PID_FILE"
echo "[$(date)] 스케줄러 시작 (PID: $$)" >> "$LOG_FILE"

while true; do
    # 다음 08:00까지 대기
    NOW=$(date +%s)
    TARGET=$(date -v+1d -j -f "%Y-%m-%d %H:%M:%S" "$(date -v+1d +%Y-%m-%d) 08:00:00" +%s 2>/dev/null)

    # 오늘 08:00이 아직 안 지났으면 오늘로
    TODAY_TARGET=$(date -j -f "%Y-%m-%d %H:%M:%S" "$(date +%Y-%m-%d) 08:00:00" +%s 2>/dev/null)
    if [ "$TODAY_TARGET" -gt "$NOW" ]; then
        TARGET=$TODAY_TARGET
    fi

    WAIT=$((TARGET - NOW))
    echo "[$(date)] 다음 실행까지 ${WAIT}초 대기" >> "$LOG_FILE"
    sleep $WAIT

    # 실행
    echo "[$(date)] 자동 분석 실행 시작" >> "$LOG_FILE"
    cd "$BLOG_DIR"
    bash scripts/auto-analyze.sh >> "$LOG_FILE" 2>&1
    echo "[$(date)] 자동 분석 실행 완료" >> "$LOG_FILE"
done
