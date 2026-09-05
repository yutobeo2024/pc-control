# Parental Control System - Project Context

## Tổng Quan Dự Án

### Mục đích
Hệ thống Parental Control cho phép phụ huynh kiểm soát việc sử dụng máy tính của
con cái từ xa thông qua Web App trên điện thoại.

### Architecture
```
┌─────────────────────┐
│   Web App           │
│   (Netlify)         │
│   - Google Auth     │
│   - Control Panel   │
│   - Service Worker  │
└──────────┬──────────┘
           │
           │ Firebase Realtime DB
           │ (web: real-time onValue / client: polling 2s)
           │
┌──────────▼──────────┐
│  Windows Client     │
│  (Python/PyQt5)     │
│  - Lock Screen      │
│  - Keyboard hook    │
│  - Auto-start       │
└─────────────────────┘
```

### Tech Stack

**Frontend (Web App):**
- HTML5/CSS3/Vanilla JavaScript (không build step)
- Firebase SDK v10.7.1 (modular)
- Firebase Authentication (Google Sign-In)
- Firebase Realtime Database
- Service Worker (`sw.js`) cho notification có nút bấm
- Deployed on Netlify (`yutokun.netlify.app`)

**Backend:**
- Firebase Realtime Database
- Firebase Security Rules (server-side validation)
- Không có backend riêng

**Windows Client:**
- Python 3.13
- PyQt5 (GUI framework)
- Pyrebase4 (Firebase client, **không đăng nhập**)
- ctypes / Win32 API (keyboard hook, single-instance mutex)
- Windows Task Scheduler (auto-start)

---

## Key Features Đã Implement

### 1. Unlock Logic (KHÔNG giới hạn thời gian)
- **Location:** `web-app/public/app.js:304` (`approveRequest`)
- **Behavior:** Khi phụ huynh bấm "Cho phép", máy mở khóa VÔ THỜI HẠN
- **Implementation:** Set `timeRemaining: null` → Firebase **xóa hẳn key**.
  Client hiểu "không có key" = vô thời hạn (`main.py:196`).

### 2. Multiple Lock Options
- **Location:** `web-app/public/index.html:83-90`
- **Options:** Khóa ngay, sau 30p, 1h, 1.5h, 2h, 3h
- **Implementation:**
  - Frontend: 6 buttons với `data-delay` attribute
  - Backend: `lockScheduled` timestamp (milliseconds)
  - Client: `main.py:393-400`

### 3. Notifications qua Service Worker
- **Location:** `web-app/public/notifications.js` + `web-app/public/sw.js`
- **Features:**
  - Notification có nút **Cho phép** / **Từ chối** bấm trực tiếp
  - Toggle button 🔔 On/Off, test notification khi bật lần đầu
  - Click notification → focus web app
  - Rung trên mobile
  - Tự đóng notification khi request không còn pending (`closeResolved`)
- **Flow:** SW `notificationclick` → `postMessage` → `app.js:347` dispatch
  `notification-action` → `approveRequest` / `rejectRequest`
- **⚠️ Giới hạn:** KHÔNG phải Web Push. Trang web phải đang mở (kể cả tab nền).
  Đóng hẳn trình duyệt = không nhận thông báo. Muốn nhận thật sự cần FCM Web
  Push (VAPID key + backend gửi message).

### 4. Google Authentication
- **Location:** `web-app/public/index.html:168-200`
- **Security:**
  - Email whitelist stored in Firebase Rules (server-side)
  - Frontend tests database access to verify permission
  - NO email exposure in client code

### 5. Firebase Security Rules
- **Location:** `firebase/database.rules.json` (**nguồn duy nhất**)
- **Cấu trúc 2 tầng:**
  - Mức collection (`devices`, `requests`): `auth != null && <email whitelist>`
    → chỉ phụ huynh đã đăng nhập. Người ngoài **không liệt kê, không xóa sạch**
    được.
  - Mức node (`$deviceId`, `$requestId`): thêm `auth == null` → Windows client
    (không đăng nhập) vẫn đọc/ghi được node của nó.
  - Rules Firebase cascade theo hướng **cấp quyền**: rule cha `false` không
    chặn rule con `true`, nên client vẫn chạy bình thường.
- `.indexOn: ["status", "timestamp"]` trên `requests` cho query pending
- **Kiểm chứng:** `python firebase/verify-rules.py` (kỳ vọng 8/8)
- `FIREBASE-RULES-SECURE.json` ở root là bản copy giống hệt, giữ lại vì các
  tài liệu cũ có tham chiếu tới.

