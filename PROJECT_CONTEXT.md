# FANCY PC CONTROL - Project Context

## Tổng Quan Dự Án

### Mục đích
Hệ thống FANCY PC CONTROL cho phép Admin quản lý việc sử dụng máy tính của nhân viên từ xa thông qua Web App hiện đại, hỗ trợ điều khiển tức thời, đặt lịch khóa máy hàng loạt và quản lý thời gian làm việc.

### Architecture
```
┌─────────────────────┐
│   Admin Web App     │
│   (Netlify)         │
│   - Google Auth     │
│   - Premium UI      │
│   - Bulk Control    │
└──────────┬──────────┘
           │
           │ Firebase Realtime DB (fancy-pc-11159)
           │ (Real-time sync)
           │
┌──────────▼──────────┐
│  Windows Client     │
│  (Python/PyQt5)     │
│  - Lock Screen      │
│  - Remote Commands  │
│  - Bulk Schedule    │
└─────────────────────┘
```

### Tech Stack

**Frontend (Web App):**
- HTML5/CSS3 (Vanilla CSS with Premium Glassmorphism)
- Firebase SDK v10+
- Deployed on Netlify (`fancy-pc.netlify.app`)

**Backend:**
- Firebase Realtime Database
- Firebase Authentication (Google Sign-In)

**Windows Client:**
- Python 3.12+
- PyQt5 (GUI)
- Pyrebase (Firebase integration)

---

## Key Features Đã Hệ Thống

### 1. FANCY PC CONTROL Branding ⭐ NEW
- Giao diện được thiết kế lại hoàn toàn theo phong cách **Premium Glassmorphism**.
- Dark Mode mặc định với các hiệu ứng gradient và animation mượt mà.
- Thay đổi tone màu chủ đạo sang Violet & Rose.

### 2. Bulk Scheduled Lock (Khóa hàng loạt) ⭐ NEW
- Admin có thể thiết lập giờ khóa máy chung cho toàn bộ nhân viên.
- Hỗ trợ kiểu lặp lại: **Một lần** (Once) hoặc **Hàng ngày** (Daily).
- Client tự động kiểm tra và thực hiện khóa máy đồng loạt khi đến giờ hẹn.

### 3. Employee Management (Quản lý Nhân viên)
- Cho phép Admin thay đổi tên hiển thị (Friendly Name) của nhân viên ngay trên Dashboard.
- Hiển thị Metadata chi tiết: Hostname gốc, Phiên bản hệ điều hành (Windows 10/11...).
- Bảo vệ tên tùy chỉnh: Không bị ghi đè bởi Hostname khi máy tính khởi động lại.

### 4. Emergency Unlock (Mở khóa Cấp cứu)
- **Hotkey:** `Ctrl+Shift+Alt+U`
- **Password:** `admin123` (Mặc định)
- **Security Fix:** Màn hình khóa giữ trạng thái FullScreen ngay cả khi nhập sai mật khẩu, ngăn chặn việc phá khóa bằng cách thu nhỏ cửa sổ.
- **Focus Management:** Tự động trả lại focus cho màn hình khóa sau khi đóng hộp thoại mật khẩu.

### 5. UI/UX Improvements
- Ẩn icon đếm ngược ở góc màn hình (Timer Widget) theo yêu cầu để tạo không gian làm việc sạch sẽ.
- Thông báo thân thiện hơn: "Đang chờ admin cho phép, đợi xíu em trai!".
- Màn hình phê duyệt (Approved Screen) hiển thị rõ ràng trong 2 giây trước khi đóng hoàn toàn.

---

## Code Locations Quan Trọng

### Web App
- `web-app/public/index.html`: Giao diện chính và cấu hình Firebase mới.
- `web-app/public/app.js`: Logic xử lý bulk schedule và employee management.
- `web-app/public/styles.css`: Hệ thống design system Premium.

### Windows Client
- `windows-client/main.py`: Chứa hàm `check_bulk_schedule` để kiểm tra lịch khóa hàng loạt.
- `windows-client/lock_screen.py`: Quản lý màn hình khóa và thông báo "em trai".
- `windows-client/config.py`: Cấu hình Firebase mới projects và mật khẩu admin.

---

## Nhật ký Nâng cấp (Changelog)

### v2.0 (2026-01-27) - FANCY PC CONTROL Migration
- ✅ Chuyển đổi sang dự án Firebase mới: `fancy-pc-11159`.
- ✅ Deploy domain Netlify mới: `fancy-pc.netlify.app`.
- ✅ Cập nhật danh sách Email Admin authorized: `hanhtoami@gmail.com`, `huyho.it98@gmail.com`, `kawavlr@gmail.com`.
- ✅ Triển khai tính năng Khóa máy hàng loạt (Bulk Schedule).
- ✅ Nâng cấp giao diện Premium Glassmorphism.
- ✅ Fix lỗi bảo mật màn hình khóa khi nhập sai password.
- ✅ Ẩn đồng hồ đếm ngược trên Client.

---

## Hướng dẫn Vận hành

### deploy Web App
Kéo thả thư mục `web-app/public` lên Netlify project `fancy-pc`.

### Cài đặt Client mới
1. Tải thư mục `windows-client`.
2. Kiểm tra `config.py` đã đúng thông tin Firebase.
3. Chạy `install-dependencies.bat`.
4. (Quan trọng) Xóa `device_id.txt` nếu máy này từng cài bản cũ.
5. Chạy `START.bat`.

---
**Last Updated:** 2026-01-27
**Status:** Version 2.0 - Fully Updated & Deployed ✅
