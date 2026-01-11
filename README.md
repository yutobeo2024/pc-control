# Ứng dụng Parental Control

Ứng dụng kiểm soát máy tính con cái đơn giản với 3 tính năng cốt lõi.

## Tính năng

### 1. Xác thực Mở máy
- Con bật máy tính → Màn hình khóa hiện: "Đang chờ phụ huynh cho phép..."
- App điện thoại nhận thông báo → Bấm "Cho phép" hoặc "Từ chối"
- Nếu approve → Máy tính mở khóa

### 2. Đặt Giới hạn Thời gian
- Phụ huynh đặt: VD "2 giờ/ngày"
- Đồng hồ đếm ngược hiển thị trên màn hình con
- Hết giờ → Tự động khóa máy

### 3. Điều khiển Từ xa
- Xem con đang dùng máy hay không
- Khóa máy ngay lập tức từ điện thoại
- Gia hạn thêm thời gian

## Kiến trúc

```
[Máy tính con]          [Firebase]          [App phụ huynh]
      |                     |                      |
   Bật máy  ----------->  Request  ---------> Thông báo
      |                     |                      |
   Chờ...  <-----------  Pending  <---------  Approve
      |                     |                      |
   Mở khóa <-----------  Unlock                    |
      |                     |                      |
   Đếm giờ                 |                 Theo dõi
      |                     |                      |
   Hết giờ ----------->  Timeout  ---------> Thông báo
      |                     |                      |
   Khóa                    |                      |
```

## Tech Stack

### Máy tính (Windows)
- **Python 3.8+**
- **PyQt5** - Giao diện và chạy nền
- **pyrebase4** - Kết nối Firebase
- Tự động khóa/mở khóa màn hình Windows

### Backend
- **Firebase Realtime Database** - Lưu trữ trạng thái
- **Firebase Cloud Messaging (FCM)** - Push notification
- Không cần tự code server

### Mobile App
- **Flutter** - Chạy cả iOS & Android
- **firebase_core** - Kết nối Firebase
- **firebase_messaging** - Nhận thông báo
- **firebase_database** - Đồng bộ dữ liệu

## Cấu trúc Dự án

```
yuto-control/
├── windows-client/          # Windows app (Python)
│   ├── main.py
│   ├── lock_screen.py
│   ├── timer_widget.py
│   ├── firebase_handler.py
│   └── requirements.txt
│
├── mobile-app/              # Flutter app
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/
│   │   │   ├── home_screen.dart
│   │   │   └── control_screen.dart
│   │   └── services/
│   │       └── firebase_service.dart
│   └── pubspec.yaml
│
├── firebase/                # Firebase config
│   ├── database.rules.json
│   ├── firebase-config.md
│   └── README.md
│
└── README.md
```

## Cài đặt

### 1. Setup Firebase
- Tạo project trên [Firebase Console](https://console.firebase.google.com)
- Enable Realtime Database
- Enable Cloud Messaging
- Tải xuống config files

### 2. Windows Client
```bash
cd windows-client
pip install -r requirements.txt
python main.py
```

### 3. Mobile App
```bash
cd mobile-app
flutter pub get
flutter run
```

## Database Schema (Firebase)

```json
{
  "devices": {
    "device_id_123": {
      "status": "locked|unlocked|pending",
      "timeLimit": 7200,
      "timeRemaining": 3600,
      "lastActive": 1234567890,
      "parentId": "parent_id_456"
    }
  },
  "requests": {
    "request_id_789": {
      "deviceId": "device_id_123",
      "type": "unlock_request",
      "timestamp": 1234567890,
      "status": "pending|approved|rejected"
    }
  }
}
```

## Bảo mật

- Mỗi thiết bị có ID duy nhất
- Xác thực qua Firebase Authentication
- Rules bảo vệ dữ liệu chỉ phụ huynh mới sửa được

## License

MIT License