### 6. Emergency Unlock
- **Hotkey:** `Ctrl+Shift+Alt+U`
- **Password:** lưu dạng **SHA-256 hash** trong `config.py`
  (`EMERGENCY_UNLOCK_PASSWORD_HASH`)
- **Đổi mật khẩu:** `python set_password.py`
- **Location:**
  - Dialog: `windows-client/emergency_dialog.py`
  - Verify: `windows-client/password_util.py`
  - Handler: `windows-client/main.py:266`
- **Security:** NO hint shown on lock screen. App cảnh báo lúc khởi động nếu
  mật khẩu vẫn là `admin123` mặc định.

### 7. Auto-start with Windows
- **Location:** `windows-client/setup_autostart.bat`
- **Method:** Windows Task Scheduler
- **Features:** Run with highest privileges, hidden console (`pythonw.exe`),
  `WorkingDirectory` được set đúng

### 8. Lock Screen Management
- **Location:** `windows-client/lock_screen.py`
- **Features:**
  - Fullscreen, always on top, không đóng/thu nhỏ được
  - Recreated on each lock (tránh lỗi state)
  - Chặn Alt+Tab / phím Windows / Alt+F4 / Ctrl+Esc qua low-level keyboard
    hook (`input_blocker.py`)
  - Thoát từ system tray cần mật khẩu admin (`main.py:450`)
  - Hiển thị đếm ngược khi bị từ chối (`show_rejected_message`)

### 9. Heartbeat / Online Status
- **Location:** `main.py:319` (`send_heartbeat_if_due`) →
  `firebase_handler.py:send_heartbeat`
- Client cập nhật `lastActive` mỗi `HEARTBEAT_INTERVAL` (5s), độc lập với timer
- Web coi máy online nếu `lastActive` mới hơn `ONLINE_THRESHOLD_SECONDS` (20s),
  `app.js:477`

### 10. Dọn dẹp `requests/`
- Client xóa request ngay sau khi đọc kết quả duyệt/từ chối
  (`firebase_handler.delete_request`)
- Web query chỉ lấy `status == 'pending'` thay vì load cả nhánh (`app.js:53`)
- Web dọn định kỳ các request quá hạn (`cleanupStaleRequests`, `app.js:388`)

### 11. Đóng gói thành `.exe` độc lập (mới ở v1.2)
- **Location:** `windows-client/ParentalControl.spec`, `build-exe.bat`,
  `paths.py`, `setup_autostart_exe.bat`, `BUILD-EXE-GUIDE.md`
- **Mục đích:** máy con chỉ cần **một file `ParentalControl.exe`** — không cài
  Python, không `pip install`. Build một lần rồi copy sang bao nhiêu máy tùy ý.
- **`paths.py` — vì sao cần:** bản onefile của PyInstaller giải nén vào thư mục
  tạm (`sys._MEIPASS`) rồi **xóa khi thoát**, nên file ghi cạnh `__file__` sẽ
  biến mất sau mỗi lần chạy. `app_path()` trả về thư mục chứa `.exe` (hoặc thư
  mục mã nguồn khi chạy bằng python), dùng cho `device_id.txt`
  (`firebase_handler.py:14`) và `slack_webhook.txt` (`slack_notifier.py:12`).
- **Spec:** `console=False` (chạy ngầm, tương đương `pythonw.exe`);
  `hiddenimports` gom submodule của `pyrebase / requests_toolbelt / gcloud /
  oauth2client / Crypto / jwt` vì PyInstaller không dò ra qua chuỗi import động
  — thiếu một cái là exe crash `ModuleNotFoundError` lúc chạy;
  `collect_data_files("gcloud")` kèm các file JSON; loại
  `tkinter / numpy / PIL / PyQt6 / PySide` cho nhẹ (~78 MB).
- **`config.py` bị NHÚNG vào exe** → phải điền `FIREBASE_CONFIG` và chạy
  `set_password.py` **trước** khi build. Đổi cấu hình sau đó = phải build lại.
- **Auto-start bản exe:** `setup_autostart_exe.bat` tạo task Scheduler
  `ParentalControlClient` trỏ vào `ParentalControl.exe` **nằm cùng thư mục** với
  nó. Gỡ vẫn dùng chung `remove_autostart.bat`.
- **⚠️ Chưa từng build** — chưa có `windows-client/dist/`. Xem "Trạng thái hiện
  tại".

### 12. Khóa lại khi máy ngủ dậy (mới ở v1.2.1)
- **Location:** `main.py:check_firebase_updates` (đầu hàm), `config.LOCK_ON_WAKE`
- **Vấn đề:** "khóa khi mở máy" không phải logic riêng — nó chỉ là hệ quả của
  việc tiến trình khởi động lại (`__init__` đặt `is_locked = True`). Task
  Scheduler chỉ có `LogonTrigger`, mà sleep không sinh logon event. Nên **cho
  máy ngủ thay vì tắt là đi vòng qua toàn bộ hệ thống** — không cần Task
  Manager, không cần mật khẩu.
