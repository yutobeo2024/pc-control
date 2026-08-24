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
4. Chọn "Start in locked mode"
5. Click "Enable"

### Cấu hình Security Rules

1. Chọn tab "Rules"
2. Copy **toàn bộ** nội dung file [`database.rules.json`](database.rules.json)
3. Sửa danh sách email phụ huynh trong rules cho đúng tài khoản của bạn
4. Click "Publish"
5. Kiểm chứng: `python verify-rules.py` (kỳ vọng **8/8**)

> `database.rules.json` là **nguồn duy nhất** cho Security Rules của dự án.
> Đừng dán rules "test mode" (`.read: true / .write: true`) lên production —
> ai cũng đọc/ghi được database.

Rules chia 2 tầng: tầng collection chỉ cho phụ huynh đã đăng nhập, tầng node lẻ
mở thêm cho Windows client (không đăng nhập). Xem
[FIREBASE-SECURITY-SETUP.md](../FIREBASE-SECURITY-SETUP.md) để hiểu vì sao.

## Bước 3: Enable Authentication (Google Sign-In)

1. Chọn "Authentication" → tab "Sign-in method"
2. Bật provider **Google**
3. Sang tab "Settings" → "Authorized domains"
4. Thêm domain của web app (VD: `yutokun.netlify.app`)

## Bước 4: Lấy Config cho Windows Client & Web App

1. Click vào icon Settings (bánh răng) > "Project settings"
2. Scroll xuống "Your apps"
3. Click vào icon Web (`</>`)
4. Đặt tên app: `Parental Control`
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

8. Windows client: copy `windows-client/config.example.py` thành `config.py`,
   thay các giá trị trong `FIREBASE_CONFIG`
9. Web app: thay `firebaseConfig` trong `web-app/public/index.html`

## Database Structure

Sau khi setup xong, database sẽ có cấu trúc như sau:

```json
{
  "devices": {
    "device-uuid-1234": {
      "status": "locked",
      "timeLimit": 7200,
      "timeRemaining": 7200,
      "lockScheduled": null,
      "lastActive": 1234567890,
      "deviceName": "PC-Con-Nha",
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

Ghi chú:
- `timeRemaining` bị **xóa khỏi database** khi mở khóa không giới hạn thời gian
  (web app set `null`). Client hiểu "không có key" = vô thời hạn.
- `lastActive` được client cập nhật định kỳ (heartbeat) để web biết máy online.
- Node trong `requests/` được client xóa ngay sau khi đọc kết quả duyệt/từ chối.

## Test Firebase

```bash
cd windows-client
python -c "from firebase_handler import FirebaseHandler; print(FirebaseHandler().get_device_status())"
```

## Lưu ý bảo mật

- Không commit `windows-client/config.py` (đã có trong `.gitignore`)
- Rules vẫn cho phép `auth == null` ở **mức node lẻ** để Windows client
  (không đăng nhập) hoạt động. Ai biết chính xác device UUID vẫn ghi được vào
  node đó — xem `SECURITY-SUMMARY.md`.
  Hướng khắc phục: cho client đăng nhập bằng Firebase Anonymous Auth hoặc
  custom token, rồi siết `$deviceId` về `auth != null && auth.uid == $deviceId`.
