# Hướng dẫn Setup Firebase

## Bước 1: Tạo Firebase Project

1. Truy cập [Firebase Console](https://console.firebase.google.com)
2. Click "Add project" / "Thêm dự án"
3. Đặt tên project: `parental-control-app` (hoặc tên khác)
4. Bỏ chọn Google Analytics (không cần thiết)
5. Click "Create project"

## Bước 2: Enable Realtime Database

1. Trong Firebase Console, chọn "Realtime Database" từ menu bên trái
2. Click "Create Database"
3. Chọn location gần nhất (VD: `asia-southeast1`)
4. Chọn "Start in test mode" (tạm thời)
5. Click "Enable"

### Cấu hình Security Rules

1. Chọn tab "Rules"
2. Copy nội dung từ file `database.rules.json`
3. Click "Publish"

## Bước 3: Enable Cloud Messaging (FCM)

1. Chọn "Cloud Messaging" từ menu bên trái
2. Click "Get started"
3. Cloud Messaging sẽ được kích hoạt tự động

## Bước 4: Lấy Config cho Windows Client

1. Click vào icon Settings (bánh răng) > "Project settings"
2. Scroll xuống "Your apps"
3. Click vào icon Web (`</>`)
4. Đặt tên app: `Windows Client`
5. Không cần check "Firebase Hosting"
6. Click "Register app"

7. Copy đoạn config, nó sẽ có dạng:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "parental-control-xxxx.firebaseapp.com",
  databaseURL: "https://parental-control-xxxx-default-rtdb.firebaseio.com",
  projectId: "parental-control-xxxx",
  storageBucket: "parental-control-xxxx.appspot.com",
  messagingSenderId: "1234567890",
  appId: "1:1234567890:web:xxxxxxxxxxxxxxxxxx"
};
```

8. Mở file `windows-client/config.py`
9. Thay thế các giá trị trong `FIREBASE_CONFIG` bằng các giá trị từ Firebase

## Bước 5: Lấy Config cho Mobile App (Flutter)

### Android

1. Trong Project Settings, scroll xuống "Your apps"
2. Click vào icon Android
3. Nhập package name: `com.parentalcontrol.app`
4. Click "Register app"
5. Download file `google-services.json`
6. Copy vào: `mobile-app/android/app/google-services.json`

### iOS

1. Click vào icon iOS
2. Nhập bundle ID: `com.parentalcontrol.app`
3. Click "Register app"
4. Download file `GoogleService-Info.plist`
5. Copy vào: `mobile-app/ios/Runner/GoogleService-Info.plist`

## Bước 6: Cấu hình Server Key cho FCM (Push Notifications)

1. Trong Project Settings, chọn tab "Cloud Messaging"
2. Scroll xuống "Cloud Messaging API (Legacy)"
3. Click "Enable" nếu chưa bật
4. Copy "Server key" (sẽ dùng cho mobile app)

## Database Structure

Sau khi setup xong, database sẽ có cấu trúc như sau:

```json
{
  "devices": {
    "device-uuid-1234": {
      "status": "locked",
      "timeLimit": 7200,
      "timeRemaining": 7200,
      "lastActive": 1234567890,
      "deviceName": "PC-Con-Nha",
      "parentId": "parent-uuid-5678",
      "createdAt": 1234567890
    }
  },
  "requests": {
    "request-uuid-abcd": {
      "deviceId": "device-uuid-1234",
      "type": "unlock_request",
      "timestamp": 1234567890,
      "status": "pending",
      "deviceName": "PC-Con-Nha"
    }
  }
}
```

## Test Firebase

Để test kết nối Firebase:

```python
# Test script
python windows-client/firebase_handler.py
```

## Bảo mật (Sau khi test xong)

Cập nhật Rules để bảo mật hơn:

```json
{
  "rules": {
    "devices": {
      "$device_id": {
        ".read": "auth != null",
        ".write": "auth != null && (auth.uid == data.child('parentId').val() || !data.exists())"
      }
    },
    "requests": {
      "$request_id": {
        ".read": "auth != null",
        ".write": "auth != null"
      }
    }
  }
}
```

## Lưu ý

- Không commit file config có chứa API keys lên Git
- Tạo file `.gitignore` để exclude các file config
- Test mode chỉ dùng khi phát triển, production cần bật authentication