- **Cách phát hiện:** vòng lặp polling chạy mỗi 2 giây; `QTimer` không tick khi
  máy ngủ, nên khoảng cách giữa hai lần chạy nhảy vọt = vừa ngủ dậy.
- **Dùng `time.time()` chứ KHÔNG dùng `time.monotonic()`:** trên Windows
  monotonic không tính thời gian máy nằm trong sleep/hibernate, dùng nó thì ngủ
  bao lâu cũng không phát hiện ra.
- **Đặt TRƯỚC mọi lệnh gọi Firebase:** lúc vừa thức dậy card mạng thường chưa
  kết nối lại; nếu để sau, `get_device_status()` lỗi rồi `return` sớm và máy
  không bao giờ bị khóa.
- **Hệ quả được vá kèm:** đồng hồ đếm ngược cũng đứng yên trong lúc ngủ (QTimer
  không chạy, mà `timeRemaining` do chính client ghi lên Firebase) — ngủ 3 tiếng
  không bị trừ phút nào. Giờ ngủ dậy là khóa nên thời gian còn lại hết ý nghĩa.

---

## Code Locations Quan Trọng

### Web App (`web-app/public/`)

| Việc gì | Ở đâu |
|---|---|
| Firebase init + Google Auth | `index.html:150-215` |
| Query pending requests | `app.js:50-63` |
| Render danh sách thiết bị | `app.js:129` |
| Duyệt yêu cầu | `app.js:304` (`approveRequest`) |
| Từ chối yêu cầu | `app.js:329` (`rejectRequest`) |
| Nút bấm từ notification | `app.js:347` |
| Khóa máy (có delay) | `app.js:357` (`lockDevice`) |
| Dọn request cũ | `app.js:388` |
| Kiểm tra online | `app.js:477` (`isDeviceOnline`) |
| Xử lý "không giới hạn thời gian" | `app.js:473` (`hasTimeLimit`) |

### Windows Client (`windows-client/`)

| Việc gì | Ở đâu |
|---|---|
| Vòng lặp chính | `main.py:426` (`check_firebase_updates`) |
| Đang khóa - chờ duyệt | `main.py:333` (`handle_locked_state`) |
| Đang mở - chờ lệnh khóa | `main.py:384` (`handle_unlocked_state`) |
| Tạo lock screen | `main.py:113` (`show_lock_screen`) |
| Hoàn tất mở khóa | `main.py:177` (`complete_unlock`) |
| Heartbeat | `main.py:319` |
| Emergency unlock | `main.py:266` |
| Thoát app (cần mật khẩu) | `main.py:450` |
| Chặn phím tắt | `input_blocker.py` |
| Chống chạy 2 instance | `single_instance.py` |
| Kiểm tra mật khẩu | `password_util.py` |
| Đường dẫn file runtime (dev / .exe) | `paths.py` (`app_path`) |
| Đóng gói .exe | `ParentalControl.spec`, `build-exe.bat` |

---

## Database Schema

```json
{
  "devices": {
    "<device-uuid>": {
      "status": "locked | pending | unlocked",
      "timeLimit": 7200,
      "timeRemaining": 3600,
      "lockScheduled": 1234567890000,
      "lastActive": 1234567890,
      "deviceName": "PC-CON",
      "createdAt": 1234567890
    }
  },
  "requests": {
    "<request-uuid>": {
      "deviceId": "<device-uuid>",
      "type": "unlock_request",
      "timestamp": 1234567890,
      "status": "pending | approved | rejected",
      "deviceName": "PC-CON"
    }
  }
}
```

Lưu ý:
- `timeRemaining` **vắng mặt** khi mở khóa vô thời hạn (Firebase xóa key khi
  set `null`). Đừng dùng `device.timeRemaining || 0` — sẽ hiện "Còn 0h 0m".
- `lockScheduled` tính bằng **milliseconds** (`Date.now()`), còn `timestamp` và
  `lastActive` tính bằng **seconds**.
- `lastActive` dùng đồng hồ của máy con. Máy sai giờ → trạng thái online sai.

---

## Configuration Files

### `windows-client/config.py` (gitignored)
Copy từ `config.example.py`. Các tham số:

