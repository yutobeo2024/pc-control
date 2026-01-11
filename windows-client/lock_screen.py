"""
Lock Screen - Màn hình khóa toàn màn hình
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class LockScreen(QWidget):
    unlock_requested = pyqtSignal()
    emergency_unlock = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Khởi tạo giao diện màn hình khóa"""
        # Cài đặt cửa sổ toàn màn hình
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint
        )
        self.showFullScreen()

        # Bắt buộc nhận focus để chặn input
        self.setFocus()
        self.activateWindow()
        self.raise_()

        # Tạo layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Icon khóa
        lock_icon = QLabel("🔒")
        lock_icon.setAlignment(Qt.AlignCenter)
        lock_font = QFont("Segoe UI Emoji", 80)
        lock_icon.setFont(lock_font)

        # Tiêu đề
        title = QLabel("Máy tính đã bị khóa")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 32, QFont.Bold)
        title.setFont(title_font)

        # Thông báo chờ
        self.message = QLabel("Đang chờ phụ huynh cho phép...")
        self.message.setAlignment(Qt.AlignCenter)
        message_font = QFont("Segoe UI", 18)
        self.message.setFont(message_font)

        # Error message
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        error_font = QFont("Segoe UI", 12)
        self.error_label.setFont(error_font)
        self.error_label.setStyleSheet("color: #FF4444;")

        # Hiệu ứng loading (dấu chấm nhảy)
        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self.animate_dots)
        self.dots_count = 0
        self.dots_timer.start(500)

        # Device ID info
        self.device_info = QLabel("")
        self.device_info.setAlignment(Qt.AlignCenter)
        info_font = QFont("Segoe UI", 10)
        self.device_info.setFont(info_font)
        self.device_info.setStyleSheet("color: #888;")

        # Thêm vào layout
        layout.addWidget(lock_icon)
        layout.addSpacing(20)
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(self.message)
        layout.addSpacing(10)
        layout.addWidget(self.error_label)
        layout.addSpacing(30)
        layout.addWidget(self.device_info)

        self.setLayout(layout)

        # Thiết lập màu nền
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Timer để đảm bảo luôn ở trên cùng
        self.stay_on_top_timer = QTimer()
        self.stay_on_top_timer.timeout.connect(self.ensure_on_top)
        self.stay_on_top_timer.start(500)  # Kiểm tra mỗi 0.5 giây

    def ensure_on_top(self):
        """Đảm bảo cửa sổ luôn ở trên cùng"""
        self.raise_()
        self.activateWindow()

    def animate_dots(self):
        """Hiệu ứng loading với dấu chấm"""
        self.dots_count = (self.dots_count + 1) % 4
        dots = "." * self.dots_count
        self.message.setText(f"Đang chờ phụ huynh cho phép{dots}")

    def set_device_id(self, device_id):
        """Hiển thị Device ID"""
        self.device_info.setText(f"Device ID: {device_id[:8]}...")

    def set_message(self, message):
        """Cập nhật thông báo"""
        self.dots_timer.stop()
        self.message.setText(message)

    def show_error_message(self, message):
        """Hiển thị thông báo lỗi"""
        self.error_label.setText(message)
        # Tự động xóa sau 3 giây
        QTimer.singleShot(3000, lambda: self.error_label.setText(""))

    def keyPressEvent(self, event):
        """Chặn phím tắt và xử lý emergency unlock"""
        # Emergency unlock: Ctrl+Shift+Alt+U
        if (event.key() == Qt.Key_U and
            event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier | Qt.AltModifier)):
            print("🚨 Emergency unlock hotkey pressed!")
            self.emergency_unlock.emit()
            return

        # Chặn tất cả phím khác
        event.ignore()

    def closeEvent(self, event):
        """Ngăn đóng cửa sổ"""
        event.ignore()


class ApprovedScreen(QWidget):
    """Màn hình hiển thị khi được phê duyệt"""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Khởi tạo giao diện màn hình phê duyệt"""
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint
        )
        self.showFullScreen()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Icon mở khóa
        unlock_icon = QLabel("✅")
        unlock_icon.setAlignment(Qt.AlignCenter)
        icon_font = QFont("Segoe UI Emoji", 80)
        unlock_icon.setFont(icon_font)

        # Thông báo
        message = QLabel("Phụ huynh đã cho phép!\nMáy tính sẽ mở khóa...")
        message.setAlignment(Qt.AlignCenter)
        message_font = QFont("Segoe UI", 24)
        message.setFont(message_font)

        layout.addWidget(unlock_icon)
        layout.addSpacing(20)
        layout.addWidget(message)

        self.setLayout(layout)

        # Màu nền xanh lá nhạt
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(40, 120, 80))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Tự động đóng sau 2 giây
        QTimer.singleShot(2000, self.close)
