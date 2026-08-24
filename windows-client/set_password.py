"""
Đổi mật khẩu Emergency Unlock.

Chạy:  python set_password.py

Script sẽ hỏi mật khẩu mới, tính SHA-256 hash và ghi thẳng vào config.py.
Mật khẩu plaintext KHÔNG bao giờ được lưu xuống đĩa.
"""

import getpass
import os
import re
import sys

from password_util import hash_password

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")


def write_hash(new_hash):
    """Cập nhật EMERGENCY_UNLOCK_PASSWORD_HASH trong config.py"""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if "EMERGENCY_UNLOCK_PASSWORD_HASH" in content:
        content = re.sub(
            r'^EMERGENCY_UNLOCK_PASSWORD_HASH\s*=\s*".*"$',
            f'EMERGENCY_UNLOCK_PASSWORD_HASH = "{new_hash}"',
            content,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        content += f'\nEMERGENCY_UNLOCK_PASSWORD_HASH = "{new_hash}"\n'

    # Xóa plaintext còn sót lại từ cấu hình cũ
    content = re.sub(
        r'^EMERGENCY_UNLOCK_PASSWORD\s*=\s*".*"$',
        'EMERGENCY_UNLOCK_PASSWORD = ""',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    if not os.path.exists(CONFIG_FILE):
        print("❌ Không tìm thấy config.py")
        print("   Hãy copy config.example.py thành config.py trước.")
        return 1

    print("=== Đổi mật khẩu Emergency Unlock ===\n")

    password = getpass.getpass("Mật khẩu mới: ")
    if len(password) < 6:
        print("❌ Mật khẩu phải có ít nhất 6 ký tự")
        return 1

    confirm = getpass.getpass("Nhập lại: ")
    if password != confirm:
        print("❌ Hai lần nhập không khớp")
        return 1

    write_hash(hash_password(password))
    print("\n✅ Đã cập nhật mật khẩu trong config.py")
    print("   Khởi động lại app để áp dụng.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