```python
CHECK_INTERVAL = 2000       # ms - tần suất polling Firebase
HEARTBEAT_INTERVAL = 5      # giây - cập nhật lastActive
REJECT_RETRY_DELAY = 30     # giây - chờ trước khi gửi lại yêu cầu
WARNING_TIME = 600          # giây - cảnh báo còn 10 phút

EMERGENCY_UNLOCK_ENABLED = True
EMERGENCY_UNLOCK_PASSWORD_HASH = "<sha256>"   # đổi bằng set_password.py
EMERGENCY_UNLOCK_PASSWORD = ""                # fallback plaintext (cấu hình cũ)

BLOCK_SYSTEM_HOTKEYS = True
SINGLE_INSTANCE = True
REQUIRE_PASSWORD_TO_EXIT = True

LOCK_ON_WAKE = True         # ngủ dậy thì khóa lại, coi như vừa bật máy
SLEEP_DETECT_SECONDS = 60   # giây - ngủ lâu hơn ngần này mới khóa
```

> Khi đóng gói `.exe`, `config.py` được **nhúng thẳng vào file exe**. Cấu hình
> xong rồi mới `build-exe.bat`; sửa config sau đó phải build lại.

### `web-app/public/index.html`
`firebaseConfig` ở khoảng dòng 126.

### `firebase/database.rules.json`
Security Rules. **Nguồn duy nhất** — đừng chép rules từ file .md nào khác.

---

## Bugs Đã Sửa (v1.2)

| # | Vấn đề | Cách sửa |
|---|---|---|
| 5 | Thiết bị luôn hiện Offline khi mở khóa vô thời hạn — không có timer nên `lastActive` đứng yên | Thêm heartbeat độc lập (`send_heartbeat_if_due`), nới ngưỡng online lên 20s |
| 6 | `rejectBtn.dataset.deviceId` không bao giờ được set → Slack luôn ghi "Unknown Device" | Set deviceId lên cả hai nút trong `renderPendingRequests` |
| 7 | UI hiện "Còn 0h 0m" khi mở khóa vô thời hạn | Thêm `hasTimeLimit()`, hiện "∞ Không giới hạn" |
| 8 | `requests/` phình vô hạn, web load cả nhánh mỗi lần thay đổi | Client tự xóa request đã xử lý; web query `equalTo('pending')` + dọn định kỳ |
| 9 | Notification dùng `new Notification()` nên `actions`/`vibrate` bị bỏ qua | Chuyển sang Service Worker `showNotification`, nút bấm gửi về app qua `postMessage` |
| 2 | `lockScheduled` không clear sau khi lịch nổ → approve xong bị khóa lại sau 2 giây, vĩnh viễn | `on_time_expired()` gọi `clear_lock_schedule()`; `approveRequest()` cũng set `lockScheduled: null` |
| 2b | Lịch khóa và timer đếm ngược cùng bắn `on_time_expired()` cách nhau 1-2 giây → hai lock screen, hai unlock request | Guard `if self.is_locked: return` + `TimerWidget.stop()` dừng hẳn QTimer (trước chỉ `hide()`) |
| 3 | `initialize_device()` dùng `.set()` → mỗi lần khởi động ghi đè `createdAt`, xóa `lockScheduled` và mọi field web app thêm vào | `.update()` khi node đã tồn tại, `.set()` chỉ khi tạo mới; phân biệt "chưa tồn tại" với "đọc lỗi" để mất mạng không gây xóa node |
| 1 | Rules cho phép `auth == null` đọc/ghi ở mức collection → ai cũng liệt kê & xóa sạch database | Bỏ `auth == null` ở mức collection, chỉ giữ ở `$deviceId` / `$requestId`. Kèm `firebase/verify-rules.py` để kiểm chứng |
| 10 | **Cho máy ngủ thay vì tắt = không bao giờ bị khóa.** Tiến trình không khởi động lại, Task Scheduler chỉ có `LogonTrigger` | Phát hiện bước nhảy thời gian ở đầu vòng lặp polling → khóa lại (`LOCK_ON_WAKE`) |
| 11 | `update_status`, `update_time_remaining`, `send_unlock_request` không có `try/except`. Mất mạng đúng lúc khóa → exception trong slot Qt → PyQt gọi `qFatal` giết cả app, để lại máy **không khóa** | Bọc `try/except`, trả `None`/`False` thay vì ném |
| 12 | Gửi yêu cầu mở khóa thất bại vì mạng → `current_request_id = None` và không có hẹn gửi lại → `handle_locked_state` đứng im, phụ huynh không thấy yêu cầu nào | Hẹn gửi lại sau `REQUEST_RETRY_DELAY` (5s) ở cả 3 nhánh gửi request |
| 13 | Slack luôn báo "Đã hết giờ và bị khóa" kể cả khi khóa vì lý do khác | `on_time_expired(reason=...)` truyền lý do xuống `send_time_expired` |

