# Mobile App - Parental Control

Ứng dụng Flutter cho phụ huynh, chạy trên iOS và Android.

## Tính năng

1. **Nhận thông báo** khi con yêu cầu mở máy
2. **Phê duyệt/Từ chối** yêu cầu mở máy
3. **Xem trạng thái** máy tính con real-time
4. **Khóa máy từ xa** bất cứ lúc nào
5. **Thêm thời gian** linh hoạt (+15p, +30p, +1h)
6. **Đặt giới hạn** thời gian mặc định

## Yêu cầu

- Flutter 3.0 trở lên
- Android Studio / Xcode
- Firebase project đã setup

## Cài đặt

```bash
flutter pub get
```

## Cấu hình Firebase

### Android

1. Download `google-services.json` từ Firebase Console
2. Copy vào: `android/app/google-services.json`

### iOS

1. Download `GoogleService-Info.plist` từ Firebase Console
2. Copy vào: `ios/Runner/GoogleService-Info.plist`

## Chạy

### Android
```bash
flutter run
```

### iOS
```bash
cd ios
pod install
cd ..
flutter run
```

## Build Release

### Android APK
```bash
flutter build apk --release
```

File output: `build/app/outputs/flutter-apk/app-release.apk`

### iOS
```bash
flutter build ios --release
```

Sau đó mở Xcode để archive và submit lên App Store.

## Cấu trúc

```
lib/
├── main.dart                 # Entry point
├── models/
│   ├── device.dart          # Device model
│   └── unlock_request.dart  # Request model
├── screens/
│   ├── home_screen.dart     # Màn hình chính
│   └── control_screen.dart  # Màn hình điều khiển
└── services/
    └── firebase_service.dart # Firebase logic
```

## Permissions

### Android (android/app/src/main/AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
```

### iOS (ios/Runner/Info.plist)

Đã tự động được thêm khi setup Firebase Messaging.

## Gỡ lỗi

### Xem logs

```bash
flutter logs
```

### Test trên emulator

```bash
# Android
flutter emulators --launch <emulator_id>
flutter run

# iOS
open -a Simulator
flutter run
```

### Firebase Connection Issues

1. Kiểm tra `google-services.json` / `GoogleService-Info.plist`
2. Kiểm tra package name match với Firebase project
3. Xem Firebase Console → Realtime Database → Data

## UI Theme

- **Dark Mode** với màu nền `#1E1E1E`
- **Primary Color:** Orange
- **Cards:** `#2D2D2D`
- **Font:** Roboto

## Screenshots

### Home Screen
- Hiển thị yêu cầu mở khóa (nếu có)
- Danh sách thiết bị với trạng thái

### Control Screen
- Card trạng thái thiết bị
- Đồng hồ đếm ngược
- Nút điều khiển (Khóa/Mở/Thêm giờ)
- Cài đặt giới hạn thời gian
