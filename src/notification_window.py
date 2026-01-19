"""
좌측 하단에 표시되는 알림 창 구현
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt6.QtGui import QFont, QColor


class NotificationWindow(QWidget):
    """좌측 하단에 표시되는 슬라이드 알림 창"""

    def __init__(self, message: str, duration: int = 5000):
        super().__init__()
        self.message = message
        self.duration = duration
        self.setup_ui()
        self.setup_animation()

    def setup_ui(self):
        """UI 초기화"""
        # 윈도우 플래그 설정 (항상 위, 프레임 없음, 태스크바에 표시 안함)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)

        # 타이틀 레이블
        title_label = QLabel("Claude Code")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")

        # 메시지 레이블
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #34495e; padding-top: 5px;")
        message_font = QFont()
        message_font.setPointSize(10)
        message_label.setFont(message_font)

        layout.addWidget(title_label)
        layout.addWidget(message_label)

        # 컨테이너 위젯
        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #bdc3c7;
            }
        """)

        # 그림자 효과
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        container.setGraphicsEffect(shadow)

        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # 크기 설정
        self.setFixedSize(350, 120)

        # 마우스 클릭으로 닫기
        self.mousePressEvent = lambda event: self.close_notification()

    def setup_animation(self):
        """애니메이션 설정"""
        # 화면 크기 가져오기
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()

        # 좌측 하단 위치 계산
        margin = 20
        x_pos = margin
        y_pos = screen.height() - self.height() - margin

        # 시작 위치 (화면 밖 왼쪽)
        self.start_pos = QRect(-self.width(), y_pos, self.width(), self.height())
        # 종료 위치 (화면 안 좌측 하단)
        self.end_pos = QRect(x_pos, y_pos, self.width(), self.height())

        # 슬라이드 인 애니메이션
        self.slide_in_animation = QPropertyAnimation(self, b"geometry")
        self.slide_in_animation.setDuration(500)
        self.slide_in_animation.setStartValue(self.start_pos)
        self.slide_in_animation.setEndValue(self.end_pos)
        self.slide_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 슬라이드 아웃 애니메이션
        self.slide_out_animation = QPropertyAnimation(self, b"geometry")
        self.slide_out_animation.setDuration(400)
        self.slide_out_animation.setStartValue(self.end_pos)
        self.slide_out_animation.setEndValue(self.start_pos)
        self.slide_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.slide_out_animation.finished.connect(self.close)

    def show_notification(self):
        """알림 표시"""
        self.show()
        self.slide_in_animation.start()

        # 일정 시간 후 자동으로 닫기
        QTimer.singleShot(self.duration, self.close_notification)

    def close_notification(self):
        """알림 닫기 애니메이션"""
        if self.slide_out_animation.state() != QPropertyAnimation.State.Running:
            self.slide_out_animation.start()