### Dọn dẹp kèm theo
- Xóa `mobile-app/` (Flutter dở dang, thiếu `android/` và `ios/` nên không build được)
- Xóa `RobloxPlayerInstaller.exe` ở root; thêm `*.exe`, `*.msi` vào `.gitignore`
- Hợp nhất Security Rules về một file, sửa các bản rules mâu thuẫn nằm trong .md
- Xóa dead code trong `app.js`: `unlockDevice()`, `addTime()`, `setTimeLimit()`
- Bỏ hàng chục `console.log` debug trong luồng render request
- `slack_notifier.py` dùng đường dẫn tuyệt đối cho `slack_webhook.txt`
- Mật khẩu emergency chuyển sang SHA-256 hash + script `set_password.py`
- Chống chạy nhiều instance (named mutex)
- Chặn Alt+Tab / Win / Alt+F4 / Ctrl+Esc khi đang khóa
- Thoát từ system tray phải nhập mật khẩu
- `run-debug.bat` set `chcp 65001`, `main.py` ép stdout về UTF-8 (emoji trong
  log từng làm sập app khi chạy bằng `python.exe`)

---

## Thay Đổi Chi Tiết Theo File (v1.1 → v1.2)

> Toàn bộ thay đổi dưới đây **chưa commit** — vẫn nằm ở working tree. Commit
> gần nhất là `9c33f6d` (v1.1, 11/01/2026).

### File mới

| File | Nội dung |
|---|---|
| `web-app/public/sw.js` | Service Worker: `showNotification` có `actions`, `notificationclick` → `postMessage` về app, focus tab khi click |
| `windows-client/paths.py` | `is_frozen()` / `app_dir()` / `app_path()` — phân giải đường dẫn bền cho cả chạy python lẫn chạy `.exe` |
| `windows-client/input_blocker.py` | Low-level keyboard hook (Win32) chặn Alt+Tab, phím Windows, Alt+F4, Ctrl+Esc khi đang khóa |
| `windows-client/single_instance.py` | Named mutex — không cho chạy 2 bản cùng lúc |
| `windows-client/password_util.py` | Hash SHA-256 + verify mật khẩu (giữ fallback plaintext cho cấu hình cũ) |
| `windows-client/set_password.py` | Script đổi mật khẩu khẩn cấp, ghi hash vào `config.py` |
| `windows-client/config.example.py` | Mẫu cấu hình (vì `config.py` bị gitignore, trước đây repo không có bản mẫu nào) |
| `windows-client/ParentalControl.spec` | PyInstaller spec (hidden imports cho pyrebase, `console=False`) |
| `windows-client/build-exe.bat` | Build wrapper: kiểm tra `config.py`, tự cài PyInstaller, chạy spec |
| `windows-client/setup_autostart_exe.bat` | Auto-start cho bản đóng gói (Task Scheduler trỏ vào `.exe`) |
| `windows-client/BUILD-EXE-GUIDE.md` | Hướng dẫn build + cài lên máy con + xử lý sự cố |
| `firebase/verify-rules.py` | Probe rules **không kèm token** (giả lập người ngoài), 8 kiểm tra: người lạ không liệt kê được collection, client không đăng nhập vẫn ghi được node của nó |

### File sửa

