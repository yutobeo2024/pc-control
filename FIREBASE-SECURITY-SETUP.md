# 🔐 Hướng Dẫn Cấu Hình Bảo Mật Firebase

## ⚠️ QUAN TRỌNG: Làm ngay sau khi deploy!

Hiện tại Firebase Database của bạn **HOÀN TOÀN MỞ** cho bất kỳ ai. Phải cấu hình lại ngay!

---

## Bước 1: Cập Nhật Firebase Rules

### 1.1. Mở Firebase Console

1. Vào https://console.firebase.google.com/
2. Chọn project **kanban-d775c**
3. Vào **Realtime Database** ở sidebar trái
4. Click tab **Rules**

### 1.2. Thay Thế Rules Hiện Tại

**Rules CŨ (NGUY HIỂM):**
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

**Rules MỚI (BẢO MẬT CAO):**

**QUAN TRỌNG:** Thay email của bạn và vợ vào đây!

```json
{
  "rules": {
    "devices": {
      ".read": "auth != null && (auth.token.email == 'your-email@gmail.com' || auth.token.email == 'your-wife-email@gmail.com')",
      ".write": "auth != null && (auth.token.email == 'your-email@gmail.com' || auth.token.email == 'your-wife-email@gmail.com')",
      "$deviceId": {
        ".read": "auth != null && (auth.token.email == 'your-email@gmail.com' || auth.token.email == 'your-wife-email@gmail.com')",
        ".write": "auth != null && (auth.token.email == 'your-email@gmail.com' || auth.token.email == 'your-wife-email@gmail.com')"
      }
    },
    "requests": {
      ".read": "auth != null && (auth.token.email == 'your-email@gmail.com' || auth.token.email == 'your-wife-email@gmail.com')",
      ".write": "auth != null && (auth.token.email == 'your-email@gmail.com' || auth.token.email == 'your-wife-email@gmail.com')",
      "$requestId": {
        ".read": "auth != null && (auth.token.email == 'your-email@gmail.com' || auth.token.email == 'your-wife-email@gmail.com')",
        ".write": "auth != null && (auth.token.email == 'your-email@gmail.com' || auth.token.email == 'your-wife-email@gmail.com')"
      }
    }
  }
}
```

**Ví dụ với email thật:**
```json
{
  "rules": {
    "devices": {
      ".read": "auth != null && (auth.token.email == 'hanhtoami@gmail.com' || auth.token.email == 'thuydungsp@gmail.com')",
      ".write": "auth != null && (auth.token.email == 'hanhtoami@gmail.com' || auth.token.email == 'thuydungsp@gmail.com')"
    },
    "requests": {
      ".read": "auth != null && (auth.token.email == 'hanhtoami@gmail.com' || auth.token.email == 'thuydungsp@gmail.com')",
      ".write": "auth != null && (auth.token.email == 'hanhtoami@gmail.com' || auth.token.email == 'thuydungsp@gmail.com')"
    }
  }
}
```

**Giải thích:**
- `auth != null` → Phải đăng nhập
- `auth.token.email == 'xxx'` → CHỈ email này mới được phép
- Bảo mật ở **SERVER-SIDE** (Firebase), KHÔNG thể bypass
- Email whitelist giờ nằm ở Firebase Rules, KHÔNG lộ ra frontend

### 1.3. Publish Rules

1. Click **Publish** ở góc trên bên phải
2. Xác nhận publish

---

## Bước 2: Bật Google Authentication

### 2.1. Vào Authentication

1. Trong Firebase Console
2. Click **Authentication** ở sidebar
3. Click **Get Started** (nếu chưa setup)

### 2.2. Bật Google Sign-In

1. Click tab **Sign-in method**
2. Tìm **Google** trong danh sách providers
3. Click **Google** → Click **Enable**
4. **Project support email**: Chọn email của bạn
5. Click **Save**

---

## Bước 3: Deploy Lại Web App

