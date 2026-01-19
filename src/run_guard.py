"""
RunGuard - 중복 실행 방지 모듈

PID 파일을 사용하여 애플리케이션의 중복 실행을 방지합니다.
"""
import os
import sys
import atexit
from pathlib import Path


class RunGuard:
    """애플리케이션 중복 실행 방지 클래스"""
    def __init__(self, app_name: str = "claude_notifier"):
        self.app_name = app_name
        self._pid_file = self._get_pid_file_path()
        self._locked = False

    def _get_pid_file_path(self) -> Path:
        if sys.platform == "win32":
            # Windows: %TEMP% 디렉토리 사용
            temp_dir = Path(os.environ.get("TEMP", os.environ.get("TMP", ".")))
        else:
            # Linux/Mac: /tmp 또는 XDG_RUNTIME_DIR 사용
            runtime_dir = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
            temp_dir = Path(runtime_dir)

        return temp_dir / f"{self.app_name}.pid"

    def _is_process_running(self, pid: int) -> bool:
        if sys.platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        else:
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False

    def is_already_running(self) -> bool:
        if not self._pid_file.exists():
            return False

        try:
            pid = int(self._pid_file.read_text().strip())
            if self._is_process_running(pid):
                return True
            self._pid_file.unlink()
            return False
        except (ValueError, OSError):
            try:
                self._pid_file.unlink()
            except OSError:
                pass
            return False

    def acquire(self) -> bool:
        if self.is_already_running():
            return False

        try:
            self._pid_file.write_text(str(os.getpid()))
            self._locked = True
            atexit.register(self.release)
            return True
        except OSError as e:
            print(f"PID 파일 생성 실패: {e}", file=sys.stderr)
            return False

    def release(self):
        """락 해제 (PID 파일 삭제)"""
        if self._locked:
            try:
                if self._pid_file.exists():
                    self._pid_file.unlink()
                self._locked = False
            except OSError:
                pass

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"{self.app_name}이(가) 이미 실행 중입니다.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False
