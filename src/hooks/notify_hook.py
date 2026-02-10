#!/usr/bin/env python3
"""
Claude Code Hook - 알림 이벤트 처리
Notification hook: idle_prompt, permission_prompt 등을 처리
"""
import json
import sys
from common import send_notification


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)

    notification_type = input_data.get("notification_type", "")
    message = input_data.get("message", "")

    if notification_type == "idle_prompt":
        send_notification(title="Claude Code 대기 중", message="입력을 기다리고 있습니다", notification_type="idle")
    elif notification_type == "permission_prompt":
        send_notification(title="권한 요청",message=message or "Claude Code가 권한을 요청합니다", notification_type="permission")
    elif notification_type == "elicitation_dialog":
        send_notification(title="선택 필요",message=message or "사용자 입력이 필요합니다", notification_type="input")
    else:
        if message:
            send_notification(title="Claude Code",message=message,notification_type="info")

    sys.exit(0)


if __name__ == "__main__":
    main()