### 3.1. Vào Netlify

1. Vào https://app.netlify.com/
2. Vào site **yutokun.netlify.app**

### 3.2. Deploy

**Cách 1: Drag & Drop (Dễ nhất)**
1. Kéo folder `d:\yuto control\web-app\public` vào Netlify
2. Chờ deploy xong (~ 1 phút)

**Cách 2: Netlify CLI**
```bash
cd "d:\yuto control\web-app"
netlify deploy --prod --dir=public
```

---

## Bước 4: Test Bảo Mật

### 4.1. Test Login

1. Mở https://yutokun.netlify.app/
2. Bấm **"Đăng nhập với Google"**
3. Chọn email của bạn (hoặc email vợ)
4. ✅ Phải vào được app

### 4.2. Test Unauthorized Access

1. Đăng xuất
2. Thử đăng nhập bằng email khác (không trong whitelist)
3. ✅ Phải thấy thông báo: "Email của bạn không được phép truy cập!"

### 4.3. Test Windows Client

1. Chạy Windows Client: `START.bat`
2. ✅ Vẫn phải hoạt động bình thường (không cần login)
3. Windows Client dùng Firebase Admin SDK nên bypass rules

---

## 🔒 Các Lớp Bảo Mật

Sau khi setup xong, hệ thống có **3 lớp bảo mật**:

### Lớp 1: Email Whitelist (Frontend)
- Kiểm tra ngay khi login
- Chặn email không được phép

### Lớp 2: Firebase Authentication
- Chỉ user đã login mới gọi Firebase API được
- Firebase Rules yêu cầu `auth != null`

### Lớp 3: Firebase Rules (Backend)
- Kiểm tra lại phía server
- Chặn truy cập trực tiếp vào database

---

## ⚠️ VẤN ĐỀ VẪN CÒN TỒN TẠI

### 1. Firebase Credentials Vẫn Public

❌ **Vấn đề:** Firebase config vẫn hiển thị trong HTML source code

**Tại sao không nghiêm trọng:**
- Firebase config **ĐƯỢC PHÉP** public (theo Google)
- Bảo mật thật sự ở **Firebase Rules**
- Chỉ cần Rules đúng là an toàn

**Nếu muốn ẩn hoàn toàn:**
- Cần setup Firebase Backend (Cloud Functions)
- Chi phí ~$25/tháng
- Phức tạp hơn nhiều

**Quyết định:** GIỮ NGUYÊN (đủ an toàn cho use case này)

### 2. Windows Client Credentials

✅ **An toàn:** Windows Client dùng Service Account credentials trong `config.py`

**Lý do:**
- File `config.py` chỉ ở local máy con
- Không public lên internet
- Con không thể xem được (nếu máy bị khóa)

---

## 🎯 Checklist Sau Khi Setup

- [ ] Firebase Rules đã publish
- [ ] Google Authentication đã bật
- [ ] Email whitelist đã thay đúng
- [ ] Web App đã deploy lại
- [ ] Test login thành công
- [ ] Test email unauthorized bị chặn
- [ ] Windows Client vẫn hoạt động

---

## 🆘 Nếu Gặp Lỗi

### Lỗi: "Permission denied"

**Nguyên nhân:** Firebase Rules chặn

**Giải pháp:**
1. Kiểm tra đã đăng nhập chưa
2. Kiểm tra email có trong whitelist không
3. Xem Console logs (F12 → Console)

### Lỗi: "auth/popup-blocked"

**Nguyên nhân:** Browser chặn popup

**Giải pháp:**
1. Cho phép popup cho site này
2. Hoặc dùng Incognito mode

### Lỗi: Windows Client không kết nối được

**Nguyên nhân:** Có thể do Rules chặn

**Giải pháp:**
- Windows Client phải dùng Service Account
- Kiểm tra `config.py` có đúng credentials không

---

**LƯU FILE NÀY ĐỂ THAM KHẢO!** 📖
