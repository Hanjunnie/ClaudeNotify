#!/usr/bin/env python3
"""
알림 테스트 스크립트
"""
import sys
from PyQt6.QtWidgets import QApplication
from notification_window import NotificationWindow

def test_notification():
    """알림 창 테스트"""
    app = QApplication(sys.argv)

    # Yes 응답 알림 테스트
    notification = NotificationWindow("Yes 응답 감지!")
    notification.show_notification()

    sys.exit(app.exec())

if __name__ == "__main__":
    test_notification()
