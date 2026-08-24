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

**Rules MỚI:** dán **toàn bộ** nội dung file
[`firebase/database.rules.json`](firebase/database.rules.json), rồi sửa hai
email trong đó thành email của bạn và vợ.

> ⚠️ `firebase/database.rules.json` là **nguồn duy nhất** cho Security
> Rules. Đừng chép rules từ tài liệu này hay bất kỳ file .md nào khác — trước
> đây dự án có nhiều bản rules mâu thuẫn nằm rải rác và rất dễ deploy nhầm.

**Giải thích cấu trúc rules — 2 tầng:**

*Tầng collection* (`devices`, `requests`) — chỉ phụ huynh:
```
"auth != null && (auth.token.email == 'email-1' || auth.token.email == 'email-2')"
```

*Tầng node* (`$deviceId`, `$requestId`) — thêm cửa cho Windows client:
```
"auth == null || (auth.token.email == 'email-1' || auth.token.email == 'email-2')"
```

Vì sao chia 2 tầng: Windows client dùng `pyrebase` và **không đăng nhập**, nên
bắt buộc phải chấp nhận `auth == null` ở đâu đó. Nhưng client chỉ đọc/ghi
**từng node lẻ**, không bao giờ đụng cả collection — nên chỉ cần mở ở tầng node.

Kết quả: người ngoài không `GET /devices.json` để liệt kê, cũng không
`DELETE /devices.json` để xóa sạch được nữa.

Rules Firebase **cascade theo hướng cấp quyền**: rule cha trả `false` KHÔNG
chặn rule con trả `true`. Nên đóng tầng collection không làm hỏng client.

`.indexOn: ["status", "timestamp"]` ở nhánh `requests` → để web app query được
các request đang pending mà không phải tải cả nhánh.

**Kiểm chứng sau khi Publish:**

```bash
cd firebase
python verify-rules.py
```

Script gửi request không kèm token và kiểm tra cả hai chiều: người ngoài bị
chặn, client vẫn chạy được. Kỳ vọng **8/8**.

**Vẫn còn hở:** ai biết chính xác device UUID vẫn ghi được vào node đó. Sửa tận
gốc cần Firebase **Anonymous Auth** — xem
[SECURITY-SUMMARY.md](SECURITY-SUMMARY.md).

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

### Lớp 1: Google Authentication (Web App)
- Bắt buộc đăng nhập Google mới vào được web app
- Sau khi login, frontend thử đọc database; bị từ chối thì tự đăng xuất

### Lớp 2: Firebase Rules (Backend)
- Whitelist email kiểm tra ở phía server, không bypass được từ frontend
- Email không nằm trong frontend nên không lộ ra ngoài

### ⚠️ Lớp 2 hiện đang bị vô hiệu hóa một phần

Rules có nhánh `auth == null` (để Windows client hoạt động) được kiểm tra
**trước** whitelist email. Người truy cập thẳng vào `databaseURL` mà không
đăng nhập sẽ khớp nhánh này và có toàn quyền đọc/ghi.

Nghĩa là hiện tại whitelist chỉ chặn được người đã đăng nhập bằng email lạ,
không chặn được người không đăng nhập. Xem mục "VẤN ĐỀ VẪN CÒN TỒN TẠI" bên dưới.

---

## ⚠️ VẤN ĐỀ VẪN CÒN TỒN TẠI

### 1. Rules cho phép `auth == null` — điểm yếu chính

❌ **Vấn đề:** Rules hiện tại có nhánh `auth == null` để Windows client
(không đăng nhập) hoạt động được. Kết hợp với `databaseURL` nằm công khai
trong `web-app/public/index.html`, **bất kỳ ai cũng đọc/ghi được database mà
không cần đăng nhập** — mở khóa máy, xóa dữ liệu.

Google Auth và whitelist email chỉ chặn được người dùng đã đăng nhập; nhánh
`auth == null` được kiểm tra trước nên trên thực tế whitelist không có tác dụng.

**Hướng khắc phục:**
1. Cho Windows client đăng nhập bằng Firebase **Anonymous Auth** (pyrebase hỗ
   trợ `auth().sign_in_anonymous()`), lưu lại `uid`
2. Đổi rules: `auth != null && (auth.uid == 'uid-cua-client' || auth.token.email == '...')`
3. Client refresh token định kỳ (token Firebase hết hạn sau 1 giờ)

**Chưa làm** — đây là việc cần làm tiếp theo nếu muốn hệ thống thật sự kín.

### 2. Firebase Credentials Public trong HTML

⚠️ **Vấn đề:** Firebase config hiển thị trong HTML source code

**Tại sao bình thường không nghiêm trọng:**
- Firebase web config **ĐƯỢC PHÉP** public (theo Google)
- Bảo mật thật sự nằm ở Firebase Rules

**Nhưng ở dự án này thì có:** vì Rules đang mở cho `auth == null` (mục 1),
`databaseURL` public đồng nghĩa với database public. Sửa mục 1 thì mục này
trở lại vô hại.

### 3. Windows Client Credentials

⚠️ Windows client dùng **cùng một Firebase web config** như web app
(apiKey/databaseURL public), **không phải** service account.

- `config.py` đã được `.gitignore` nên không lộ lên GitHub
- Nhưng giá trị bên trong giống hệt cái đã public trong `index.html`
- Nghĩa là giữ bí mật `config.py` không mang lại thêm bảo mật nào

Mật khẩu emergency unlock trong `config.py` thì có giá trị bảo mật thật —
và đã được lưu dạng SHA-256 hash thay vì plaintext.

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
