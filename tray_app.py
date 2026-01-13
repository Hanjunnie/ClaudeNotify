"""
시스템 트레이 애플리케이션
"""
import sys
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction, QPainter, QColor
from PyQt6.QtCore import QObject, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap
from notification_window import NotificationWindow


class TrayApp(QObject):
    """시스템 트레이 애플리케이션"""

    notification_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)

        self.setup_tray_icon()
        self.setup_menu()

        # 알림 신호 연결
        self.notification_requested.connect(self.show_notification)

    def create_icon(self):
        """간단한 아이콘 생성 (Claude Code 로고 대신)"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 배경 원
        painter.setBrush(QColor("#8B5CF6"))
        painter.setPen(QColor("#8B5CF6"))
        painter.drawEllipse(4, 4, 56, 56)

        # 'C' 문자
        painter.setPen(QColor("white"))
        from PyQt6.QtGui import QFont
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), 0x84, "C")  # AlignCenter

        painter.end()

        return QIcon(pixmap)

    def setup_tray_icon(self):
        """트레이 아이콘 설정"""
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setIcon(self.create_icon())
        self.tray_icon.setToolTip("Claude Code Notifier")
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def setup_menu(self):
        """트레이 메뉴 설정"""
        menu = QMenu()

        # 테스트 알림 액션
        test_action = QAction("테스트 알림 보내기", self.app)
        test_action.triggered.connect(self.test_notification)
        menu.addAction(test_action)

        menu.addSeparator()

        # 정보 액션
        about_action = QAction("정보", self.app)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)

        menu.addSeparator()

        # 종료 액션
        quit_action = QAction("종료", self.app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

    def on_tray_icon_activated(self, reason):
        """트레이 아이콘 클릭 이벤트"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_about()

    def show_notification(self, message: str):
        """알림 표시"""
        notification = NotificationWindow(message)
        notification.show_notification()

        # 트레이 아이콘에도 메시지 표시
        self.tray_icon.showMessage(
            "Claude Code",
            message,
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def test_notification(self):
        """테스트 알림"""
        self.show_notification("작업이 완료되었습니다!")

    def show_about(self):
        """정보 표시"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Claude Code Notifier",
            "Claude Code의 작업 완료 및 응답을 알려주는 알림 애플리케이션입니다.\n\n"
            "버전: 1.0.0\n"
            "크로스 플랫폼 지원: Windows, macOS"
        )

    def quit_app(self):
        """애플리케이션 종료"""
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        """애플리케이션 실행"""
        self.tray_icon.show()
        return self.app.exec()
