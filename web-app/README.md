# Web App - Parental Control

Web app responsive cho mobile và desktop. Đây là giao diện phụ huynh duy nhất của dự án.

## Tính năng

- ✅ Responsive, hoạt động trên mọi thiết bị
- ✅ Không cần cài đặt, mở browser là dùng
- ✅ Tích hợp Slack notifications
- ✅ Real-time updates từ Firebase
- ✅ PWA-ready (có thể thêm vào home screen)

## Cấu trúc

```
web-app/
├── public/
│   ├── index.html          # Trang chính
│   ├── slack-setup.html    # Trang cấu hình Slack
│   ├── styles.css          # Styles responsive
│   └── app.js              # Logic ứng dụng
├── firebase.json           # Config Firebase Hosting
└── README.md
```

## Chạy Local

### Cách 1: Python HTTP Server

```bash
cd public
python -m http.server 8000
```

Mở browser: http://localhost:8000

### Cách 2: Live Server (VS Code)

1. Cài extension "Live Server"
2. Right-click vào `index.html` → "Open with Live Server"

## Deploy lên Firebase Hosting

### Bước 1: Cài Firebase CLI

```bash
npm install -g firebase-tools
```

### Bước 2: Login

```bash
firebase login
```

### Bước 3: Init Firebase

```bash
cd web-app
firebase init hosting
```

Chọn:
- Use existing project: `kanban-d775c`
- Public directory: `public`
- Configure as single-page app: `No`
- Overwrite index.html: `No`

### Bước 4: Deploy

```bash
firebase deploy --only hosting
```

URL sau khi deploy:
```
https://kanban-d775c.web.app
```

### Bước 5: Cập nhật URL trong Windows Client

Sau khi deploy, mở file `windows-client/main.py` và cập nhật:

```python
WEB_APP_URL = "https://kanban-d775c.web.app"
```

## Cấu hình Slack

1. Mở web app
2. Vào trang: `/slack-setup.html`
3. Làm theo hướng dẫn để tạo Slack Incoming Webhook
4. Paste Webhook URL và Save
5. Test notification

## Workflow

### 1. Con yêu cầu mở máy

- Windows client gửi request lên Firebase
- Gửi Slack notification với button link đến web app

### 2. Phụ huynh nhận thông báo

- Nhận message trên Slack
- Click button "Mở Web App & Duyệt"

### 3. Duyệt trên web app

- Web app mở ra, hiển thị yêu cầu
- Bấm "Cho phép" hoặc "Từ chối"
- Máy tính con nhận phản hồi real-time

### 4. Điều khiển từ xa

- Xem danh sách thiết bị
- Click vào device → Mở modal điều khiển
- Khóa/mở khóa, thêm giờ, đặt giới hạn

## Tính năng nâng cao

### PWA (Progressive Web App)

Thêm file `manifest.json` và service worker để:
- Thêm vào home screen như native app
- Hoạt động offline (cache dữ liệu)
- Push notifications (nếu cần)

### Dark/Light Mode

Hiện tại mặc định dark mode. Có thể thêm toggle để chuyển đổi.

### Multiple Parents

Hiện tại 1 web app cho tất cả devices. Có thể thêm authentication để phân quyền.

## Troubleshooting

### Firebase không connect

- Kiểm tra `index.html` có đúng Firebase config
- Kiểm tra Database URL đúng region (asia-southeast1)

### Slack notification không gửi

- Kiểm tra webhook URL đã lưu chưa (localStorage)
- Test webhook trên trang slack-setup.html
- Kiểm tra Windows client có file `slack_webhook.txt`

### Web app không update real-time

- Kiểm tra kết nối internet
- Refresh trang
- Kiểm tra Firebase Console → Database → Rules

## Browser Support

- Chrome/Edge: ✅
- Safari (iOS): ✅
- Firefox: ✅
- Samsung Internet: ✅

## Mobile Optimization

- Touch-friendly buttons (min 48px)
- Responsive layout (max-width: 600px)
- No hover states trên mobile
- Bottom sheet modal trên mobile
- Prevent zoom (user-scalable=no)
