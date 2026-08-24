# 🚀 Web App Quick Start Guide

Hướng dẫn nhanh để chạy và deploy Web App cho Parental Control.

## 🎯 Tại sao dùng Web App?

✅ **Không cần cài app** - Mở browser là xài ngay
✅ **Chạy mọi thiết bị** - iPhone, Android, iPad, Laptop
✅ **Slack notifications** - Nhận alert và duyệt nhanh
✅ **Đơn giản hơn** - Không cần build APK/IPA

---

## 📱 Test ngay trên máy (2 phút)

### Bước 1: Chạy web server local

```bash
cd "d:\yuto control\web-app\public"
python -m http.server 8000
```

### Bước 2: Mở browser

Trên máy tính:
```
http://localhost:8000
```

Trên điện thoại (cùng WiFi):
```
http://<IP-máy-tính>:8000
```

Để lấy IP máy tính:
```bash
ipconfig | findstr IPv4
```

### Bước 3: Test

- Màn hình sẽ hiển thị "Connected" khi kết nối Firebase thành công
- Nếu Windows client đang chạy, bạn sẽ thấy device trong danh sách
- Click vào device để mở modal điều khiển

---

## 🌐 Deploy lên Firebase Hosting (10 phút)

### Bước 1: Cài Firebase CLI

```bash
npm install -g firebase-tools
```

Nếu chưa có npm, tải Node.js từ: https://nodejs.org

### Bước 2: Login Firebase

```bash
firebase login
```

Browser sẽ mở ra, chọn tài khoản Google của bạn.

### Bước 3: Init project

```bash
cd "d:\yuto control\web-app"
firebase init hosting
```

Trả lời các câu hỏi:
```
? Select a default Firebase project: kanban-d775c (Kanban)
? What do you want to use as your public directory? public
? Configure as a single-page app? No
? Set up automatic builds? No
? File public/index.html already exists. Overwrite? No
```

### Bước 4: Deploy

```bash
firebase deploy --only hosting
```

Sau khi deploy xong, bạn sẽ nhận được URL:
```
✔  Deploy complete!

Hosting URL: https://kanban-d775c.web.app
```

### Bước 5: Cập nhật URL trong Windows Client

Mở file `windows-client\main.py`, tìm dòng:

```python
WEB_APP_URL = "http://localhost:8000"
```

Thay bằng:

```python
WEB_APP_URL = "https://kanban-d775c.web.app"
```

Khởi động lại Windows client.

---

## 🔔 Setup Slack Notifications (5 phút)

### Bước 1: Tạo Slack Incoming Webhook

1. Vào https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. App Name: `Parental Control`
4. Workspace: Chọn workspace của bạn
5. Click **"Create App"**

