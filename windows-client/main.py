"""
Main Application - Ứng dụng Parental Control cho Windows
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from firebase_handler import FirebaseHandler
from lock_screen import LockScreen, ApprovedScreen
from timer_widget import TimerWidget, WarningDialog
from slack_notifier import SlackNotifier
from emergency_dialog import EmergencyDialog
from config import (
    CHECK_INTERVAL,
    EMERGENCY_UNLOCK_ENABLED,
    EMERGENCY_UNLOCK_PASSWORD
)

# Web App URL
WEB_APP_URL = "https://yutokun.netlify.app"


class ParentalControlApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Khởi tạo Firebase
        self.firebase = FirebaseHandler()
        self.firebase.initialize_device()

        # Khởi tạo Slack Notifier
        self.slack = SlackNotifier()

        # Trạng thái
        self.is_locked = True
        self.current_request_id = None
        self.is_running = True
        self.warning_sent = False

        # Khởi tạo UI components
        self.lock_screen = None
        self.timer_widget = None
        self.warning_dialog = None
        self.approved_screen = None

        # System tray
        self.setup_system_tray()

        # Bắt đầu với màn hình khóa
        self.show_lock_screen()

        # Timer kiểm tra Firebase
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_firebase_updates)
        self.check_timer.start(CHECK_INTERVAL)

        print(f"App started - Device ID: {self.firebase.get_device_id()}")

    def setup_system_tray(self):
        """Thiết lập system tray icon"""
        self.tray_icon = QSystemTrayIcon(self.app)

        # Menu
        menu = QMenu()
        device_id_action = menu.addAction(f"Device ID: {self.firebase.get_device_id()[:8]}...")
        device_id_action.setEnabled(False)
        menu.addSeparator()
        quit_action = menu.addAction("Exit (Admin only)")
        quit_action.triggered.connect(self.quit_app)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def show_lock_screen(self):
        """Hiển thị màn hình khóa và gửi yêu cầu mở khóa"""
        # Xóa lock screen cũ nếu có (đảm bảo luôn tạo mới)
        if self.lock_screen:
            try:
                self.lock_screen.close()
                self.lock_screen.deleteLater()
            except:
                pass
            self.lock_screen = None

        # Tạo lock screen mới
        self.lock_screen = LockScreen()
        self.lock_screen.set_device_id(self.firebase.get_device_id())

        # Kết nối emergency unlock signal
        if EMERGENCY_UNLOCK_ENABLED:
            self.lock_screen.emergency_unlock.connect(self.handle_emergency_unlock)

        self.lock_screen.show()
        self.lock_screen.raise_()
        self.lock_screen.activateWindow()
        self.is_locked = True

        # Ẩn timer widget nếu đang hiển thị
        if self.timer_widget:
            self.timer_widget.hide()

        # Gửi yêu cầu mở khóa
        self.current_request_id = self.firebase.send_unlock_request()
        self.firebase.update_status("pending")

        # Gửi thông báo Slack
        device_name = os.environ.get('COMPUTERNAME', 'Unknown')
        self.slack.send_unlock_request(device_name, self.firebase.get_device_id(), WEB_APP_URL)

    def unlock_computer(self):
        """Mở khóa máy tính"""
        # Xóa approved screen cũ nếu có
        if self.approved_screen:
            try:
                self.approved_screen.close()
                self.approved_screen.deleteLater()
            except:
                pass

        # Tạo approved screen mới (để timer chạy lại)
        self.approved_screen = ApprovedScreen()
        self.approved_screen.show()

        # Đóng màn hình khóa sau 2 giây
        QTimer.singleShot(2000, self.complete_unlock)

    def complete_unlock(self):
        """Hoàn tất mở khóa - KHÔNG giới hạn thời gian"""
        # Đóng lock screen
        if self.lock_screen:
            try:
                self.lock_screen.close()
                self.lock_screen.deleteLater()
            except:
                pass
            self.lock_screen = None

        # Đóng approved screen (đảm bảo không còn cửa sổ nào)
        if self.approved_screen:
            try:
                self.approved_screen.close()
                self.approved_screen.deleteLater()
            except:
                pass
            self.approved_screen = None

        self.is_locked = False
        self.firebase.update_status("unlocked")

        # Kiểm tra xem có timeRemaining từ Firebase không
        device_data = self.firebase.get_device_status()
        if device_data:
            time_remaining = device_data.get('timeRemaining')

            # Nếu timeRemaining là None hoặc null → Không giới hạn thời gian
            if time_remaining is None:
                print("✅ Unlocked with NO time limit")
                # Ẩn timer widget
                if self.timer_widget:
                    self.timer_widget.hide()
            else:
                # Có giới hạn thời gian → Hiển thị timer
                print(f"✅ Unlocked with {time_remaining}s time limit")
                if not self.timer_widget:
                    self.timer_widget = TimerWidget()
                    self.timer_widget.time_expired.connect(self.on_time_expired)
                    self.timer_widget.warning_shown.connect(self.show_warning)

                self.timer_widget.set_time(time_remaining)
                self.timer_widget.show()

    def on_time_expired(self):
        """Xử lý khi hết thời gian"""
        print("Time expired! Locking computer...")
        self.firebase.update_status("locked")

        # Gửi thông báo Slack
        device_name = os.environ.get('COMPUTERNAME', 'Unknown')
        self.slack.send_time_expired(device_name)

        self.show_lock_screen()
        self.warning_sent = False

    def show_warning(self):
        """Hiển thị cảnh báo còn 10 phút"""
        if not self.warning_dialog:
            self.warning_dialog = WarningDialog()
        self.warning_dialog.show_warning()

        # Gửi thông báo Slack (chỉ 1 lần)
        if not self.warning_sent:
            device_name = os.environ.get('COMPUTERNAME', 'Unknown')
            self.slack.send_time_warning(device_name, 10)
            self.warning_sent = True

    def handle_emergency_unlock(self):
        """Xử lý emergency unlock hotkey"""
        print("🚨 Emergency unlock requested!")

        # Tạm ẩn lock screen để dialog hiển thị được
        if self.lock_screen:
            self.lock_screen.hide()

        try:
            # Hiện dialog nhập password (custom dialog)
            password, ok = EmergencyDialog.get_emergency_password()

            if ok and password == EMERGENCY_UNLOCK_PASSWORD:
                print("✅ Emergency unlock approved!")
                self.emergency_unlock()
            elif ok:
                # Sai password - hiện lại lock screen với thông báo lỗi
                print("❌ Wrong password!")
                if self.lock_screen:
                    self.lock_screen.show()
                    self.lock_screen.show_error_message("❌ Sai mật khẩu!")
            else:
                # User hủy - hiện lại lock screen
                print("⚠️ Emergency unlock cancelled")
                if self.lock_screen:
                    self.lock_screen.show()
        except Exception as e:
            print(f"❌ Error in emergency unlock: {e}")
            # Nếu có lỗi, hiện lại lock screen
            if self.lock_screen:
                self.lock_screen.show()

    def emergency_unlock(self):
        """Mở khóa khẩn cấp (khi server/webapp lỗi)"""
        print("🆘 EMERGENCY UNLOCK activated")
        self.current_request_id = None
        self.unlock_computer()

        # Gửi thông báo Slack
        device_name = os.environ.get('COMPUTERNAME', 'Unknown')
        self.slack.send_emergency_unlock(device_name)

    def check_firebase_updates(self):
        """Kiểm tra cập nhật từ Firebase"""
        if not self.is_running:
            return

        device_data = self.firebase.get_device_status()
        if not device_data:
            print("⚠️ Cannot connect to Firebase - check internet connection")
            return

        # Kiểm tra lệnh từ xa
        remote_status = device_data.get('status', '')

        # Nếu đang khóa, kiểm tra xem có được phê duyệt không
        if self.is_locked and self.current_request_id:
            request_status = self.firebase.check_request_status(self.current_request_id)

            if request_status == 'approved':
                print("Unlock approved!")
                self.unlock_computer()
                self.current_request_id = None
            elif request_status == 'rejected':
                print("Request rejected! Sending new request...")
                # Reset và gửi request mới
                self.current_request_id = self.firebase.send_unlock_request()
            elif remote_status == 'unlocked':
                # Phụ huynh unlock từ xa
                self.unlock_computer()
                self.current_request_id = None

        # Nếu đang mở khóa, kiểm tra lệnh khóa từ xa
        elif not self.is_locked:
            if remote_status == 'locked':
                # Khóa ngay
                print("Remote lock command received!")
                self.on_time_expired()

            # Kiểm tra lockScheduled (khóa có delay)
            lock_scheduled = device_data.get('lockScheduled')
            if lock_scheduled and lock_scheduled > 0:
                import time
                current_time_ms = int(time.time() * 1000)
                if current_time_ms >= lock_scheduled:
                    # Đã đến giờ khóa
                    print(f"Scheduled lock time reached! Locking...")
                    self.on_time_expired()

        # Cập nhật thời gian từ Firebase (nếu có timer)
        if not self.is_locked:
            remote_time = device_data.get('timeRemaining')

            # Nếu có timeRemaining (không phải None)
            if remote_time is not None:
                # Nếu chưa có timer widget, tạo mới
                if not self.timer_widget:
                    self.timer_widget = TimerWidget()
                    self.timer_widget.time_expired.connect(self.on_time_expired)
                    self.timer_widget.warning_shown.connect(self.show_warning)
                    self.timer_widget.set_time(remote_time)
                    self.timer_widget.show()
                else:
                    # Đồng bộ thời gian nếu khác nhiều
                    current_time = self.timer_widget.time_remaining
                    if abs(remote_time - current_time) > 5:
                        print(f"Syncing time: {remote_time}s")
                        self.timer_widget.set_time(remote_time)
                    else:
                        # Cập nhật thời gian hiện tại lên Firebase
                        self.firebase.update_time_remaining(current_time)

    def quit_app(self):
        """Thoát ứng dụng (chỉ admin)"""
        # TODO: Thêm xác thực admin password
        self.is_running = False
        if self.lock_screen:
            self.lock_screen.close()
        if self.timer_widget:
            self.timer_widget.close()
        self.app.quit()

    def run(self):
        """Chạy ứng dụng"""
        return self.app.exec_()


def main():
    """Entry point"""
    try:
        app = ParentalControlApp()
        sys.exit(app.run())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
