#!/usr/bin/env python3
"""
Claude Code Notifier - 메인 진입점

Claude Code의 Hook 이벤트를 수신하여 알림을 표시합니다.
"""
import sys
import argparse
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from tray_app import TrayApp
from ipc_server import IPCServer
from run_guard import RunGuard


class NotificationBridge(QObject):
    """IPC 서버와 트레이 앱 사이의 브릿지 (스레드 간 통신)"""
    notification_signal = pyqtSignal(str)


def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="Claude Code Notifier - Claude Code Hook 기반 알림 애플리케이션"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=19876,
        help="IPC 서버 포트 (기본값: 19876)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="테스트 모드로 실행 (즉시 테스트 알림 표시)"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    # 중복 실행 방지
    guard = RunGuard()
    if not guard.acquire():
        print("Claude Code Notifier가 이미 실행 중입니다.", file=sys.stderr)
        return 1

    # 트레이 애플리케이션 초기화
    tray = TrayApp()

    # 브릿지 객체 생성 (스레드 안전한 신호 전달)
    bridge = NotificationBridge()
    bridge.notification_signal.connect(tray.show_notification)

    # IPC 서버 초기화 (Hook 스크립트로부터 알림 수신)
    def on_notification(title: str, message: str, notification_type: str):
        """알림 수신 콜백"""
        display_message = f"[{title}] {message}"
        bridge.notification_signal.emit(display_message)

    ipc_server = IPCServer(callback=on_notification, port=args.port)

    # 테스트 모드
    if args.test:
        print("테스트 모드로 실행 중...")
        QTimer.singleShot(2000, lambda: tray.show_notification("테스트 알림: 작업이 완료되었습니다!"))
        QTimer.singleShot(5000, lambda: tray.show_notification("테스트 알림: 권한 요청 감지"))

    # IPC 서버 시작
    ipc_server.start()

    print("Claude Code Notifier가 시작되었습니다.")
    print("시스템 트레이에서 실행 중입니다.")
    print(f"IPC 서버 포트: {args.port}")
    print("\n[설정 방법]")
    print("~/.claude/settings.json 또는 프로젝트의 .claude/settings.json에")
    print("hooks 설정을 추가하세요. (install-hooks 명령어 참고)")

    # 애플리케이션 실행
    try:
        return tray.run()
    except KeyboardInterrupt:
        print("\n애플리케이션을 종료합니다...")
        ipc_server.stop()
        return 0


if __name__ == "__main__":
    main()
