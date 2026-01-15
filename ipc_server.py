"""
IPC 서버 - Hook 스크립트로부터 알림을 수신
"""
import json
import socket
import threading
from typing import Callable, Optional


class IPCServer:
    """Hook 스크립트와 통신하는 소켓 서버"""

    DEFAULT_PORT = 19876

    def __init__(self, callback: Callable[[str, str, str], None], port: int = DEFAULT_PORT):
        """
        Args:
            callback: 알림 수신 시 호출 (title, message, notification_type)
            port: 수신 포트
        """
        self.callback = callback
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """서버 시작"""
        if self.running:
            return

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("127.0.0.1", self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # accept 타임아웃
            self.running = True

            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()

            print(f"IPC 서버 시작됨 (포트: {self.port})")
        except OSError as e:
            print(f"IPC 서버 시작 실패: {e}")
            self.running = False

    def _listen_loop(self):
        """클라이언트 연결 수신 루프"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                ).start()
            except socket.timeout:
                continue
            except OSError:
                break

    def _handle_client(self, client_socket: socket.socket):
        """클라이언트 요청 처리"""
        try:
            data = client_socket.recv(4096)
            if data:
                try:
                    payload = json.loads(data.decode("utf-8"))
                    title = payload.get("title", "Claude Code")
                    message = payload.get("message", "")
                    notification_type = payload.get("type", "info")

                    if message:
                        self.callback(title, message, notification_type)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"클라이언트 처리 오류: {e}")
        finally:
            client_socket.close()

    def stop(self):
        """서버 중지"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass
        if self.thread:
            self.thread.join(timeout=2)
        print("IPC 서버 중지됨")
