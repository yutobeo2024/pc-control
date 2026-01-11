# Windows Client - Parental Control

Ứng dụng chạy trên máy tính con, quản lý khóa/mở máy và theo dõi thời gian sử dụng.

## Tính năng

1. **Màn hình khóa toàn màn hình** khi khởi động
2. **Đồng hồ đếm ngược** hiển thị góc màn hình
3. **Tự động khóa** khi hết thời gian
4. **Đồng bộ real-time** với Firebase

## Cài đặt

```bash
pip install -r requirements.txt
```

## Cấu hình

1. Mở file `config.py`
2. Thay thế các giá trị Firebase config từ Firebase Console
3. Lưu file

## Chạy

```bash
python main.py
```

## Cấu trúc File

- `main.py` - Entry point, quản lý app chính
- `firebase_handler.py` - Xử lý kết nối Firebase
- `lock_screen.py` - Màn hình khóa
- `timer_widget.py` - Đồng hồ đếm ngược
- `config.py` - Cấu hình Firebase (KHÔNG commit file này)

## Chạy khi Khởi động Windows

### Cách 1: Startup Folder

1. Tạo file `run.bat`:
```bat
@echo off
pythonw "D:\yuto control\windows-client\main.py"
```

2. Copy shortcut của `run.bat` vào:
```
C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

### Cách 2: Task Scheduler

1. Mở Task Scheduler
2. Create Task:
   - **Name:** Parental Control Client
   - **Trigger:** At startup
   - **Action:** Start a program
     - Program: `pythonw.exe`
     - Arguments: `"D:\yuto control\windows-client\main.py"`
   - **Run with highest privileges:** ✓

## Gỡ lỗi

### Test Firebase Connection

```bash
python -c "from firebase_handler import FirebaseHandler; fb = FirebaseHandler(); print(f'Device ID: {fb.get_device_id()}')"
```

### Xem Device ID

```bash
type device_id.txt
```

### Log Output

Chạy với console để xem log:
```bash
python main.py
```

## Lưu ý

- Cần quyền Administrator để khóa màn hình hiệu quả
- File `device_id.txt` được tạo tự động và không nên xóa
- Mỗi máy tính có Device ID riêng biệt
