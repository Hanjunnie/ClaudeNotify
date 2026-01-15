#!/usr/bin/env python3
"""
Claude Code Hook - 작업 완료 이벤트 처리
Stop hook: Claude Code가 응답을 완료했을 때 호출
"""
import json
import socket
import sys

SOCKET_PORT = 19876


def send_notification(title: str, message: str, notification_type: str = "info"):
    """트레이 앱에 알림 전송"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("127.0.0.1", SOCKET_PORT))

        payload = json.dumps({
            "title": title,
            "message": message,
            "type": notification_type
        })
        sock.sendall(payload.encode("utf-8"))
        sock.close()
        return True
    except (ConnectionRefusedError, socket.timeout):
        return False
    except Exception as e:
        print(f"알림 전송 실패: {e}", file=sys.stderr)
        return False


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)

    # stop_hook_active 체크 (무한 루프 방지)
    if input_data.get("stop_hook_active"):
        sys.exit(0)

    send_notification(
        title="작업 완료",
        message="Claude Code가 응답을 완료했습니다",
        notification_type="complete"
    )

    sys.exit(0)


if __name__ == "__main__":
    main()