| File | Thay đổi |
|---|---|
| `windows-client/main.py` | Heartbeat độc lập (`send_heartbeat_if_due`); guard `is_locked` chống double-fire `on_time_expired`; emergency unlock verify qua hash; `quit_app` yêu cầu mật khẩu; tích hợp single-instance + input blocker; cooldown 30s sau khi bị từ chối; ép `stdout` về UTF-8 (emoji trong log từng làm sập app) |
| `windows-client/firebase_handler.py` | `initialize_device()` dùng `.update()` khi node đã tồn tại (trước là `.set()` → ghi đè `createdAt`, xóa `lockScheduled`); phân biệt "chưa tồn tại" với "đọc lỗi" để mất mạng không gây xóa node; thêm `clear_lock_schedule()`, `send_heartbeat()`, `delete_request()`, `check_request_status()`; `DEVICE_ID_PATH` đi qua `app_path()` |
| `windows-client/lock_screen.py` | `show_rejected_message()` + đếm ngược tới lần gửi lại; `reset_message()`; `allow_close()` để admin thoát app đóng được cửa sổ (trước `closeEvent` luôn `ignore()`) |
| `windows-client/timer_widget.py` | Thêm `stop()` — dừng hẳn `QTimer` (trước chỉ `hide()`, timer vẫn chạy ngầm và bắn hết giờ lần hai); `set_time_remaining()` tự khởi động lại đồng hồ |
| `windows-client/slack_notifier.py` | `slack_webhook.txt` dùng đường dẫn tuyệt đối qua `app_path()` (trước phụ thuộc thư mục hiện hành → chạy auto-start là mất webhook) |
| `windows-client/run-debug.bat` | Thêm `chcp 65001` để console hiện đúng tiếng Việt/emoji |
| `web-app/public/app.js` | Query `equalTo('pending')` thay vì load cả nhánh `requests`; `cleanupStaleRequests()`; `hasTimeLimit()` cho mở khóa vô thời hạn; `approveRequest` set `lockScheduled: null`; set `deviceId` cho **cả hai** nút duyệt/từ chối; nhận `notification-action` từ Service Worker; xóa dead code `unlockDevice/addTime/setTimeLimit` + hàng chục `console.log` |
| `web-app/public/index.html` | Import thêm `remove, get, query, orderByChild, equalTo` từ Firebase SDK và expose qua `window.dbRef` (phục vụ query pending + xóa request) |
| `web-app/public/notifications.js` | Chuyển từ `new Notification()` sang Service Worker `showNotification` (nhờ đó `actions` và `vibrate` mới có tác dụng); thêm `closeResolved` tự đóng notification khi request hết pending |
| `firebase/database.rules.json` | Bỏ `auth == null` ở **mức collection** (`devices`, `requests`), chỉ giữ ở mức node `$deviceId` / `$requestId`; thêm `.indexOn: ["status","timestamp"]` |
| `FIREBASE-RULES-SECURE.json` | Đồng bộ y hệt `firebase/database.rules.json` |
| `.gitignore` | Thêm `*.exe`, `*.msi`; thêm build artifact `windows-client/build/`, `dist/`, `test-run/` |
| Tài liệu (`README.md`, `QUICKSTART.md`, `WEB-APP-QUICKSTART.md`, `SECURITY-SUMMARY.md`, `FIREBASE-SECURITY-SETUP.md`, `firebase/README.md`, `web-app/README.md`, `AUTO-START-GUIDE.md`, `SAFETY-FEATURES.md`) | Đồng bộ theo rules mới; gỡ các bản rules mâu thuẫn từng nằm rải rác trong .md; cập nhật hướng dẫn mật khẩu hash và các tính năng an toàn mới |

### File xóa

| File | Lý do |
|---|---|
| `mobile-app/` (8 file Flutter) | Dở dang — thiếu `android/` và `ios/` nên không build được. Vai trò của nó đã do web app đảm nhiệm |
| `RobloxPlayerInstaller.exe` (root) | Binary lạc vào repo, không thuộc dự án |

---

## Bugs CHƯA Sửa

### 🟠 1. Client vẫn truy cập Firebase mà không đăng nhập

Sau bản vá, người ngoài **không** còn liệt kê hay xóa sạch được database. Nhưng
`auth == null` vẫn được chấp nhận ở mức từng node lẻ (`devices/$deviceId`,
`requests/$requestId`) vì Windows client không đăng nhập.

Nghĩa là ai **biết chính xác device UUID** vẫn ghi được vào node đó. UUID không
đoán được và không liệt kê được nữa, nhưng **đứa con thì biết** — nó nằm ngay
trong `windows-client/device_id.txt` trên máy nó.

**Hướng sửa tận gốc:** Firebase Anonymous Auth, dùng `uid` làm device ID:

```python
user = self.firebase.auth().sign_in_anonymous()
self.db.child(path).get(user['idToken'])
# lưu refreshToken ra file, refresh mỗi <1 giờ
```

```jsonc
"$deviceId": { ".write": "auth != null && (auth.uid == $deviceId || isParent)" }
```

### 🟡 2. Lock screen là "khóa mềm"

Chặn được Alt+Tab, phím Windows, Alt+F4, Ctrl+Esc (`input_blocker.py`) nhưng
**không** chặn được `Ctrl+Alt+Del` → Task Manager → kill `pythonw.exe`.

Đây là giới hạn thật của mọi giải pháp chạy ở user-mode. Muốn chặn triệt để:
- Cho con dùng tài khoản Windows **standard** (không phải admin)
- Chạy phần canh giữ dưới dạng **Windows Service**
- Hoặc khóa Task Manager bằng Group Policy

---

## Trạng Thái Hiện Tại (cập nhật 24/08/2026)

### Đã có hiệu lực

