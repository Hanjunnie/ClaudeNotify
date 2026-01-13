#!/usr/bin/env python3
"""
Claude Code Notifier - 메인 진입점

Claude Code의 작업 완료 및 Yes 응답을 감지하여 알림을 표시합니다.
"""
import sys
import argparse
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from tray_app import TrayApp
from log_monitor import LogMonitor


class NotificationBridge(QObject):
    """로그 모니터와 트레이 앱 사이의 브릿지"""
    notification_signal = pyqtSignal(str)


def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="Claude Code Notifier - Claude Code 작업 완료 알림 애플리케이션"
    )
    parser.add_argument(
        "--log-path",
        type=str,
        help="모니터링할 Claude Code 로그 파일 또는 디렉토리 경로"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="테스트 모드로 실행 (즉시 테스트 알림 표시)"
    )
    return parser.parse_args()


def main():
    """메인 함수"""
    args = parse_arguments()

    # 트레이 애플리케이션 초기화
    tray = TrayApp()

    # 브릿지 객체 생성
    bridge = NotificationBridge()

    # 브릿지 신호를 트레이 앱의 알림 요청 신호에 연결
    bridge.notification_signal.connect(tray.show_notification)

    # 로그 모니터 초기화
    log_monitor = LogMonitor(
        callback=lambda msg: bridge.notification_signal.emit(msg),
        log_path=args.log_path
    )

    # 테스트 모드
    if args.test:
        print("테스트 모드로 실행 중...")
        # 2초 후 테스트 알림 표시
        QTimer.singleShot(2000, lambda: tray.show_notification("테스트 알림: 작업이 완료되었습니다!"))
        QTimer.singleShot(5000, lambda: tray.show_notification("테스트 알림: Yes 응답 감지"))
    else:
        # 로그 모니터링 시작
        log_monitor.start()
        print("Claude Code Notifier가 시작되었습니다.")
        print("시스템 트레이에서 실행 중입니다.")
        if args.log_path:
            print(f"모니터링 경로: {args.log_path}")

    # 애플리케이션 실행
    try:
        sys.exit(tray.run())
    except KeyboardInterrupt:
        print("\n애플리케이션을 종료합니다...")
        log_monitor.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
