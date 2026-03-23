#!/usr/bin/env python3
"""
네이버 카페 API OAuth 토큰 발급 스크립트.

사용법:
    python3 scripts/naver_auth.py

브라우저가 열리면 네이버 로그인 후 권한 동의 → 토큰이 자동 저장됩니다.
"""

import http.server
import os
import subprocess
import sys
import urllib.parse
import webbrowser

# 크리덴셜 로드
creds = {}
with open(os.path.expanduser("~/.naver-cafe-api")) as f:
    for line in f:
        if "=" in line:
            k, v = line.strip().split("=", 1)
            creds[k] = v

CLIENT_ID = creds["NAVER_CLIENT_ID"]
CLIENT_SECRET = creds["NAVER_CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:8080/callback"
TOKEN_FILE = os.path.expanduser("~/.naver-cafe-token")


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    """OAuth 콜백을 처리하는 핸들러."""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("인증 성공! 이 창을 닫으셔도 됩니다.".encode())

            # 토큰 교환
            token_url = "https://nid.naver.com/oauth2.0/token"
            token_params = urllib.parse.urlencode({
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code,
            })
            full_url = f"{token_url}?{token_params}"

            result = subprocess.run(
                ["curl", "-s", full_url],
                capture_output=True, text=True,
            )
            token_data = result.stdout

            import json
            token_json = json.loads(token_data)

            if "access_token" in token_json:
                with open(TOKEN_FILE, "w") as f:
                    json.dump(token_json, f, indent=2)
                os.chmod(TOKEN_FILE, 0o600)
                print(f"\n[SUCCESS] 토큰 저장 완료: {TOKEN_FILE}")
                print(f"  access_token: {token_json['access_token'][:20]}...")
                print(f"  refresh_token: {token_json.get('refresh_token', 'N/A')[:20]}...")
            else:
                print(f"\n[ERROR] 토큰 발급 실패: {token_data}")

            # 서버 종료
            import threading
            threading.Thread(target=self.server.shutdown).start()
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: no code")

    def log_message(self, format, *args):
        pass  # 로그 숨기기


def main():
    # 인증 URL 생성
    auth_url = (
        "https://nid.naver.com/oauth2.0/authorize?"
        + urllib.parse.urlencode({
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "state": "tech-engineer-blog",
        })
    )

    print("[INFO] 브라우저에서 네이버 로그인 후 권한을 동의해주세요.")
    webbrowser.open(auth_url)

    # 콜백 서버 시작
    server = http.server.HTTPServer(("localhost", 8080), CallbackHandler)
    print("[INFO] 콜백 대기 중 (localhost:8080)...")
    server.serve_forever()


if __name__ == "__main__":
    main()
