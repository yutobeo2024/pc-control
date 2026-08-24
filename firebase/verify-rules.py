"""
Kiểm chứng Firebase Security Rules đã publish đúng chưa.

Chạy:
    cd firebase
    python verify-rules.py

Script gửi request KHÔNG kèm token xác thực (giả lập người ngoài) và kiểm tra:

  1. Người ngoài KHÔNG liệt kê được nhánh devices / requests, và root đóng
  2. Windows client (cũng không đăng nhập) VẪN đọc/ghi được node của chính nó

Chỉ dùng thao tác an toàn: GET, PATCH `lastActive` (đúng thứ heartbeat vẫn ghi),
và DELETE trên node probe không tồn tại.

Hai lưu ý khi sửa script này:

* ĐỪNG probe bằng `PATCH <collection>.json` với body rỗng `{}`. Không có child
  nào để ghi thì Firebase chẳng đánh giá rule nào cả và trả 200, tạo ra kết quả
  "được phép" giả.
* Cũng đừng probe bằng `PATCH devices.json` với một child thật: Firebase tách
  nó thành lệnh ghi tại `devices/<child>`, và rule `$deviceId` cho phép -
  đúng thiết kế, không phải lỗ hổng.

Quyền ghi ở mức collection (SET/DELETE cả nhánh) chỉ kiểm tra được bằng thao
tác phá hủy dữ liệu, nên script không probe. Nó dùng **cùng một biểu thức** với
quyền đọc ở mức collection đã được kiểm ở trên.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "windows-client"))

try:
    from config import FIREBASE_CONFIG, DEVICE_ID_FILE
except ImportError:
    print("❌ Không import được windows-client/config.py")
    print("   Copy config.example.py thành config.py trước.")
    sys.exit(1)

DB_URL = FIREBASE_CONFIG["databaseURL"].rstrip("/")

DEVICE_ID_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "windows-client", DEVICE_ID_FILE
)


def request(method, path, body=None):
    """Gửi request KHÔNG kèm token. Trả về (status_code, text)."""
    url = f"{DB_URL}/{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)


def check(label, method, path, body, want_denied):
    """want_denied=True nghĩa là mong đợi bị chặn (401)."""
    status, text = request(method, path, body)
    denied = status in (401, 403)
    ok = denied == want_denied

    icon = "✅" if ok else "❌"
    verdict = "bị chặn" if denied else f"ĐƯỢC PHÉP (HTTP {status})"
    print(f"  {icon} {label}")
    print(f"       {method} /{path} -> {verdict}")

    if not ok:
        expected = "phải BỊ CHẶN" if want_denied else "phải ĐƯỢC PHÉP"
        print(f"       ⚠️  Sai: {expected}")
        if not denied and len(text) < 200:
            print(f"       trả về: {text.strip()}")
    return ok


def main():
    print(f"Database: {DB_URL}\n")

    try:
        with open(DEVICE_ID_PATH) as f:
            device_id = f.read().strip()
    except FileNotFoundError:
        print(f"❌ Không tìm thấy {DEVICE_ID_PATH}")
        print("   Chạy Windows client ít nhất một lần để tạo device ID.")
        return 1

    results = []

    print("── Người ngoài (không đăng nhập) PHẢI bị chặn ──")
    results.append(check(
        "Liệt kê toàn bộ thiết bị",
        "GET", "devices.json?shallow=true", None, want_denied=True))
    results.append(check(
        "Liệt kê toàn bộ request",
        "GET", "requests.json?shallow=true", None, want_denied=True))
    results.append(check(
        "Đọc nhánh không có rule (root phải đóng)",
        "GET", "verify-rules-probe.json", None, want_denied=True))
    results.append(check(
        "Ghi nhánh không có rule (root phải đóng)",
        "PATCH", "verify-rules-probe.json", {"probe": 1}, want_denied=True))

    print("\n── Windows client PHẢI chạy được ──")
    results.append(check(
        "Đọc node thiết bị của mình",
        "GET", f"devices/{device_id}.json", None, want_denied=False))
    results.append(check(
        "Heartbeat lên node của mình",
        "PATCH", f"devices/{device_id}.json",
        {"lastActive": int(time.time())}, want_denied=False))
    results.append(check(
        "Đọc một request lẻ",
        "GET", "requests/verify-rules-probe.json", None, want_denied=False))
    results.append(check(
        "Xóa một request đã xử lý",
        "DELETE", "requests/verify-rules-probe.json", None, want_denied=False))

    passed = sum(results)
    total = len(results)
    print(f"\n{'─' * 50}")

    if passed == total:
        print(f"✅ {passed}/{total} - Rules đã publish đúng.")
        print()
        print("Còn lại cần kiểm tra thủ công:")
        print("  • Mở web app, xem Console không có 'FIREBASE WARNING: Using an")
        print("    unspecified index' -> xác nhận .indexOn đã có hiệu lực")
        print("  • Đăng nhập bằng email lạ -> phải bị từ chối")
        return 0

    print(f"❌ {passed}/{total} - Rules CHƯA đúng.")
    print()
    print("Vào Firebase Console → Realtime Database → Rules,")
    print("dán nội dung firebase/database.rules.json rồi bấm Publish.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
