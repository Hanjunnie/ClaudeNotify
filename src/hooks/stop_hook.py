#!/usr/bin/env python3
"""
Claude Code Hook - 작업 완료 이벤트 처리
Stop hook: Claude Code가 응답을 완료했을 때 호출
"""
import json
import sys
from common import send_notification


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)

    # stop_hook_active 체크 (무한 루프 방지)
    if input_data.get("stop_hook_active"):
        sys.exit(0)

    send_notification(title="작업 완료",message="Claude Code가 응답을 완료했습니다",notification_type="complete")

    sys.exit(0)


if __name__ == "__main__":
    main()