6. Trong app settings:
   - Click **"Incoming Webhooks"** (sidebar)
   - Toggle **"Activate Incoming Webhooks"** → ON
   - Click **"Add New Webhook to Workspace"**
   - Chọn channel (VD: #general hoặc #parental-control)
   - Click **"Allow"**

7. Copy **Webhook URL** (dạng: `https://hooks.slack.com/services/T.../B.../...`)

### Bước 2: Config trên Web App

1. Mở web app: `https://kanban-d775c.web.app/slack-setup.html`
2. Paste Webhook URL vào ô input
3. Click **"Lưu cấu hình"**
4. Click **"Gửi test notification"** để kiểm tra

### Bước 3: Config trên Windows Client

#### Option 1: Chạy script config

```bash
cd "d:\yuto control\windows-client"
python slack_notifier.py
```

Paste Webhook URL khi được hỏi.

#### Option 2: Tạo file thủ công

Tạo file `windows-client\slack_webhook.txt` với nội dung:

```
https://hooks.slack.com/services/T.../B.../...
```

### Bước 4: Test

1. Chạy Windows client
2. Màn hình khóa sẽ xuất hiện
3. Kiểm tra Slack → Bạn sẽ nhận message với button "Mở Web App & Duyệt"
4. Click button → Web app mở ra
5. Bấm "Cho phép" → Máy tính mở khóa

---

## 📱 Sử dụng trên Mobile

### iOS (Safari)

1. Mở web app trong Safari
2. Bấm nút **Share** (ô vuông với mũi tên)
3. Chọn **"Add to Home Screen"**
4. Đặt tên: "Parental Control"
5. Icon sẽ xuất hiện trên home screen như native app

### Android (Chrome)

1. Mở web app trong Chrome
2. Menu (3 chấm) → **"Add to Home screen"**
3. Đặt tên: "Parental Control"
4. Icon sẽ xuất hiện trên launcher

### Lợi ích

- Mở nhanh như native app
- Không chiếm dung lượng
- Tự động update khi refresh

---

## 🔥 Workflow Hoàn chỉnh

### 1. Con bật máy tính

```
Windows Client
    ↓
Màn hình khóa hiện lên
    ↓
Gửi request lên Firebase
    ↓
Gửi Slack notification
```

### 2. Phụ huynh nhận thông báo

```
Slack Message:
🔔 Yêu cầu mở máy
Thiết bị: DESKTOP-ABC123
[Mở Web App & Duyệt] ← Button
```

### 3. Phụ huynh duyệt

```
Click button
    ↓
Web app mở ra
    ↓
Hiển thị request
    ↓
Bấm "Cho phép" hoặc "Từ chối"
    ↓
Firebase cập nhật real-time
    ↓
Windows Client nhận phản hồi
    ↓
Máy tính mở khóa hoặc vẫn khóa
```

### 4. Điều khiển từ xa

```
Mở web app bất cứ lúc nào
    ↓
Xem danh sách thiết bị
    ↓
Click vào device
    ↓
• Khóa máy ngay
• Thêm 15p / 30p / 1h
• Đặt giới hạn 1h / 2h / 3h
```

---

## 🎨 Giao diện Mobile

### Màn hình chính

```
┌─────────────────────────┐
│  🔒 Parental Control    │
│     ● Connected         │
├─────────────────────────┤
│                         │
│ ┌─────────────────────┐ │
│ │  🔔 Yêu cầu mở máy  │ │
│ │                     │ │
│ │  DESKTOP-ABC123     │ │
│ │  Vừa xong           │ │
│ │                     │ │
│ │ [Từ chối] [Cho phép]│ │
│ └─────────────────────┘ │
│                         │
│  Thiết bị               │
│ ┌─────────────────────┐ │
│ │ 💻 DESKTOP-ABC123   │ │
│ │ Đang hoạt động      │ │
│ │ Còn 1h 45m      ›   │ │
│ └─────────────────────┘ │
│                         │
└─────────────────────────┘
```

### Modal điều khiển

```
┌─────────────────────────┐
│ DESKTOP-ABC123      ✖   │
├─────────────────────────┤
│        ✅               │
│  Đang hoạt động         │
│      ● Online           │
├─────────────────────────┤
│  ⏱️ Thời gian còn lại   │
│      01:45:30           │
├─────────────────────────┤
│  [   Khóa máy ngay   ]  │
│                         │
│  [+15p] [+30p] [+1h]    │
│                         │
│  Giới hạn mặc định:     │
│  [1h]  [2h]  [3h]       │
└─────────────────────────┘
```

---

## 🔧 Troubleshooting

### Web app không kết nối Firebase

**Lỗi:** Màn hình hiển thị "Connecting..." mãi

**Fix:**
1. Mở Console (F12) → Tab "Console"
2. Xem có lỗi gì không
3. Kiểm tra Firebase config trong `public/index.html`
4. Đảm bảo Database URL đúng:
   ```
   https://kanban-d775c-default-rtdb.asia-southeast1.firebasedatabase.app
   ```

### Slack notification không gửi

**Lỗi:** Không nhận message trên Slack

**Fix:**
1. Kiểm tra file `windows-client\slack_webhook.txt` có tồn tại
2. Kiểm tra URL trong file có đúng format
3. Test webhook trên web app: `/slack-setup.html`
4. Xem Windows client console có lỗi không

### Device không hiện trên web app

**Lỗi:** Danh sách thiết bị trống

**Fix:**
1. Kiểm tra Windows client đang chạy
2. Kiểm tra Firebase Console → Database → Có data không
3. Refresh web app
4. Xem Network tab trong Console

---

## 📊 Vì sao dùng Web App thay vì app native

Dự án từng có một bản Flutter dở dang (chỉ có `lib/`, thiếu `android/` và
`ios/` nên không build được) - đã gỡ bỏ. Web App là giao diện phụ huynh duy nhất:

| Tiêu chí | Web App |
|----------|---------|
| **Cài đặt** | Mở browser, "Add to Home Screen" là xong |
| **Update** | Tự động khi deploy |
| **iOS / Android** | Chạy được cả hai, không mất phí developer account |
| **Deploy** | Push lên Netlify |
| **Thông báo** | Notification trình duyệt (cần mở tab) + Slack |

---

## 🎯 Next Steps

1. ✅ Deploy web app lên Firebase Hosting
2. ✅ Setup Slack notifications
3. ✅ Add to home screen trên mobile
4. 🔜 (Optional) Thêm PWA manifest cho offline support
5. 🔜 (Optional) Thêm Firebase Authentication
6. 🔜 (Optional) Multi-user support (nhiều phụ huynh)

---

## 💡 Tips

- **Bookmark** web app URL trên mobile
- **Pin Slack channel** để không bỏ lỡ notification
- **Test định kỳ** để đảm bảo mọi thứ hoạt động
- **Backup** Slack webhook URL

---

**Hoàn thành!** Giờ bạn có thể điều khiển máy tính con từ bất kỳ đâu chỉ với điện thoại. 🎉
