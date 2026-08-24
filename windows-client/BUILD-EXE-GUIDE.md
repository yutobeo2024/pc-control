# Đóng gói thành .exe độc lập

Gói toàn bộ client thành **một file `ParentalControl.exe`** chạy được trên máy
con mà **không cần cài Python**. Copy một file, chạy, xong.

---

## Vì sao nên dùng bản .exe

| | Bản Python (`main.py`) | Bản đóng gói (`.exe`) |
|---|---|---|
| Cài Python trên máy con | Cần | **Không cần** |
| Cài `pip install` | Cần | **Không cần** |
| Số file phải copy | Cả thư mục | **1 file** |
| Kích thước | Nhỏ | ~78 MB |
| Đổi cấu hình sau khi cài | Sửa `config.py` | Phải build lại |

Bản .exe **nhúng luôn `config.py`** (Firebase config + mật khẩu khẩn cấp), nên
cấu hình một lần trên máy build rồi copy exe đi khắp nơi.

---

## Build (làm 1 lần, trên MÁY CÓ PYTHON)

### 1. Cấu hình trước khi build

Vì config bị nhúng vào exe, phải làm xong bước này **trước**:

```bash
cd windows-client
copy config.example.py config.py     # rồi điền FIREBASE_CONFIG
python set_password.py               # đổi mật khẩu khẩn cấp
```

### 2. Build

```bash
build-exe.bat
```

Hoặc thủ công:

```bash
pip install pyinstaller
python -m PyInstaller ParentalControl.spec --noconfirm --clean
```

Mất 1-3 phút. Kết quả: **`dist\ParentalControl.exe`**

### 3. Kiểm tra nhanh

Chạy thử `dist\ParentalControl.exe` trên chính máy build. Màn hình khóa hiện ra
= chạy được. Mở web app duyệt để mở lại, rồi thoát qua system tray (nhập mật khẩu).

---

## Cài lên máy con

### 1. Copy sang máy con

Chỉ cần **`ParentalControl.exe`** + **`setup_autostart_exe.bat`**. Đặt cùng một
thư mục cố định, ví dụ `C:\ParentalControl\`.

> ⚠️ **Đừng copy kèm `device_id.txt`.** Mỗi máy phải tự sinh ID riêng ở lần chạy
> đầu. Chép ID trùng nhau = hai máy tranh một node Firebase, mở máy này thì máy
> kia cũng mở.

### 2. Chạy thử 1 lần

Double-click `ParentalControl.exe`. Lần đầu nó tạo `device_id.txt` **cạnh exe**.
Mở web app → thấy máy mới xuất hiện → duyệt để test.

### 3. Bật auto-start

Chuột phải `setup_autostart_exe.bat` → **Run as administrator**.

Từ lần khởi động sau, app tự chạy ngầm khi đăng nhập Windows (không cửa sổ
console vì spec đặt `console=False`).

Gỡ auto-start: `remove_autostart.bat` (dùng chung cho cả 2 bản).

---

## Nhiều máy

Build **một lần**, copy `ParentalControl.exe` sang bao nhiêu máy tùy ý. Mỗi máy:

- Tự sinh `device_id.txt` riêng ở lần chạy đầu → hiện thành thiết bị riêng
- Dùng chung Firebase config và (nếu đặt giống) mật khẩu khẩn cấp đã nhúng
- Quản lý tất cả từ cùng một tài khoản phụ huynh trên web app

Muốn đổi Firebase config hay mật khẩu → sửa `config.py` trên máy build rồi
build lại, copy exe mới đè lên (giữ nguyên `device_id.txt` trên máy con).

---

## Các file runtime (tạo cạnh exe, riêng từng máy)

| File | Vai trò | Nguồn |
|---|---|---|
| `device_id.txt` | ID thiết bị, riêng mỗi máy | Tự sinh lần đầu |
| `slack_webhook.txt` | Webhook Slack (tùy chọn) | `ParentalControl.exe` không tạo — copy tay nếu muốn Slack |

`paths.py` bảo đảm các file này nằm cạnh exe (không phải thư mục tạm), nhờ đó
tồn tại lâu dài qua các lần khởi động.

---

## Xử lý sự cố

| Triệu chứng | Nguyên nhân |
|---|---|
| Exe mở rồi tắt ngay, không thấy gì | Chạy `smoke_test` hoặc bản `run-debug.bat` để xem lỗi. Thường do sai `FIREBASE_CONFIG` đã nhúng |
| `device_id` đổi mỗi lần khởi động | Exe không ghi được cạnh nó — đặt vào thư mục có quyền ghi (đừng để trong `C:\Program Files\`) |
| SmartScreen chặn "Windows protected your PC" | Exe chưa ký số. Bấm "More info" → "Run anyway". Muốn hết cần mua code-signing certificate |
| Diệt virus báo nhầm | Thường gặp với exe PyInstaller chưa ký. Thêm ngoại lệ, hoặc ký số |
| Máy con là 32-bit | Build trên máy 32-bit (exe theo kiến trúc máy build) |

> **Lưu ý:** exe build trên Windows 64-bit chỉ chạy trên Windows 64-bit. Build
> trên đúng loại kiến trúc/phiên bản Windows gần với máy con nhất.
