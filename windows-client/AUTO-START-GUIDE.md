# 🚀 Hướng Dẫn Cài Đặt Auto-Start

Hướng dẫn cài đặt Parental Control Client tự động chạy khi Windows khởi động.

---

## ⚡ Cách Nhanh: Sử dụng Task Scheduler (KHUYẾN NGHỊ)

### Cài đặt Auto-Start:

1. **Right-click** file `setup_autostart.bat`
2. Chọn **"Run as administrator"**
3. Chờ thông báo "SUCCESS!"
4. Xong! Khởi động lại Windows để test

### Gỡ bỏ Auto-Start:

1. **Right-click** file `remove_autostart.bat`
2. Chọn **"Run as administrator"**
3. Xong!

---

## 🔍 Kiểm Tra Auto-Start

### Cách 1: Khởi động lại Windows

1. Khởi động lại máy
2. Sau khi đăng nhập Windows, màn hình khóa Parental Control phải tự động hiện lên
3. ✅ Nếu thấy màn hình khóa → Auto-start hoạt động!

### Cách 2: Kiểm tra Task Scheduler

1. Bấm `Win + R`
2. Gõ `taskschd.msc` và Enter
3. Tìm task tên **"ParentalControlClient"**
4. Click phải → **Run** để test ngay

---

## ⚙️ Cấu Hình Task Scheduler

Task đã được cấu hình với các thiết lập tối ưu:

✅ **Run with highest privileges** - Chạy với quyền admin
✅ **Run whether user is logged on or not** - Chạy ngay cả khi chưa login
✅ **Hidden** - Ẩn cửa sổ console
✅ **Start when available** - Tự khởi động lại nếu bị miss
✅ **Don't stop on battery** - Không tắt khi dùng pin (laptop)

---

## 🛠️ Cách Khác: Registry Startup (Đơn giản hơn, nhưng không ẩn console)

Nếu không muốn dùng Task Scheduler:

### Setup:

1. Bấm `Win + R`
2. Gõ `shell:startup` và Enter
3. Tạo shortcut đến `START.bat` trong folder này
4. Khởi động lại Windows

### Remove:

1. Bấm `Win + R`
2. Gõ `shell:startup` và Enter
3. Xóa shortcut đã tạo

**Nhược điểm:** Cửa sổ console sẽ hiển thị, không ẩn được.

---

## ⚠️ LƯU Ý QUAN TRỌNG

### Trước khi enable auto-start:

1. ✅ **TEST Emergency Unlock** trước:
   - Chạy Windows Client thủ công
   - Bấm `Ctrl+Shift+Alt+U`
   - Nhập password admin (mặc định `admin123`)
   - Xác nhận máy mở khóa được

2. ✅ **ĐỔI password mặc định** trong `config.py`:
   ```python
   EMERGENCY_UNLOCK_PASSWORD = "your_strong_password"
   ```

3. ✅ **BACKUP password** ở nơi an toàn (giấy viết tay, file text riêng)

### Nếu quên password Emergency Unlock:

1. Khởi động lại Windows
2. Bấm F8 ngay khi khởi động → Chọn **Safe Mode**
3. Vào Task Scheduler → Disable task "ParentalControlClient"
4. Khởi động lại bình thường
5. Sửa password trong `config.py`
6. Enable lại task

---

## 🎯 Test Auto-Start

**Test 1: Khởi động lại máy**
```
1. Khởi động lại Windows
2. Đăng nhập
3. Màn hình khóa phải tự động hiện ra
4. ✅ Success!
```

**Test 2: Emergency Unlock**
```
1. Sau khi auto-start
2. Bấm Ctrl+Shift+Alt+U
3. Nhập password
4. Máy phải mở khóa
5. ✅ Success!
```

**Test 3: Web App Control**
```
1. Mở https://yutokun.netlify.app/ trên điện thoại
2. Bấm "Cho phép"
3. Máy phải mở khóa
4. ✅ Success!
```

---

## 🔧 Troubleshooting

### Vấn đề: Auto-start không chạy

**Kiểm tra:**
1. Vào Task Scheduler → Tìm task "ParentalControlClient"
2. Click phải → Properties → History tab
3. Xem lỗi gì

**Giải pháp phổ biến:**
- Chưa chạy `setup_autostart.bat` as Administrator
- Python không có trong PATH
- Sai đường dẫn file `main.py`

### Vấn đề: Cửa sổ console hiện ra

**Giải pháp:**
- Đảm bảo dùng `pythonw.exe` (không phải `python.exe`)
- Task Scheduler đã được cấu hình đúng với `pythonw.exe`

### Vấn đề: Máy chạy chậm khi startup

**Giải pháp:**
- Vào Task Scheduler → Task Properties
- Tab "Conditions" → Bỏ tick "Start the task only if the computer is on AC power"
- Tab "Settings" → Tick "Allow task to be run on demand"

---

## 📋 Checklist Hoàn Chỉnh

Trước khi enable auto-start, check tất cả:

- [ ] Emergency Unlock đã test thành công
- [ ] Password đã đổi khỏi `admin123` (chạy `python set_password.py`)
- [ ] Password đã backup ở nơi an toàn
- [ ] Web App login thành công
- [ ] Web App approve/reject hoạt động
- [ ] Lock buttons hoạt động (khóa ngay, sau 30p, 1h, etc.)
- [ ] Windows Client kết nối Firebase thành công
- [ ] Đã test thủ công Windows Client chạy OK

Nếu tất cả đều ✅ → An toàn để enable auto-start!

---

## 🆘 Nếu Bị Khóa Vĩnh Viễn

1. **Khởi động lại máy**
2. **Boot vào Safe Mode** (F8 khi khởi động)
3. **Disable task** trong Task Scheduler
4. **Khởi động lại** bình thường
5. **Fix lỗi** rồi enable lại

---

**🎉 DONE! Hệ thống Parental Control giờ đã tự động chạy mỗi khi Windows khởi động!**
