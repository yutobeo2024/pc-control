# 🛡️ Tính năng An toàn - Safety Features

Để tránh bị khóa máy vĩnh viễn khi webapp/server gặp sự cố.

---

## 🚨 Emergency Unlock Hotkey

### Cách sử dụng:

Khi máy bị khóa và webapp không hoạt động:

1. **Bấm tổ hợp phím:** `Ctrl + Shift + Alt + U`
2. **Nhập password admin:** `admin123` (mặc định)
3. **Máy sẽ mở khóa ngay lập tức**

### Thay đổi password:

Mở file `config.py` và sửa:

```python
EMERGENCY_UNLOCK_PASSWORD = "your_new_password"
```

### Vô hiệu hóa (KHÔNG khuyến nghị):

```python
EMERGENCY_UNLOCK_ENABLED = False  # Chỉ tắt nếu bạn chắc chắn 100%
```

---

## 🔄 Firebase Connection Retry

Nếu không kết nối được Firebase:

- Console sẽ hiện: `⚠️ Cannot connect to Firebase - check internet connection`
- Hệ thống sẽ tự động retry mỗi 2 giây (cấu hình `CHECK_INTERVAL`)

---

## 📊 Workflow Xử lý Lỗi

### Kịch bản 1: Webapp lỗi
```
1. Bấm Ctrl+Shift+Alt+U
2. Nhập password admin
3. ✅ Máy mở khóa
4. Slack nhận thông báo: "🆘 EMERGENCY UNLOCK"
```

### Kịch bản 2: Mất kết nối Firebase
```
1. Console hiện: "⚠️ Cannot connect to Firebase"
2. Dùng Emergency Hotkey: Ctrl+Shift+Alt+U
3. ✅ Máy mở khóa
```

### Kịch bản 3: Từ chối request
```
1. Phụ huynh bấm "Từ chối"
2. Windows Client tự động gửi request mới
3. Request mới hiện lên Web App ngay lập tức
```

---

## ��️ Cấu hình An toàn Khuyến nghị

File `config.py`:

```python
# ✅ LUÔN BẬT để phòng lỗi
EMERGENCY_UNLOCK_ENABLED = True

# ⚠️ ĐỔI MẬT KHẨU MẶC ĐỊNH
EMERGENCY_UNLOCK_PASSWORD = "your_strong_password_here"  # KHÔNG dùng "admin123"
```

**Lưu ý quan trọng:**
- Password nên dài ít nhất 8 ký tự
- Kết hợp chữ hoa, chữ thường, số
- Backup password ở nơi an toàn (nếu quên phải khởi động lại máy)

---

## 🎯 Kiểm tra Tính năng

### Test Emergency Unlock:

1. Chạy Windows Client
2. Chờ màn hình khóa xuất hiện
3. Bấm `Ctrl+Shift+Alt+U`
4. Nhập password
5. Kiểm tra xem máy mở khóa không

### Test Request Reject:

1. Mở Web App
2. Bấm "Từ chối"
3. Kiểm tra console → Request mới sẽ xuất hiện ngay

---

## ⚠️ Lưu ý Quan trọng

1. **Luôn bật EMERGENCY_UNLOCK_ENABLED** - đây là cách duy nhất để unlock khi webapp/server lỗi
2. **Đổi password mặc định** `admin123` thành password mạnh
3. **Backup password** ở nơi an toàn (nếu quên sẽ phải khởi động lại máy)
4. **Test Emergency Unlock** trước khi setup auto-start with Windows
5. **Giữ bí mật password** - đừng để con biết!

---

## 🆘 Nếu Bị Khóa Vĩnh viễn

1. **Thử Emergency Hotkey:** `Ctrl+Shift+Alt+U`
2. **Nếu quên password:** Khởi động lại máy
3. **Vào Safe Mode:** Boot vào Safe Mode → Tắt auto-start
4. **Kill process:** Ctrl+Shift+Esc (nếu Task Manager mở được) → Kill Python

---

**Lưu file này để tham khảo khi cần!** 📖
