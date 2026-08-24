"""
Input Blocker - Chặn phím tắt hệ thống khi màn hình khóa đang hiện.

Dùng low-level keyboard hook (WH_KEYBOARD_LL) để nuốt các tổ hợp cho phép
thoát khỏi lock screen:

    Alt+Tab, Alt+Esc, Ctrl+Esc, Alt+F4, phím Windows (trái/phải)

⚠️ GIỚI HẠN: Không chặn được Ctrl+Alt+Del - Windows bảo lưu tổ hợp này ở mức
Secure Attention Sequence, chỉ Group Policy hoặc credential provider mới can
thiệp được. Nghĩa là vẫn có thể vào Task Manager và kill process. Đây là "khóa
mềm", không phải kiosk mode thật.

Hook cần một message loop đang chạy - Qt event loop đáp ứng điều kiện này, nên
module chỉ hoạt động khi được cài đặt từ luồng chính của app.
"""

import ctypes
import sys
from ctypes import wintypes

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104

VK_TAB = 0x09
VK_ESCAPE = 0x1B
VK_F4 = 0x73
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_CONTROL = 0x11

LLKHF_ALTDOWN = 0x20


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


HOOKPROC = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)


class InputBlocker:
    """
    Bật/tắt việc chặn phím tắt hệ thống.

        blocker = InputBlocker()
        blocker.enable()   # khi hiện lock screen
        blocker.disable()  # khi mở khóa
    """

    def __init__(self):
        self._hook = None
        self._proc = None  # phải giữ tham chiếu, nếu không callback bị GC
        self._user32 = None
        self._kernel32 = None

        if not sys.platform.startswith("win"):
            return

        self._user32 = ctypes.WinDLL("user32", use_last_error=True)
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        self._user32.SetWindowsHookExW.argtypes = [
            ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD
        ]
        self._user32.SetWindowsHookExW.restype = ctypes.c_void_p

        self._user32.CallNextHookEx.argtypes = [
            ctypes.c_void_p, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
        ]
        self._user32.CallNextHookEx.restype = ctypes.c_long

        self._user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]
        self._user32.UnhookWindowsHookEx.restype = wintypes.BOOL

        self._kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        self._kernel32.GetModuleHandleW.restype = wintypes.HMODULE

    @property
    def is_enabled(self):
        return self._hook is not None

    def _should_block(self, vk_code, flags):
        """Quyết định có nuốt phím này không"""
        alt_down = bool(flags & LLKHF_ALTDOWN)
        ctrl_down = bool(self._user32.GetAsyncKeyState(VK_CONTROL) & 0x8000)

        # Phím Windows - mở Start menu / Win+D / Win+R ...
        if vk_code in (VK_LWIN, VK_RWIN):
            return True

        # Alt+Tab - chuyển sang cửa sổ khác
        if vk_code == VK_TAB and alt_down:
            return True

        # Alt+Esc / Ctrl+Esc - đưa lock screen xuống dưới, mở Start menu
        if vk_code == VK_ESCAPE and (alt_down or ctrl_down):
            return True

        # Alt+F4 - đóng cửa sổ
        if vk_code == VK_F4 and alt_down:
            return True

        return False

    def _hook_callback(self, n_code, w_param, l_param):
        if n_code == 0 and w_param in (WM_KEYDOWN, WM_SYSKEYDOWN):
            try:
                kb = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                if self._should_block(kb.vkCode, kb.flags):
                    return 1  # nuốt phím, không chuyển tiếp
            except Exception:
                pass  # lỗi trong hook không được phép làm sập app

        return self._user32.CallNextHookEx(self._hook, n_code, w_param, l_param)

    def enable(self):
        """Cài hook. An toàn khi gọi nhiều lần."""
        if self._user32 is None or self._hook is not None:
            return False

        self._proc = HOOKPROC(self._hook_callback)
        module = self._kernel32.GetModuleHandleW(None)
        self._hook = self._user32.SetWindowsHookExW(
            WH_KEYBOARD_LL, self._proc, module, 0
        )

        if not self._hook:
            err = ctypes.get_last_error()
            print(f"⚠️ Không cài được keyboard hook (error {err})")
            self._hook = None
            self._proc = None
            return False

        print("🛡️ Đã chặn phím tắt hệ thống (Alt+Tab, Win, Alt+F4, Ctrl+Esc)")
        return True

    def disable(self):
        """Gỡ hook. An toàn khi gọi nhiều lần."""
        if self._hook is None:
            return

        try:
            self._user32.UnhookWindowsHookEx(self._hook)
        except Exception as e:
            print(f"⚠️ Lỗi khi gỡ keyboard hook: {e}")

        self._hook = None
        self._proc = None
        print("🛡️ Đã bỏ chặn phím tắt hệ thống")
