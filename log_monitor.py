"""
Claude Code 로그 모니터링 모듈
"""
import os
import time
import re
from pathlib import Path
from threading import Thread, Event
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class LogMonitor:
    """Claude Code 로그 파일을 모니터링하는 클래스"""

    def __init__(self, callback: Callable[[str], None], log_path: Optional[str] = None):
        """
        Args:
            callback: 이벤트 감지 시 호출될 콜백 함수
            log_path: 모니터링할 로그 파일 또는 디렉토리 경로
        """
        self.callback = callback
        self.log_path = log_path
        self.stop_event = Event()
        self.observer = None
        self.file_position = 0

        # 감지할 패턴들
        self.patterns = [
            (re.compile(r'\bYes\b', re.IGNORECASE), "Yes 응답 감지"),
            (re.compile(r'completed|finished|done', re.IGNORECASE), "작업 완료 감지"),
            (re.compile(r'successfully', re.IGNORECASE), "성공적으로 완료"),
            (re.compile(r'✓|✔', re.UNICODE), "체크마크 감지 (완료)"),
            (re.compile(r'AskUserQuestion', re.IGNORECASE), "사용자 선택 요청"),
            (re.compile(r'질문|선택하세요|옵션을 선택', re.IGNORECASE), "선택지 제시"),
        ]

    def detect_event(self, text: str) -> Optional[str]:
        """텍스트에서 이벤트 패턴 감지"""
        for pattern, message in self.patterns:
            if pattern.search(text):
                return message
        return None

    def monitor_file(self, file_path: str):
        """파일 모니터링 (tail -f 방식)"""
        try:
            # 파일이 존재하지 않으면 생성될 때까지 대기
            while not os.path.exists(file_path) and not self.stop_event.is_set():
                time.sleep(1)

            if self.stop_event.is_set():
                return

            # 파일 끝으로 이동
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(0, os.SEEK_END)
                self.file_position = f.tell()

                while not self.stop_event.is_set():
                    line = f.readline()
                    if line:
                        # 새로운 줄 발견
                        event_message = self.detect_event(line)
                        if event_message:
                            self.callback(f"{event_message}: {line.strip()[:100]}")
                    else:
                        # 새로운 내용이 없으면 대기
                        time.sleep(0.5)
                        # 파일이 잘렸는지 확인 (로그 로테이션)
                        current_size = os.path.getsize(file_path)
                        if current_size < self.file_position:
                            f.seek(0)
                            self.file_position = 0

        except Exception as e:
            print(f"파일 모니터링 오류: {e}")

    def start_file_monitoring(self, file_path: str):
        """파일 모니터링 시작"""
        monitor_thread = Thread(target=self.monitor_file, args=(file_path,), daemon=True)
        monitor_thread.start()

    def start_directory_monitoring(self, directory: str):
        """디렉토리 내 로그 파일 모니터링"""
        class LogFileHandler(FileSystemEventHandler):
            def __init__(self, parent):
                self.parent = parent

            def on_modified(self, event):
                if not event.is_directory and event.src_path.endswith('.log'):
                    self.parent.process_file_change(event.src_path)

        handler = LogFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(handler, directory, recursive=False)
        self.observer.start()

    def process_file_change(self, file_path: str):
        """파일 변경 처리"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 마지막 위치부터 읽기
                f.seek(self.file_position)
                new_content = f.read()
                self.file_position = f.tell()

                if new_content:
                    event_message = self.detect_event(new_content)
                    if event_message:
                        # 첫 100자만 표시
                        preview = new_content.strip()[:100]
                        self.callback(f"{event_message}: {preview}")
        except Exception as e:
            print(f"파일 처리 오류: {e}")

    def start(self):
        """모니터링 시작"""
        if self.log_path:
            if os.path.isfile(self.log_path):
                self.start_file_monitoring(self.log_path)
            elif os.path.isdir(self.log_path):
                self.start_directory_monitoring(self.log_path)
            else:
                print(f"경로를 찾을 수 없습니다: {self.log_path}")
        else:
            # 기본 Claude Code 로그 경로 추측
            self.find_and_monitor_default_logs()

    def find_and_monitor_default_logs(self):
        """기본 Claude Code 로그 위치 찾기"""
        possible_paths = [
            Path.home() / ".claude" / "logs",
            Path.home() / "Library" / "Application Support" / "Claude" / "logs",  # macOS
            Path.home() / "AppData" / "Local" / "Claude" / "logs",  # Windows
        ]

        for path in possible_paths:
            if path.exists():
                print(f"로그 디렉토리 발견: {path}")
                self.start_directory_monitoring(str(path))
                return

        print("기본 로그 경로를 찾을 수 없습니다. --log-path 옵션으로 경로를 지정해주세요.")

    def stop(self):
        """모니터링 중지"""
        self.stop_event.set()
        if self.observer:
            self.observer.stop()
            self.observer.join()
