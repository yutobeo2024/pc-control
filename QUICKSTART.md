# Hướng dẫn Sử dụng Nhanh

## Bước 1: Setup Firebase (5 phút)

1. Truy cập https://console.firebase.google.com
2. Tạo project mới
3. Enable **Realtime Database** (chọn test mode)
4. Enable **Cloud Messaging**
5. Lấy config và cập nhật vào:
   - `windows-client/config.py`
   - `mobile-app/android/app/google-services.json`
   - `mobile-app/ios/Runner/GoogleService-Info.plist`

📖 Chi tiết: [firebase/README.md](firebase/README.md)

---

## Bước 2: Cài đặt Windows Client

### Yêu cầu
- Python 3.8 trở lên
- Windows 10/11

### Cài đặt

```bash
cd windows-client
pip install -r requirements.txt
```

### Chạy ứng dụng

```bash
python main.py
```

**Khi chạy lần đầu:**
- App sẽ tạo file `device_id.txt` với ID duy nhất
- Màn hình khóa sẽ hiện lên ngay lập tức
- Yêu cầu mở khóa được gửi tới Firebase

**Lưu ý Device ID:**
- Copy Device ID từ màn hình khóa hoặc system tray
- Dùng ID này để đăng ký trên mobile app

---

## Bước 3: Cài đặt Mobile App

### Yêu cầu
- Flutter 3.0 trở lên
- Android Studio hoặc Xcode

### Cài đặt

```bash
cd mobile-app
flutter pub get
```

### Chạy trên Android

```bash
flutter run
```

### Chạy trên iOS

```bash
cd ios
pod install
cd ..
flutter run
```

---

## Cách Sử dụng

### 1. Xác thực Mở máy

**Trên máy tính con:**
1. Bật máy tính
2. Màn hình khóa hiện: "Đang chờ phụ huynh cho phép..."
3. Device ID hiển thị ở dưới màn hình

**Trên điện thoại phụ huynh:**
1. Mở app
2. Nhận thông báo yêu cầu mở máy
3. Bấm **"Cho phép"** → Máy tính mở khóa
4. Bấm **"Từ chối"** → Máy tính vẫn bị khóa

### 2. Giới hạn Thời gian

**Cài đặt thời gian mặc định:**
1. Vào màn hình điều khiển thiết bị
2. Chọn "Giới hạn thời gian mặc định"
3. Chọn: 1 giờ / 2 giờ / 3 giờ

**Đồng hồ đếm ngược:**
- Hiển thị góc phải trên màn hình con
- Màu xám: bình thường
- Màu đỏ + cảnh báo: còn ≤ 10 phút
- Hết giờ → Tự động khóa máy

### 3. Điều khiển Từ xa

**Xem trạng thái:**
- Màn hình chính hiển thị danh sách thiết bị
- Trạng thái: Đã khóa / Đang hoạt động / Chờ phê duyệt
- Thời gian còn lại (nếu đang mở khóa)

**Khóa máy ngay:**
1. Chọn thiết bị
2. Bấm nút **"Khóa máy ngay"**
3. Máy tính sẽ bị khóa ngay lập tức

**Thêm thời gian:**
1. Chọn thiết bị đang mở khóa
2. Bấm: **+15 phút** / **+30 phút** / **+1 giờ**
3. Thời gian được cộng thêm tức thì

---

## Giao diện

### Mobile App

#### Màn hình Chính
```
┌─────────────────────────┐
│  Parental Control       │
├─────────────────────────┤
│                         │
│  🔔 Yêu cầu mở máy      │
│     PC-Con-Nha          │
│     Vừa xong            │
│                         │
│  [ Từ chối ] [ Cho phép ]│
│                         │
├─────────────────────────┤
│                         │
│  💻 PC-Con-Nha          │
│     Đang hoạt động      │
│     Còn 1h 45m 30s      │
│                    →    │
│                         │
└─────────────────────────┘
```

#### Màn hình Điều khiển
```
┌─────────────────────────┐
│  ✅ Đang hoạt động      │
│     ● Online            │
├─────────────────────────┤
│                         │
│  ⏱️ Thời gian còn lại   │
│      01:45:30           │
│                         │
├─────────────────────────┤
│                         │
│  [    Khóa máy ngay    ]│
│                         │
│  [+15p] [+30p] [+1h]    │
│                         │
│  Giới hạn mặc định:     │
│  [1h]   [2h]   [3h]     │
│                         │
└─────────────────────────┘
```

### Windows Client

#### Màn hình Khóa
```
┌─────────────────────────┐
│                         │
│         🔒              │
│                         │
│  Máy tính đã bị khóa    │
│                         │
│  Đang chờ phụ huynh     │
│  cho phép...            │
│                         │
│  Device ID: abc123...   │
│                         │
└─────────────────────────┘
```

#### Đồng hồ Đếm ngược (góc màn hình)
```
┌──────────────┐
│   ⏱️         │
│  01:45:30    │
└──────────────┘
```

---

## Troubleshooting

### Máy tính không kết nối Firebase

1. Kiểm tra `windows-client/config.py`
2. Đảm bảo `databaseURL` đúng
3. Test kết nối:
   ```bash
   python -c "from firebase_handler import FirebaseHandler; fb = FirebaseHandler(); print('OK')"
   ```

### Mobile app không nhận thông báo

1. Kiểm tra permissions (Settings → Notifications)
2. Đảm bảo FCM đã enable trong Firebase Console
3. Xem log: `flutter logs`

### Màn hình khóa không hiện

1. Chạy Python với quyền Administrator
2. Kiểm tra PyQt5 đã cài đúng:
   ```bash
   python -c "from PyQt5 import QtWidgets; print('OK')"
   ```

### Device không hiện trên mobile app

1. Kiểm tra Database Rules (test mode)
2. Kiểm tra Device ID từ `windows-client/device_id.txt`
3. Xem Firebase Console → Realtime Database

---

## Nâng cao

### Auto-start Windows Client

**Thêm vào Startup (Windows):**

1. Tạo shortcut của `main.py`
2. Copy vào: `C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

**Hoặc dùng Task Scheduler:**
```
Trigger: At startup
Action: Start program
  Program: pythonw.exe
  Arguments: "D:\yuto control\windows-client\main.py"
```

### Chạy ẩn (không hiện console)

Thay `python main.py` bằng:
```bash
pythonw main.py
```

### Build Mobile App (Release)

**Android:**
```bash
flutter build apk --release
```

**iOS:**
```bash
flutter build ios --release
```

---

## Bảo mật

⚠️ **Lưu ý:**
- Database đang ở test mode (ai cũng có thể đọc/ghi)
- Sau khi test xong, cập nhật Rules theo hướng dẫn trong `firebase/README.md`
- Thêm Firebase Authentication để bảo mật hơn

---

## Hỗ trợ

- **Issues:** GitHub Issues
- **Docs:** [README.md](README.md)
- **Firebase:** [firebase/README.md](firebase/README.md)
