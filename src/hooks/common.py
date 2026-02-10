#!/usr/bin/env python3
"""
Claude Code Hook - 공통 유틸리티 모듈
"""
import json
import urllib.request
import urllib.error

API_PORT = 19876


def get_server_host() -> str:
    """서버 호스트 주소 반환 (WSL 환경 고려)"""
    import subprocess
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            parts = result.stdout.split()
            if "via" in parts:
                return parts[parts.index("via") + 1]
    except (FileNotFoundError, IndexError):
        pass
    return "127.0.0.1"


def send_notification(title: str, message: str, notification_type: str = "info") -> bool:
    """REST API로 알림 전송"""
    host = get_server_host()
    url = f"http://{host}:{API_PORT}/notify"

    payload = json.dumps({
        "title": title,
        "message": message,
        "type": notification_type
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=1) as response:
            return response.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False