| Hạng mục | Bằng chứng |
|---|---|
| **Firebase Rules đã publish** | `python firebase/verify-rules.py` → **8/8** (kiểm ngày 24/08/2026). Người ngoài không liệt kê được `devices`/`requests`, root đóng; client không đăng nhập vẫn đọc/ghi được node của nó |
| **Windows client trên máy dev chạy code mới** | Task `ParentalControlClient` đang Running, tiến trình `pythonw.exe` khởi động 24/08/2026 09:30 — sau mọi lần sửa `.py` (mới nhất 23/08 11:24) |

### Còn treo

| # | Việc | Chi tiết |
|---|---|---|
| 1 | **Web app chưa deploy** | Netlify (`yutokun.netlify.app`) vẫn là bản cũ: `sw.js` trả **404**, `app.js` 18.590 bytes so với 20.451 bytes ở local. Nghĩa là notification có nút bấm, query pending và `cleanupStaleRequests` **chưa chạy thật**. Deploy lại thư mục `web-app/public/` lên Netlify, rồi tải lại trang trên điện thoại để Service Worker đăng ký |
| 2 | **Chưa build `.exe`** | Hạ tầng đóng gói đã viết xong nhưng chưa chạy lần nào (`windows-client/dist/` chưa tồn tại). Chỉ cần khi mang sang máy con **không cài Python** — máy dev không cần |
| 3 | **Chưa commit** | 22 file sửa + 12 file mới + xóa `mobile-app/` vẫn nằm ở working tree. Commit cuối cùng là `9c33f6d` (v1.1) |

---

## Known Issues Cũ (đã giải quyết từ trước)

| Vấn đề | Giải pháp |
|---|---|
| Email whitelist lộ trong frontend | Chuyển sang Firebase Rules (server-side) |
| `QInputDialog` crash khi hiện trên lock screen | Custom `EmergencyDialog` |
| Lock screen không hiện ở lần khóa thứ 2 | Tạo mới lock screen mỗi lần khóa |
| Approved screen không tự đóng | Tạo mới approved screen mỗi lần unlock |
| Console Python hiện trong taskbar | Dùng `pythonw.exe` trong `START.bat` |
| Firebase permission denied cho Windows Client | Rules cho phép `auth == null` |

---

## How to Run

### Prerequisites
```bash
pip install -r windows-client/requirements.txt
```

### Windows Client
```bash
cd windows-client
copy config.example.py config.py    # rồi sửa FIREBASE_CONFIG
python set_password.py              # đổi mật khẩu emergency

run-debug.bat     # chạy có console để xem log
START.bat         # chạy ẩn (pythonw.exe)
```

Auto-start: chuột phải `setup_autostart.bat` → Run as administrator.
Gỡ: `remove_autostart.bat` (cũng cần quyền admin).

### Web App
```bash
cd web-app
run-local.bat     # http://localhost:8000
```

Deploy: kéo `web-app/public/` vào Netlify, rồi thêm domain vào
Firebase Console → Authentication → Settings → Authorized domains.

> Service Worker cần HTTPS hoặc `localhost`. Mở web app qua
> `http://<tên-máy>:8000` từ điện thoại sẽ không đăng ký được SW → notification
> rơi về bản không có nút bấm.

---

## Future Features (Not Implemented)

### High Priority
- [ ] Siết Firebase Rules (bỏ `auth == null`) — xem "Bugs CHƯA Sửa" #1
- [ ] Clear `lockScheduled` sau khi khóa — #2
- [ ] Multiple device profiles (different kids)
- [ ] Usage statistics & reports
- [ ] Schedule automatic locks (bedtime)

### Medium Priority
- [ ] FCM Web Push để nhận thông báo khi đóng trình duyệt
- [ ] Whitelist/blacklist applications
- [ ] Activity logs
- [ ] Website filtering

### Low Priority
- [ ] Multi-language support
- [ ] Dark mode for web app

---

## File Structure

