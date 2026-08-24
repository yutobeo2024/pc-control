"""
Single Instance Guard - Chặn chạy nhiều bản cùng lúc.

Dùng named mutex của Windows: mutex tự động được giải phóng khi process kết
thúc, kể cả khi bị kill bằng Task Manager, nên không để lại "lock file mồ côi".
"""

import ctypes
import sys

MUTEX_NAME = "Global\\ParentalControlClient_SingleInstance"
ERROR_ALREADY_EXISTS = 183


class SingleInstance:
    """
    Giữ mutex trong suốt vòng đời process.

        guard = SingleInstance()
        if guard.already_running:
            sys.exit(0)
    """

    def __init__(self, name=MUTEX_NAME):
        self.handle = None
        self.already_running = False

        if not sys.platform.startswith("win"):
            # Không phải Windows - bỏ qua, app chỉ chạy trên Windows
            return

        try:
            kernel32 = ctypes.windll.kernel32
            self.handle = kernel32.CreateMutexW(None, ctypes.c_bool(True), name)
            if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
                self.already_running = True
        except Exception as e:
            print(f"⚠️ Không tạo được single-instance mutex: {e}")

    def release(self):
        """Giải phóng mutex (thường không cần gọi - Windows tự dọn)"""
        if self.handle:
            try:
                ctypes.windll.kernel32.ReleaseMutex(self.handle)
                ctypes.windll.kernel32.CloseHandle(self.handle)
            except Exception:
                pass
            self.handle = None
