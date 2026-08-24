# Quick Start

Cài đặt hệ thống Parental Control trong ~15 phút.

Hệ thống gồm 2 phần: **Windows client** (chạy trên máy con) và
**Web app** (phụ huynh mở trên điện thoại). Firebase làm kênh trung gian.

---

## 1. Setup Firebase (5 phút)

Làm theo [`firebase/README.md`](firebase/README.md). Tóm tắt:

1. Tạo project trên [Firebase Console](https://console.firebase.google.com)
2. **Realtime Database** → Create Database → chọn region gần nhất → Start in locked mode
3. **Authentication** → Sign-in method → bật **Google**
4. **Realtime Database → Rules** → dán nội dung [`firebase/database.rules.json`](firebase/database.rules.json)
   → sửa email phụ huynh trong rules cho đúng → **Publish**
5. **Project settings → Your apps → Web (`</>`)** → copy `firebaseConfig`

---

## 2. Windows Client (5 phút)

Chạy trên **máy tính của con**.

### Cài đặt

```bash
cd windows-client
pip install -r requirements.txt
```

Hoặc chạy `install-dependencies.bat`.

### Cấu hình

```bash
copy config.example.py config.py
```

Mở `config.py`, thay `FIREBASE_CONFIG` bằng config lấy ở bước 1.

### Đổi mật khẩu khẩn cấp

```bash
python set_password.py
```

⚠️ Bắt buộc — mật khẩu mặc định là `admin123`. Đây là cách duy nhất mở khóa
máy khi Firebase / web app gặp sự cố, nên hãy **ghi lại ở nơi an toàn**.

### Chạy thử

```bash
run-debug.bat
```

Màn hình khóa sẽ hiện ra. Kiểm tra:
- [ ] Alt+Tab, phím Windows, Alt+F4 bị chặn
- [ ] `Ctrl+Shift+Alt+U` mở dialog nhập mật khẩu
- [ ] Nhập đúng mật khẩu → máy mở khóa

Thoát: chuột phải icon ở system tray → Exit (cần mật khẩu).

### Bật auto-start

Chuột phải `setup_autostart.bat` → **Run as administrator**.

Gỡ bằng `remove_autostart.bat` (cũng cần quyền admin).

---

## 3. Web App (5 phút)

Chạy trên **điện thoại phụ huynh**.

### Cấu hình

Mở `web-app/public/index.html`, thay `firebaseConfig` (dòng ~126) bằng
config lấy ở bước 1.

### Test local

```bash
cd web-app
run-local.bat
```

Mở `http://localhost:8000`.

### Deploy

Xem [`web-app/NETLIFY-DEPLOY.md`](web-app/NETLIFY-DEPLOY.md).
Sau khi deploy, thêm domain vào **Firebase Console → Authentication →
Settings → Authorized domains**.

Trên điện thoại: mở URL → menu trình duyệt → **Add to Home Screen**.

### Bật thông báo

Bấm nút 🔔 ở góc trên bên phải → cho phép notification.

⚠️ Thông báo chỉ đến khi tab web app còn mở (kể cả ở nền). Muốn nhận khi
đã đóng hẳn trình duyệt thì cần Slack (bước 4) hoặc FCM Web Push.

---

## 4. (Tùy chọn) Thông báo Slack

Slack hoạt động kể cả khi không mở web app — đáng để cấu hình.

1. Tạo Incoming Webhook: https://api.slack.com/messaging/webhooks
2. Windows client:
   ```bash
   cd windows-client
   python slack_notifier.py
   ```
   Dán webhook URL vào. File lưu tại `windows-client/slack_webhook.txt`.
3. Web app: mở `slack-setup.html` trên web app và dán cùng webhook URL.

---

## Luồng hoạt động

```
Con bật máy
   → Màn hình khóa + gửi yêu cầu lên Firebase
   → Phụ huynh nhận thông báo trên web app / Slack
   → Bấm "Cho phép"  → máy mở khóa (không giới hạn thời gian)
     Bấm "Từ chối"   → máy vẫn khóa, tự gửi lại yêu cầu sau 30 giây

Khi muốn khóa lại:
   → Mở web app → chọn thiết bị → "Khóa ngay" hoặc hẹn giờ 30p / 1h / 1.5h / 2h / 3h
```

---

## Xử lý sự cố

| Triệu chứng | Nguyên nhân thường gặp |
|---|---|
| Web app báo "Email không được phép" | Email chưa có trong Security Rules → sửa rules và Publish lại |
| Windows client không kết nối được | Sai `FIREBASE_CONFIG`, hoặc `databaseURL` thiếu region |
| Thiết bị luôn hiện Offline | Client không chạy, hoặc đồng hồ máy con sai giờ (`lastActive` lệch) |
| Không thấy thiết bị nào | Client chưa chạy lần nào — kiểm tra `windows-client/device_id.txt` |
| Bị khóa mà không mở được | Dùng `Ctrl+Shift+Alt+U`. Nếu quên mật khẩu: khởi động vào Safe Mode và xóa scheduled task |
| Đăng nhập Google lỗi `unauthorized-domain` | Chưa thêm domain vào Firebase → Authentication → Authorized domains |

Xem log chi tiết: chạy `windows-client/run-debug.bat` (có console).

---

## Đọc thêm

- [`README.md`](README.md) — kiến trúc, schema database
- [`WEB-APP-QUICKSTART.md`](WEB-APP-QUICKSTART.md) — hướng dẫn web app đầy đủ
- [`windows-client/SAFETY-FEATURES.md`](windows-client/SAFETY-FEATURES.md) — mở khóa khẩn cấp
- [`windows-client/AUTO-START-GUIDE.md`](windows-client/AUTO-START-GUIDE.md) — auto-start
- [`SECURITY-SUMMARY.md`](SECURITY-SUMMARY.md) — tình trạng bảo mật & hạn chế đã biết
