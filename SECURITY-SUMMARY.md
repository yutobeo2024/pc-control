# 🔐 Tóm Tắt Bảo Mật

## ✅ ĐÃ SỬA:

### **Vấn đề CŨ:**
```javascript
// ❌ Email lộ ra ngoài trong index.html
const ALLOWED_EMAILS = [
    'hanhtoami@gmail.com',
    'thuydungsp@gmail.com'
];
```

### **Giải pháp MỚI:**
- ✅ **BỎ** email whitelist khỏi frontend
- ✅ **CHUYỂN** whitelist sang Firebase Rules (server-side)
- ✅ Email giờ chỉ nằm trong Firebase Console, KHÔNG ai xem được

---

## 🛡️ CÁC LỚP BẢO MẬT:

### **Lớp 1: Firebase Authentication**
- Bắt buộc đăng nhập Google
- Không đăng nhập = không dùng được app

### **Lớp 2: Firebase Security Rules**
- Kiểm tra email ở **SERVER-SIDE**
- CHỈ 2 email được phép: `hanhtoami@gmail.com` và `thuydungsp@gmail.com`
- Không thể bypass vì chạy trên Firebase server

### **Lớp 3: Permission Test**
- Frontend thử đọc database
- Nếu bị từ chối (Permission Denied) → Đăng xuất ngay

---

## 📋 CHECKLIST SETUP:

- [ ] **Firebase Rules** đã cập nhật với email của bạn
- [ ] **Google Authentication** đã bật trong Firebase Console
- [ ] **Web App** đã deploy lại lên Netlify
- [ ] **Test login** với email của bạn → Thành công
- [ ] **Test login** với email khác → Bị chặn
- [ ] **Windows Client** vẫn hoạt động bình thường

---

## 🔥 CẦN LÀM NGAY:

### **1. Cập nhật Firebase Rules:**

Vào Firebase Console → Realtime Database → Rules → dán **toàn bộ** nội dung
file [`firebase/database.rules.json`](firebase/database.rules.json), sửa email
cho đúng tài khoản của bạn, rồi bấm **Publish**.

> ⚠️ Đừng chép rules từ tài liệu — chỉ dùng `firebase/database.rules.json`.
> Trước đây dự án có 3 bản rules khác nhau nằm rải rác, rất dễ deploy nhầm bản
> `test mode` (`.read: true / .write: true`) khiến database mở toang.

### **2. Deploy Web App:**

Kéo folder `web-app/public` vào Netlify.

---

## ⚠️ HẠN CHẾ ĐÃ BIẾT (chưa sửa)

### **1. Client vẫn truy cập Firebase mà không đăng nhập** (đã giảm nhẹ)

**Trước bản vá:** rules cho phép `auth == null` ở **mức collection**, nghĩa là
bất kỳ ai biết `databaseURL` (nằm công khai trong `index.html`) đều có thể:

```bash
curl ".../devices.json"              # liệt kê toàn bộ thiết bị
curl -X DELETE ".../devices.json"    # xóa sạch database
```

Đã kiểm chứng thực tế: HTTP 200, không cần token.

**Sau bản vá:** `auth == null` chỉ còn ở **mức từng node lẻ**:

| | Người ngoài | Windows client | Phụ huynh |
|---|---|---|---|
| `GET /devices.json` (liệt kê) | ❌ chặn | không dùng | ✅ |
| `DELETE /devices.json` (xóa sạch) | ❌ chặn | không dùng | ✅ |
| `GET/PATCH /devices/<uuid>.json` | ⚠️ được, nếu biết UUID | ✅ | ✅ |

Rules Firebase cascade theo hướng **cấp quyền** — rule cha `false` không chặn
rule con `true` — nên client vẫn chạy bình thường dù mức collection đã đóng.

Kiểm chứng bằng: `python firebase/verify-rules.py` (kỳ vọng **8/8**).

**Còn lại:** ai biết chính xác device UUID vẫn ghi được vào node đó. UUID không
đoán và không liệt kê được nữa — nhưng **đứa con biết**, vì nó nằm trong
`windows-client/device_id.txt` trên máy nó.

**Sửa tận gốc:** cho client đăng nhập bằng Firebase Anonymous Auth, dùng `uid`
làm device ID, rồi siết `$deviceId` về `auth != null && auth.uid == $deviceId`.

### **2. Lock screen là "khóa mềm"**

Client chặn được Alt+Tab, phím Windows, Alt+F4, Ctrl+Esc (xem
`windows-client/input_blocker.py`), nhưng **không chặn được `Ctrl+Alt+Del`** —
Windows bảo lưu tổ hợp này. Từ đó vào Task Manager kill `pythonw.exe` là thoát
được.

Đây là giới hạn thật của mọi giải pháp chạy ở user-mode. Chặn triệt để cần:
- Cho con dùng tài khoản Windows **standard** (không phải admin)
- Chạy phần canh giữ dưới dạng **Windows Service**
- Hoặc khóa Task Manager bằng Group Policy

### **3. Không có rate limit**

Không giới hạn số lần gửi yêu cầu mở khóa. Client tự giới hạn bằng
`REJECT_RETRY_DELAY` (30 giây), nhưng đây là ràng buộc phía client, không phải
phía server.

---

## 🎯 KẾT QUẢ:

### **Trước khi sửa:**
- ❌ Email public trong HTML source
- ❌ Ai cũng xem được email của bạn

### **Sau khi sửa:**
- ✅ Email CHỈ nằm trong Firebase Rules (server-side)
- ✅ KHÔNG ai xem được email
- ✅ Chỉ bạn và vợ truy cập được database
- ✅ Email khác đăng nhập cũng bị chặn

---

## 📖 Chi Tiết Đầy Đủ:

Xem file [FIREBASE-SECURITY-SETUP.md](FIREBASE-SECURITY-SETUP.md)
