"""
Timer Widget - Đồng hồ đếm ngược hiển thị góc màn hình
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class TimerWidget(QWidget):
    time_expired = pyqtSignal()
    warning_shown = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.time_remaining = 0
        self.warning_triggered = False
        self.init_ui()

    def init_ui(self):
        """Khởi tạo giao diện đồng hồ đếm ngược"""
        # Cài đặt cửa sổ
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)

        # Icon đồng hồ
        clock_icon = QLabel("⏱️")
        clock_icon.setAlignment(Qt.AlignCenter)
        icon_font = QFont("Segoe UI Emoji", 20)
        clock_icon.setFont(icon_font)

        # Label thời gian
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        time_font = QFont("Consolas", 24, QFont.Bold)
        self.time_label.setFont(time_font)

        layout.addWidget(clock_icon)
        layout.addWidget(self.time_label)

        self.setLayout(layout)

        # Màu nền
        self.update_background_color(False)

        # Timer đếm ngược
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_timer)
        self.countdown_timer.start(1000)  # Cập nhật mỗi giây

        # Vị trí góc phải trên màn hình
        self.setGeometry(1700, 20, 200, 100)

    def update_background_color(self, warning=False):
        """Cập nhật màu nền (đỏ khi sắp hết giờ)"""
        palette = self.palette()
        if warning:
            palette.setColor(QPalette.Window, QColor(200, 50, 50, 230))
        else:
            palette.setColor(QPalette.Window, QColor(50, 50, 50, 230))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def set_time(self, seconds):
        """Đặt thời gian còn lại (tự khởi động lại đồng hồ nếu đang dừng)"""
        self.time_remaining = seconds
        self.warning_triggered = False
        self.update_background_color(False)
        self.update_display()
        if not self.countdown_timer.isActive():
            self.countdown_timer.start(1000)

    def stop(self):
        """Dừng đếm ngược. Gọi khi khóa máy - hide() không dừng QTimer."""
        self.countdown_timer.stop()
        self.hide()

    def update_timer(self):
        """Cập nhật đồng hồ đếm ngược"""
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_display()

            # Cảnh báo khi còn 10 phút
            if self.time_remaining <= 600 and not self.warning_triggered:
                self.warning_triggered = True
                self.update_background_color(True)
                self.warning_shown.emit()

            # Hết giờ
            if self.time_remaining == 0:
                self.time_expired.emit()

    def update_display(self):
        """Cập nhật hiển thị thời gian"""
        hours = self.time_remaining // 3600
        minutes = (self.time_remaining % 3600) // 60
        seconds = self.time_remaining % 60

        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.time_label.setText(time_str)

    def add_time(self, seconds):
        """Thêm thời gian"""
        self.time_remaining += seconds
        if self.time_remaining > 600:
            self.update_background_color(False)
            self.warning_triggered = False
        self.update_display()


class WarningDialog(QWidget):
    """Hộp thoại cảnh báo khi sắp hết giờ"""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Khởi tạo giao diện cảnh báo"""
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint
        )

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Icon cảnh báo
        warning_icon = QLabel("⚠️")
        warning_icon.setAlignment(Qt.AlignCenter)
        icon_font = QFont("Segoe UI Emoji", 50)
        warning_icon.setFont(icon_font)

        # Thông báo
        message = QLabel("Còn 10 phút!\nMáy tính sẽ bị khóa khi hết giờ")
        message.setAlignment(Qt.AlignCenter)
        message_font = QFont("Segoe UI", 18, QFont.Bold)
        message.setFont(message_font)

        layout.addWidget(warning_icon)
        layout.addSpacing(10)
        layout.addWidget(message)

        self.setLayout(layout)

        # Màu nền vàng cam
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 160, 0))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Kích thước và vị trí giữa màn hình
        self.setFixedSize(400, 200)

        # Tự động đóng sau 5 giây
        QTimer.singleShot(5000, self.close)

    def show_warning(self):
        """Hiển thị cảnh báo ở giữa màn hình"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        self.show()
