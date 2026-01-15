"""
REST API 서버 - Hook 스크립트로부터 알림을 수신
"""
import threading
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Callable, Optional


class NotificationRequest(BaseModel):
    """알림 요청 모델"""
    title: str = "Claude Code"
    message: str
    type: str = "info"


class APIServer:
    """FastAPI 기반 알림 서버"""

    DEFAULT_PORT = 19876

    def __init__(self, callback: Callable[[str, str, str], None], port: int = DEFAULT_PORT):
        """
        Args:
            callback: 알림 수신 시 호출 (title, message, notification_type)
            port: 수신 포트
        """
        self.callback = callback
        self.port = port
        self.app = FastAPI(title="Claude Notifier API")
        self.server: Optional[uvicorn.Server] = None
        self.thread: Optional[threading.Thread] = None

        self._setup_routes()

    def _setup_routes(self):
        """API 라우트 설정"""
        @self.app.get("/health")
        async def health_check():
            return {"status": "ok"}

        @self.app.post("/notify")
        async def notify(request: NotificationRequest):
            """알림 전송"""
            if not request.message:
                raise HTTPException(status_code=400, detail="message is required")

            self.callback(request.title, request.message, request.type)
            return {"status": "sent", "message": request.message}

    def start(self):
        """서버 시작 (백그라운드 스레드)"""
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="warning"
        )
        self.server = uvicorn.Server(config)

        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()

        print(f"REST API 서버 시작됨 (포트: {self.port})")
        print(f"  - Health: http://localhost:{self.port}/health")
        print(f"  - Notify: POST http://localhost:{self.port}/notify")

    def stop(self):
        """서버 중지"""
        if self.server:
            self.server.should_exit = True
        if self.thread:
            self.thread.join(timeout=2)
        print("REST API 서버 중지됨")


# 하위 호환성을 위한 별칭
IPCServer = APIServer