```
d:\yuto control\
├── web-app/
│   ├── public/
│   │   ├── index.html          # UI + Firebase init + Google Auth
│   │   ├── app.js              # Logic duyệt / khóa / dọn request
│   │   ├── notifications.js    # NotificationManager (qua Service Worker)
│   │   ├── sw.js               # Service Worker
│   │   ├── slack-setup.html    # Cấu hình Slack webhook cho web
│   │   └── styles.css
│   ├── firebase.json
│   ├── netlify.toml
│   └── NETLIFY-DEPLOY.md
├── windows-client/
│   ├── main.py                 # Entry point, vòng lặp polling
│   ├── firebase_handler.py     # Đọc/ghi Firebase
│   ├── lock_screen.py          # Lock screen + approved screen
│   ├── timer_widget.py         # Đồng hồ đếm ngược + cảnh báo
│   ├── emergency_dialog.py     # Dialog nhập mật khẩu
│   ├── password_util.py        # Hash + verify mật khẩu
│   ├── set_password.py         # Script đổi mật khẩu
│   ├── input_blocker.py        # Keyboard hook chặn phím tắt
│   ├── single_instance.py      # Named mutex chống chạy 2 bản
│   ├── slack_notifier.py       # Thông báo Slack
│   ├── paths.py                # Phân giải đường dẫn (dev / .exe)
│   ├── ParentalControl.spec    # PyInstaller spec
│   ├── build-exe.bat           # Đóng gói thành .exe
│   ├── setup_autostart_exe.bat # Auto-start cho bản .exe
│   ├── config.example.py       # Mẫu cấu hình
│   ├── config.py               # Cấu hình thật (gitignored)
│   ├── START.bat / run.bat / run-debug.bat
│   ├── setup_autostart.bat / remove_autostart.bat
│   ├── SAFETY-FEATURES.md
│   └── AUTO-START-GUIDE.md
├── firebase/
│   ├── database.rules.json     # Security Rules (nguồn duy nhất)
│   ├── verify-rules.py        # Kiểm chứng rules đã publish đúng chưa
│   └── README.md
├── FIREBASE-RULES-SECURE.json  # Bản copy của rules (tương thích tài liệu cũ)
├── FIREBASE-SECURITY-SETUP.md
├── SECURITY-SUMMARY.md
├── QUICKSTART.md
├── WEB-APP-QUICKSTART.md
├── README.md
└── PROJECT_CONTEXT.md          # File này
```

---

## Contact & Support

**GitHub Repository:** https://github.com/yutobeo2024/pc-control

---

## Changelog

### v1.2.1 (2026-08-24) - Khóa khi máy ngủ dậy
- 🔒 Phát hiện máy vừa ngủ dậy (sleep/hibernate) và khóa lại — bịt đường đi vòng
  "cho ngủ thay vì tắt máy". Tùy chọn `LOCK_ON_WAKE` / `SLEEP_DETECT_SECONDS`
- 🐛 `update_status` / `update_time_remaining` / `send_unlock_request` chịu được
  lỗi mạng — trước đây mất mạng đúng lúc khóa có thể giết cả app và để máy mở
- 🐛 Hẹn gửi lại yêu cầu mở khóa khi gửi thất bại, không còn kẹt ở trạng thái
  khóa mà không có yêu cầu nào chờ duyệt
- 💬 Thông báo Slack ghi đúng lý do khóa thay vì luôn ghi "hết giờ"

**Files sửa:** `main.py`, `firebase_handler.py`, `slack_notifier.py`,
`config.py`, `config.example.py`

### v1.2 (2026-08-23) - Cleanup & Bug Fixes
- 🔒 Siết Firebase Rules: bỏ `auth == null` ở mức collection
- 🐛 Sửa `lockScheduled` không clear + double-fire `on_time_expired`
- 🐛 `initialize_device()` không còn ghi đè node mỗi lần khởi động
- 🐛 Sửa 5 bug: online status, deviceId nút từ chối, hiển thị "không giới hạn",
  `requests/` phình vô hạn, notification không có nút bấm
- 🧹 Xóa `mobile-app/` (Flutter dở dang), stray `.exe`, dead code trong `app.js`
- 🔐 Mật khẩu emergency chuyển sang SHA-256 hash + `set_password.py`
- 🛡️ Chặn Alt+Tab / Win / Alt+F4 / Ctrl+Esc khi đang khóa
- 🔒 Thoát từ system tray phải nhập mật khẩu
- 🔁 Chống chạy nhiều instance (named mutex)
- ⏳ Cooldown 30s sau khi bị từ chối, kèm đếm ngược trên lock screen
- 📄 Hợp nhất Security Rules về một file, sửa tài liệu mâu thuẫn

**Files mới:** `sw.js`, `input_blocker.py`, `single_instance.py`,
`password_util.py`, `set_password.py`, `config.example.py`

### v1.1 (2026-01-11) - Push Notifications
- 🔔 Browser notification cho yêu cầu mở máy
- 🔘 Toggle bật/tắt, test notification
- 📱 Âm thanh + rung trên mobile

**Commit:** e23986f

### v1.0.0 (2026-01-11) - Initial Release
- ✅ Lock/unlock cơ bản, không giới hạn thời gian khi approve
- ✅ 6 tùy chọn khóa có hẹn giờ
- ✅ Google Authentication + email whitelist server-side
- ✅ Emergency unlock (Ctrl+Shift+Alt+U)
- ✅ Auto-start with Windows

**Commit:** cec6417

---

**Last Updated:** 2026-08-23
**Version:** 1.2
**Status:** Production Ready — cần publish rules mới lên Firebase Console
