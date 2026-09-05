"""
Mẫu cấu hình cho Windows Client.

Cách dùng:
    copy config.example.py config.py
rồi sửa các giá trị bên dưới. File `config.py` đã được .gitignore nên
không bị commit lên GitHub.
"""

# ---------------------------------------------------------------- Firebase --
# Lấy từ Firebase Console > Project settings > Your apps > Web app
FIREBASE_CONFIG = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "your-project.firebaseapp.com",
    "databaseURL": "https://your-project-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "your-project",
    "storageBucket": "your-project.firebasestorage.app",
    "messagingSenderId": "000000000000",
    "appId": "1:000000000000:web:0000000000000000000000"
}

# ID thiết bị (UUID được tạo tự động ở lần chạy đầu)
DEVICE_ID_FILE = "device_id.txt"

# ------------------------------------------------------------------- Timing --
CHECK_INTERVAL = 2000       # ms  - tần suất kiểm tra Firebase
HEARTBEAT_INTERVAL = 5      # giây - tần suất cập nhật lastActive (báo online)
REJECT_RETRY_DELAY = 30     # giây - chờ bao lâu trước khi gửi lại yêu cầu sau khi bị từ chối
WARNING_TIME = 600          # giây - cảnh báo khi còn 10 phút

# -------------------------------------------------------- Emergency unlock --
# Hotkey Ctrl+Shift+Alt+U - dùng khi webapp/Firebase gặp sự cố.
# Luôn bật để tránh bị khóa vĩnh viễn.
EMERGENCY_UNLOCK_ENABLED = True

# Mật khẩu lưu dạng SHA-256 hash, KHÔNG lưu plaintext.
# Tạo hash mới bằng:  python set_password.py
# (giá trị mặc định bên dưới là hash của "admin123" - ĐỔI NGAY!)
EMERGENCY_UNLOCK_PASSWORD_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

# Fallback plaintext cho cấu hình cũ. Để rỗng nếu đã dùng hash ở trên.
EMERGENCY_UNLOCK_PASSWORD = ""

# --------------------------------------------------------------- Bảo vệ UI --
# Chặn Alt+Tab / phím Windows / Alt+F4 / Ctrl+Esc khi màn hình khóa đang hiện.
# Lưu ý: KHÔNG chặn được Ctrl+Alt+Del (Windows bảo lưu tổ hợp này).
BLOCK_SYSTEM_HOTKEYS = True

# Chỉ cho phép chạy một instance duy nhất
SINGLE_INSTANCE = True

# Yêu cầu mật khẩu emergency khi thoát app từ system tray
REQUIRE_PASSWORD_TO_EXIT = True

# ------------------------------------------------------- Khóa khi ngủ dậy --
# Cho máy ngủ (sleep/hibernate) thay vì tắt là cách đi vòng qua hệ thống: tiến
# trình không khởi động lại nên không có gì khóa máy. Bật tùy chọn này để coi
# "ngủ dậy" tương đương "bật máy" - phải xin phép lại.
LOCK_ON_WAKE = True

# Ngủ lâu hơn ngần này (giây) thì khóa. 60 = 1 phút, đủ để bỏ qua các lần màn
# hình tắt tạm vài giây mà không phiền.
SLEEP_DETECT_SECONDS = 60
