"""
Path helper - phân giải đường dẫn file đúng cho cả 2 chế độ chạy.

Vấn đề: khi đóng gói thành .exe onefile, PyInstaller giải nén vào một thư mục
tạm (`sys._MEIPASS`) rồi xóa khi thoát. `__file__` của module trỏ vào đó, nên
file ghi cạnh `__file__` sẽ biến mất sau mỗi lần chạy.

`app_dir()` trả về thư mục "bền" để đọc/ghi file cấu hình runtime:
  - Chạy .exe   -> thư mục CHỨA file .exe
  - Chạy python -> thư mục chứa mã nguồn (windows-client)

Dùng cho: device_id.txt, slack_webhook.txt - những file cần tồn tại lâu dài và
nằm cạnh ứng dụng, riêng cho từng máy.
"""

import os
import sys


def is_frozen():
    """True nếu đang chạy từ .exe do PyInstaller đóng gói"""
    return getattr(sys, "frozen", False)


def app_dir():
    """Thư mục bền cạnh ứng dụng (chứa .exe, hoặc chứa mã nguồn)"""
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def app_path(filename):
    """Đường dẫn tuyệt đối tới một file cấu hình runtime cạnh ứng dụng"""
    return os.path.join(app_dir(), filename)
