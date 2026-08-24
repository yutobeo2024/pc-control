# Ứng dụng Parental Control

Hệ thống kiểm soát máy tính con cái: máy con bị khóa cho tới khi phụ huynh duyệt từ Web App trên điện thoại.

## Tính năng

### 1. Xác thực Mở máy
- Con bật máy tính → Màn hình khóa hiện: "Đang chờ phụ huynh cho phép..."
- Web App phụ huynh hiện yêu cầu + thông báo trình duyệt → Bấm "Cho phép" hoặc "Từ chối"
- Nếu approve → Máy tính mở khóa (không giới hạn thời gian)
- Nếu reject → Máy vẫn khóa, client tự gửi lại yêu cầu sau một khoảng chờ

### 2. Khóa theo lịch
- Phụ huynh chọn: Khóa ngay / sau 30p / 1h / 1.5h / 2h / 3h
- Đồng hồ đếm ngược hiển thị trên màn hình con
- Hết giờ → Tự động khóa máy

### 3. Điều khiển Từ xa
- Xem con đang dùng máy hay không (trạng thái online theo heartbeat)
- Khóa máy ngay lập tức từ điện thoại
- Thông báo qua Slack (tùy chọn)

### 4. Mở khóa khẩn cấp
- Hotkey `Ctrl+Shift+Alt+U` + mật khẩu admin, dùng khi web app / Firebase gặp sự cố

## Kiến trúc

```
[Máy tính con]          [Firebase RTDB]          [Web App phụ huynh]
      |                       |                          |
   Bật máy  ------------->  Request  ------------>  Thông báo
      |                       |                          |
   Chờ...  <-------------  Pending  <------------   Approve
      |                       |                          |
   Mở khóa <-------------  Unlock                        |
      |                       |                          |
   Heartbeat ----------->  lastActive ---------->   Online/Offline
      |                       |                          |
   Đếm giờ / lockScheduled    |                     Theo dõi
      |                       |                          |
   Hết giờ ------------->  Locked  -------------->  Thông báo
```

Không có backend riêng — Firebase Realtime Database làm kênh trung gian.
Windows client **polling** mỗi 2 giây (không dùng stream).

## Tech Stack

### Máy tính con (Windows)
- **Python 3.8+**
- **PyQt5** — Giao diện lock screen, timer widget, system tray
- **pyrebase4** — Kết nối Firebase Realtime Database
- **ctypes / Win32 API** — Chặn phím tắt (Alt+Tab, Win, Alt+F4…) khi đang khóa

### Backend
- **Firebase Realtime Database** — Lưu trữ trạng thái, đồng bộ real-time
- **Firebase Security Rules** — Kiểm soát truy cập phía server
- Không cần tự code server

### Web App phụ huynh
- **HTML5 / CSS3 / Vanilla JavaScript** (không build step)
- **Firebase SDK v10** (modular) — Auth + Realtime Database
- **Google Sign-In** với whitelist email trong Security Rules
- **Service Worker** — Thông báo trình duyệt kèm nút Cho phép / Từ chối
- Deploy trên **Netlify**

## Cấu trúc Dự án

```
yuto-control/
├── windows-client/          # Windows client (Python)
│   ├── main.py              # Entry point, vòng lặp polling
│   ├── lock_screen.py       # Màn hình khóa + màn hình đã duyệt
│   ├── timer_widget.py      # Đồng hồ đếm ngược + cảnh báo
│   ├── firebase_handler.py  # Đọc/ghi Firebase
│   ├── emergency_dialog.py  # Dialog mở khóa khẩn cấp
│   ├── input_blocker.py     # Chặn phím tắt Windows khi khóa
│   ├── single_instance.py   # Chống chạy nhiều instance
│   ├── slack_notifier.py    # Thông báo Slack
│   ├── config.example.py    # Mẫu cấu hình (copy thành config.py)
│   └── requirements.txt
│
├── web-app/                 # Web app phụ huynh
│   └── public/
│       ├── index.html       # UI + Firebase init + Google Auth
│       ├── app.js           # Logic duyệt / khóa / dọn request
│       ├── notifications.js # Thông báo qua Service Worker
│       ├── sw.js            # Service Worker
│       └── styles.css
│
├── firebase/
│   ├── database.rules.json  # Security Rules (nguồn duy nhất)
│   └── README.md            # Hướng dẫn setup Firebase
│
└── README.md
```

## Cài đặt

### 1. Setup Firebase
Xem chi tiết trong [`firebase/README.md`](firebase/README.md).
- Tạo project trên [Firebase Console](https://console.firebase.google.com)
- Enable Realtime Database
- Enable Authentication → Google provider
- Dán nội dung `firebase/database.rules.json` vào tab Rules → Publish

### 2. Windows Client
```bash
cd windows-client
pip install -r requirements.txt
copy config.example.py config.py     # rồi sửa FIREBASE_CONFIG và mật khẩu
python main.py
```

Bật auto-start: chuột phải `setup_autostart.bat` → Run as administrator.

### 3. Web App
Deploy thư mục `web-app/public/` lên Netlify (xem `web-app/NETLIFY-DEPLOY.md`),
rồi thêm domain vào Firebase Console → Authentication → Authorized domains.

## Database Schema (Firebase)

```json
{
  "devices": {
    "device_id_123": {
      "status": "locked | unlocked | pending",
      "timeLimit": 7200,
      "timeRemaining": 3600,
      "lockScheduled": 1234567890000,
      "lastActive": 1234567890,
      "deviceName": "PC-CON",
      "createdAt": 1234567890
    }
  },
  "requests": {
    "request_id_789": {
      "deviceId": "device_id_123",
      "type": "unlock_request",
      "timestamp": 1234567890,
      "status": "pending | approved | rejected",
      "deviceName": "PC-CON"
    }
  }
}
```

`timeRemaining` bị **xóa khỏi database** (set `null`) khi mở khóa không giới hạn thời gian.

Request đã xử lý được client xóa ngay sau khi đọc, nên nhánh `requests/`
chỉ giữ tối đa một vài node. Web app cũng tự dọn các request quá hạn.

## Bảo mật

- Whitelist email nằm trong Firebase Security Rules (server-side), không lộ trong frontend
- Mật khẩu mở khóa khẩn cấp lưu dạng **SHA-256 hash** trong `config.py` (file này được gitignore)
- Mỗi thiết bị có Device ID duy nhất (UUID lưu tại `device_id.txt`)

⚠️ **Hạn chế đã biết:** Security Rules hiện cho phép `auth == null` đọc/ghi
để Windows client (không đăng nhập) hoạt động được. Điều này khiến bất kỳ ai
biết `databaseURL` cũng ghi được vào database. Xem `SECURITY-SUMMARY.md`.

⚠️ Lock screen là "khóa mềm": chặn được phím tắt thông thường nhưng **không**
chặn được `Ctrl+Alt+Del` → Task Manager → kill process. Muốn chặn triệt để cần
chạy dưới dạng Windows Service hoặc dùng Group Policy.

## License

MIT License
