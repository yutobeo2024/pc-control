"""
Emergency Unlock Dialog - Dialog nhập password để mở khóa khẩn cấp
"""

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor


class EmergencyDialog(QDialog):
    """Dialog nhập password cho emergency unlock"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.password = None
        self.init_ui()

    def init_ui(self):
        """Khởi tạo giao diện"""
        self.setWindowTitle("Emergency Unlock")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setModal(True)
        self.setFixedSize(400, 200)

        # Layout chính
        layout = QVBoxLayout()

        # Icon cảnh báo
        icon_label = QLabel("🆘")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont("Segoe UI Emoji", 40)
        icon_label.setFont(icon_font)

        # Tiêu đề
        title = QLabel("Emergency Unlock")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title.setFont(title_font)

        # Thông báo
        message = QLabel("Nhập password admin để mở khóa:\n(Hotkey: Ctrl+Shift+Alt+U)")
        message.setAlignment(Qt.AlignCenter)
        message_font = QFont("Segoe UI", 10)
        message.setFont(message_font)

        # Input password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nhập password...")
        self.password_input.setFont(QFont("Segoe UI", 12))
        self.password_input.returnPressed.connect(self.accept)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setFixedHeight(35)
        cancel_btn.clicked.connect(self.reject)

        ok_btn = QPushButton("OK")
        ok_btn.setFixedHeight(35)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)

        # Thêm vào layout
        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(message)
        layout.addSpacing(10)
        layout.addWidget(self.password_input)
        layout.addSpacing(10)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Màu nền
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(40, 40, 40))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Focus vào input
        self.password_input.setFocus()

    def get_password(self):
        """Lấy password đã nhập"""
        return self.password_input.text()

    @staticmethod
    def get_emergency_password(parent=None):
        """
        Hiện dialog và trả về (password, ok)
        Tương tự QInputDialog.getText()
        """
        dialog = EmergencyDialog(parent)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            return dialog.get_password(), True
        else:
            return "", False
