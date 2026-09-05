"""
Timer Widget - Đồng hồ đếm ngược hiển thị góc màn hình
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import config

# Còn bao nhiêu giây thì cảnh báo. Trước đây hằng số 600 nằm rải rác trong file
# này nên config.WARNING_TIME không có tác dụng gì.
WARNING_TIME = getattr(config, "WARNING_TIME", 600)

# Hộp thoại cảnh báo tự đóng sau bao nhiêu mili giây
WARNING_AUTO_CLOSE_MS = 5000


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
        # KHÔNG đặt cứng False. handle_unlocked_state gọi set_time() mỗi lần
        # lệch quá 5 giây với Firebase; nếu reset ở đây thì mỗi lần đồng bộ lại
        # bắn warning_shown thêm một lần và hộp thoại cảnh báo bật lại liên tục.
        # Thời gian mới đã dưới ngưỡng nghĩa là "đang trong vùng cảnh báo", coi
        # như đã cảnh báo rồi - kể cả khi phụ huynh cho hẳn 10 phút (600s), lúc
        # đó bật ngay "còn 10 phút" là thừa.
        self.warning_triggered = seconds <= WARNING_TIME
        self.update_background_color(self.warning_triggered)
        self.update_display()
        if not self.countdown_timer.isActive():
            self.countdown_timer.start(1000)
        # stop() vừa dừng đồng hồ vừa hide(). Nhánh đồng bộ trong
        # handle_unlocked_state chỉ gọi set_time(), nên nếu không show() ở đây
        # thì sau lần khóa đầu tiên mọi lần cấp giờ tiếp theo đều đếm ngược vô
        # hình - trẻ không thấy còn bao nhiêu phút, máy khóa không báo trước.
        self.show()

    def is_counting(self):
        """Đồng hồ có đang chạy không (dùng thay cho việc chọc vào QTimer)"""
        return self.countdown_timer.isActive()

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
            if self.time_remaining <= WARNING_TIME and not self.warning_triggered:
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
        if self.time_remaining > WARNING_TIME:
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
            Qt.FramelessWindowHint |
            Qt.Tool  # không chiếm ô trên taskbar / Alt+Tab
        )
        # Không cướp focus khi bật lên - trẻ đang gõ hoặc chơi game thì cảnh báo
        # nhảy vào giữa màn hình rồi nuốt mất phím bấm.
        self.setAttribute(Qt.WA_ShowWithoutActivating)

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

        # Hẹn giờ tự đóng. Phải là QTimer có thể start() lại chứ KHÔNG dùng
        # QTimer.singleShot() đặt trong init_ui: main.py:show_warning giữ lại
        # một instance WarningDialog dùng cho cả vòng đời app, nên singleShot
        # chỉ chạy đúng một lần cho lần cảnh báo đầu tiên. Từ lần thứ hai trở đi
        # hộp thoại bật lên rồi nằm lì giữa màn hình, không đóng và không tắt
        # được (frameless, không có nút X).
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.close)

    def mousePressEvent(self, event):
        """Bấm vào là đóng - lối thoát khi hẹn giờ tự đóng có trục trặc"""
        self.close()

    def show_warning(self):
        """Hiển thị cảnh báo ở giữa màn hình"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        self.show()
        self.raise_()
        # Hẹn giờ đếm từ lúc HIỆN, không phải lúc khởi tạo
        self.auto_close_timer.start(WARNING_AUTO_CLOSE_MS)
