"""
Main Application - Ứng dụng Parental Control cho Windows
"""

import sys
import os
import time

# Console Windows mặc định dùng cp1252 - emoji trong log sẽ ném
# UnicodeEncodeError và làm sập app khi chạy bằng python.exe (run-debug.bat).
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None:
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from firebase_handler import FirebaseHandler
from lock_screen import LockScreen, ApprovedScreen
from timer_widget import TimerWidget, WarningDialog
from slack_notifier import SlackNotifier
from emergency_dialog import EmergencyDialog
from input_blocker import InputBlocker
from single_instance import SingleInstance
from password_util import verify_password, is_default_password
import config

CHECK_INTERVAL = config.CHECK_INTERVAL
EMERGENCY_UNLOCK_ENABLED = config.EMERGENCY_UNLOCK_ENABLED

# Các tùy chọn mới - dùng getattr để không vỡ với config.py cũ
HEARTBEAT_INTERVAL = getattr(config, "HEARTBEAT_INTERVAL", 5)
REJECT_RETRY_DELAY = getattr(config, "REJECT_RETRY_DELAY", 30)
BLOCK_SYSTEM_HOTKEYS = getattr(config, "BLOCK_SYSTEM_HOTKEYS", True)
SINGLE_INSTANCE = getattr(config, "SINGLE_INSTANCE", True)
REQUIRE_PASSWORD_TO_EXIT = getattr(config, "REQUIRE_PASSWORD_TO_EXIT", True)
LOCK_ON_WAKE = getattr(config, "LOCK_ON_WAKE", True)
SLEEP_DETECT_SECONDS = getattr(config, "SLEEP_DETECT_SECONDS", 60)

# Giây chờ trước khi gửi lại yêu cầu mở khóa khi lần gửi trước thất bại vì mạng
REQUEST_RETRY_DELAY = 5

# Số lần liên tiếp đọc không thấy request thì mới coi là mất, tránh gửi lại
# yêu cầu chỉ vì một lần lỗi mạng
MISSING_REQUEST_THRESHOLD = 3

# Web App URL
WEB_APP_URL = "https://yutokun.netlify.app"


def format_duration(seconds):
    """Đổi số giây thành chuỗi người đọc được, cho log và thông báo Slack"""
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes} phút"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} tiếng" + (f" {minutes} phút" if minutes else "")


class ParentalControlApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Khởi tạo Firebase
        self.firebase = FirebaseHandler()
        self.firebase.initialize_device()

        # Khởi tạo Slack Notifier
        self.slack = SlackNotifier()

        # Chặn phím tắt hệ thống khi màn hình khóa đang hiện
        self.input_blocker = InputBlocker()
        self.app.aboutToQuit.connect(self.input_blocker.disable)

        # Trạng thái
        self.is_locked = True
        self.is_unlocking = False        # chặn unlock bị kích hoạt lặp lại
        self.current_request_id = None
        self.is_running = True
        self.warning_sent = False
        self.reject_retry_at = None      # thời điểm được phép gửi lại yêu cầu
        self.missing_request_count = 0
        self.last_heartbeat = 0.0
        # Mốc lần cuối vòng lặp polling chạy, dùng để phát hiện máy vừa ngủ dậy.
        # Phải là time.time() (đồng hồ treo tường): trên Windows time.monotonic()
        # không tính khoảng thời gian máy nằm trong sleep/hibernate, dùng nó thì
        # ngủ bao lâu cũng không phát hiện được.
        self.last_check_at = time.time()
        # Lịch khóa đang theo dõi, quy đổi sang đồng hồ của MÁY NÀY.
        # lock_schedule_raw giữ giá trị lockScheduled thô để biết khi nào phụ
        # huynh đặt lịch mới; lock_deadline là hạn tính bằng time.time() cục bộ.
        self.lock_schedule_raw = None
        self.lock_deadline = None

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

        if is_default_password():
            print("⚠️ CẢNH BÁO: mật khẩu emergency unlock vẫn là mặc định.")
            print("   Đổi ngay bằng: python set_password.py")

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
        self.is_unlocking = False
        self.reject_retry_at = None
        self.missing_request_count = 0

        # Chặn Alt+Tab / Win / Alt+F4 khi đang khóa
        if BLOCK_SYSTEM_HOTKEYS:
            self.input_blocker.enable()

        # Dừng hẳn timer widget (hide() không dừng QTimer bên trong)
        if self.timer_widget:
            self.timer_widget.stop()

        # Gửi yêu cầu mở khóa
        self.current_request_id = self.firebase.send_unlock_request()
        if self.current_request_id is None:
            # Mất mạng đúng lúc khóa - rất hay gặp ngay sau khi máy ngủ dậy.
            # Không hẹn gửi lại thì handle_locked_state đứng im vĩnh viễn vì
            # không có request nào để theo dõi, phụ huynh không thấy yêu cầu nào.
            print(f"Khong gui duoc yeu cau - thu lai sau {REQUEST_RETRY_DELAY}s")
            self.reject_retry_at = time.monotonic() + REQUEST_RETRY_DELAY
        self.firebase.update_status("pending")

        # Gửi thông báo Slack
        device_name = os.environ.get('COMPUTERNAME', 'Unknown')
        self.slack.send_unlock_request(device_name, self.firebase.get_device_id(), WEB_APP_URL)

    def unlock_computer(self):
        """Mở khóa máy tính"""
        if self.is_unlocking:
            return
        self.is_unlocking = True

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
        # Bỏ chặn phím tắt hệ thống
        self.input_blocker.disable()

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
        self.is_unlocking = False
        self.firebase.update_status("unlocked")

        # Kiểm tra xem có timeRemaining từ Firebase không
        device_data = self.firebase.get_device_status()
        if device_data:
            time_remaining = device_data.get('timeRemaining')

            # Nếu timeRemaining là None hoặc null → Không giới hạn thời gian
            if time_remaining is None:
                print("✅ Unlocked with NO time limit")
                # Dừng hẳn timer widget nếu còn sót từ lần khóa trước
                if self.timer_widget:
                    self.timer_widget.stop()
            else:
                # Có giới hạn thời gian → Hiển thị timer
                print(f"✅ Unlocked with {time_remaining}s time limit")
                if not self.timer_widget:
                    self.timer_widget = TimerWidget()
                    self.timer_widget.time_expired.connect(self.on_time_expired)
                    self.timer_widget.warning_shown.connect(self.show_warning)

                self.timer_widget.set_time(time_remaining)
                self.timer_widget.show()

    def on_time_expired(self, reason="Đã hết giờ"):
        """
        Khóa máy. Gọi từ nhiều nguồn: hết giờ đếm ngược, tới lịch lockScheduled,
        lệnh khóa từ web, và phát hiện máy vừa ngủ dậy. `reason` chỉ để log và
        báo Slack cho đúng, không đổi hành vi.
        """
        # Đã khóa rồi thì bỏ qua. Lịch khóa và timer đếm ngược là hai nguồn độc
        # lập cùng trỏ tới đây và thường nổ cách nhau 1-2 giây, không chặn thì
        # sinh ra hai màn hình khóa và hai unlock request.
        if self.is_locked:
            return

        print(f"{reason} - dang khoa may...")

        # Dừng timer trước khi khóa, nếu không nó vẫn đếm ngầm sau khi bị ẩn
        # và bắn time_expired thêm một lần nữa.
        if self.timer_widget:
            self.timer_widget.stop()

        self.firebase.update_status("locked")

        # Lịch khóa đã chạy xong -> xóa, nếu không lần approve kế tiếp sẽ bị
        # khóa lại ngay trong vòng 2 giây
        self.firebase.clear_lock_schedule()

        # Gửi thông báo Slack
        device_name = os.environ.get('COMPUTERNAME', 'Unknown')
        self.slack.send_time_expired(device_name, reason)

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

        # Tạm bỏ chặn phím tắt để gõ được mật khẩu bình thường
        was_blocking = self.input_blocker.is_enabled
        self.input_blocker.disable()

        try:
            # Hiện dialog nhập password (custom dialog)
            password, ok = EmergencyDialog.get_emergency_password()

            if ok and verify_password(password):
                print("✅ Emergency unlock approved!")
                self.emergency_unlock()
            elif ok:
                # Sai password - hiện lại lock screen với thông báo lỗi
                print("❌ Wrong password!")
                if was_blocking:
                    self.input_blocker.enable()
                if self.lock_screen:
                    self.lock_screen.show()
                    self.lock_screen.show_error_message("❌ Sai mật khẩu!")
            else:
                # User hủy - hiện lại lock screen
                print("⚠️ Emergency unlock cancelled")
                if was_blocking:
                    self.input_blocker.enable()
                if self.lock_screen:
                    self.lock_screen.show()
        except Exception as e:
            print(f"❌ Error in emergency unlock: {e}")
            # Nếu có lỗi, hiện lại lock screen
            if was_blocking:
                self.input_blocker.enable()
            if self.lock_screen:
                self.lock_screen.show()

    def emergency_unlock(self):
        """Mở khóa khẩn cấp (khi server/webapp lỗi)"""
        print("🆘 EMERGENCY UNLOCK activated")
        self.firebase.delete_request(self.current_request_id)
        self.current_request_id = None
        self.unlock_computer()

        # Gửi thông báo Slack
        device_name = os.environ.get('COMPUTERNAME', 'Unknown')
        self.slack.send_emergency_unlock(device_name)

    def send_heartbeat_if_due(self):
        """
        Cập nhật lastActive định kỳ để web app biết máy còn online.

        Phải chạy độc lập với timer: khi mở khóa không giới hạn thời gian thì
        không có timer nào ghi lên Firebase, lastActive sẽ đứng yên và web luôn
        hiển thị Offline.
        """
        now = time.monotonic()
        if now - self.last_heartbeat < HEARTBEAT_INTERVAL:
            return
        self.last_heartbeat = now
        self.firebase.send_heartbeat()

    def handle_locked_state(self, device_data, remote_status):
        """Đang khóa - chờ phụ huynh duyệt"""
        # Phụ huynh mở khóa thẳng từ trang thiết bị
        if remote_status == 'unlocked':
            print("Remote unlock received!")
            self.firebase.delete_request(self.current_request_id)
            self.current_request_id = None
            self.unlock_computer()
            return

        # Đang trong thời gian chờ sau khi bị từ chối
        if self.current_request_id is None:
            if self.reject_retry_at and time.monotonic() >= self.reject_retry_at:
                print("Retrying unlock request...")
                self.reject_retry_at = None
                self.current_request_id = self.firebase.send_unlock_request()
                if self.current_request_id is None:
                    # Vẫn chưa gửi được (mạng chưa lên) - hẹn tiếp, đừng để rơi
                    # vào trạng thái khóa mà không có yêu cầu nào chờ duyệt
                    self.reject_retry_at = time.monotonic() + REQUEST_RETRY_DELAY
                elif self.lock_screen:
                    self.lock_screen.reset_message()
            return

        request_status = self.firebase.check_request_status(self.current_request_id)

        if request_status == 'approved':
            print("Unlock approved!")
            self.missing_request_count = 0
            # Xóa request đã xử lý để nhánh requests/ không phình vô hạn
            self.firebase.delete_request(self.current_request_id)
            self.current_request_id = None
            self.unlock_computer()

        elif request_status == 'rejected':
            print(f"Request rejected! Retrying in {REJECT_RETRY_DELAY}s...")
            self.missing_request_count = 0
            self.firebase.delete_request(self.current_request_id)
            self.current_request_id = None
            self.reject_retry_at = time.monotonic() + REJECT_RETRY_DELAY
            if self.lock_screen:
                self.lock_screen.show_rejected_message(REJECT_RETRY_DELAY)

        elif request_status is None:
            # Request biến mất (bị dọn, hoặc lỗi mạng). Chỉ gửi lại khi lỗi lặp
            # nhiều lần liên tiếp, tránh tạo request thừa vì một lần timeout.
            self.missing_request_count += 1
            if self.missing_request_count >= MISSING_REQUEST_THRESHOLD:
                print("Request missing - sending a new one")
                self.missing_request_count = 0
                self.current_request_id = self.firebase.send_unlock_request()
                if self.current_request_id is None:
                    self.reject_retry_at = time.monotonic() + REQUEST_RETRY_DELAY

        else:
            self.missing_request_count = 0

    def handle_unlocked_state(self, device_data, remote_status):
        """Đang mở khóa - chờ lệnh khóa"""
        if remote_status == 'locked':
            # Khóa ngay
            print("Remote lock command received!")
            self.on_time_expired(reason="Phụ huynh khóa từ xa")
            return

        # Cập nhật thời gian từ Firebase (nếu có timer)
        remote_time = device_data.get('timeRemaining')

        # ---- Lịch khóa có delay ("Khóa sau 30 phút / 1 giờ / ...") ----
        # Web ghi cùng lúc hai giá trị: lockScheduled = Date.now() + N phút
        # (mốc tuyệt đối, tính bằng đồng hồ ĐIỆN THOẠI phụ huynh) và
        # timeRemaining = N*60 (khoảng thời gian, không phụ thuộc đồng hồ nào).
        #
        # So thẳng lockScheduled với time.time() của máy con là sai: hai đồng hồ
        # lệch nhau bao nhiêu thì lịch xê dịch bấy nhiêu. Máy con chạy nhanh hơn
        # điện thoại 30 phút thì "cho chơi 30 phút" biến thành khóa lại sau 2
        # giây. Nên chỉ dùng lockScheduled để BIẾT CÓ LỊCH MỚI, còn hạn thì tính
        # lại bằng khoảng thời gian trên chính đồng hồ máy này.
        lock_scheduled = device_data.get('lockScheduled')
        if lock_scheduled and lock_scheduled > 0:
            if lock_scheduled != self.lock_schedule_raw:
                if remote_time is not None:
                    remaining = remote_time
                else:
                    # Không có timeRemaining thì đành tin mốc tuyệt đối
                    remaining = (lock_scheduled - time.time() * 1000) / 1000.0
                self.lock_schedule_raw = lock_scheduled
                self.lock_deadline = time.time() + max(0, remaining)
                print(f"Lich khoa moi: sau {format_duration(max(0, remaining))}")

            if time.time() >= self.lock_deadline:
                self.on_time_expired(reason="Đã đến giờ khóa theo lịch")
                return
        else:
            # Lịch bị hủy (phụ huynh approve) hoặc đã tiêu thụ xong
            self.lock_schedule_raw = None
            self.lock_deadline = None

        # timeRemaining = None nghĩa là mở khóa không giới hạn thời gian
        if remote_time is None:
            return

        if not self.timer_widget:
            self.timer_widget = TimerWidget()
            self.timer_widget.time_expired.connect(self.on_time_expired)
            self.timer_widget.warning_shown.connect(self.show_warning)
            self.timer_widget.set_time(remote_time)
            self.timer_widget.show()
            return

        # Đồng bộ thời gian nếu lệch nhiều
        current_time = self.timer_widget.time_remaining
        if abs(remote_time - current_time) > 5:
            print(f"Syncing time: {remote_time}s")
            self.timer_widget.set_time(remote_time)
        else:
            # Cập nhật thời gian hiện tại lên Firebase
            self.firebase.update_time_remaining(current_time)

    def check_firebase_updates(self):
        """Kiểm tra cập nhật từ Firebase"""
        if not self.is_running:
            return

        # ---- Phát hiện máy vừa ngủ dậy ----
        # Hàm này chạy mỗi CHECK_INTERVAL (2 giây). QTimer không tick khi máy
        # ngủ, nên một bước nhảy hàng chục giây chỉ có thể là sleep/hibernate.
        #
        # Vì sao cần: "khóa khi mở máy" không phải logic riêng, nó chỉ là hệ quả
        # của việc tiến trình khởi động lại (__init__ đặt is_locked = True).
        # Sleep không kết thúc tiến trình, Task Scheduler cũng chỉ có trigger
        # logon - nên ngủ rồi thức dậy là đi vòng qua toàn bộ hệ thống.
        #
        # Kiểm tra này phải nằm TRƯỚC mọi lệnh gọi Firebase: lúc vừa thức dậy
        # card mạng thường chưa kết nối lại, đọc Firebase sẽ lỗi và return sớm,
        # máy sẽ không bao giờ bị khóa.
        now = time.time()
        gap = now - self.last_check_at
        self.last_check_at = now

        if LOCK_ON_WAKE and gap > SLEEP_DETECT_SECONDS and not self.is_locked:
            reason = f"Máy vừa ngủ dậy sau {format_duration(gap)}"
            print(f"{reason} - khóa lại")
            self.on_time_expired(reason=reason)
            return

        # Heartbeat chạy trước và độc lập với mọi nhánh logic bên dưới
        self.send_heartbeat_if_due()

        device_data = self.firebase.get_device_status()
        if not device_data:
            print("⚠️ Cannot connect to Firebase - check internet connection")
            return

        remote_status = device_data.get('status', '')

        # Đang trong 2 giây chuyển cảnh mở khóa - bỏ qua để không kích hoạt lặp
        if self.is_unlocking:
            return

        if self.is_locked:
            self.handle_locked_state(device_data, remote_status)
        else:
            self.handle_unlocked_state(device_data, remote_status)

    def quit_app(self):
        """Thoát ứng dụng (yêu cầu mật khẩu admin)"""
        if REQUIRE_PASSWORD_TO_EXIT:
            was_blocking = self.input_blocker.is_enabled
            self.input_blocker.disable()

            password, ok = EmergencyDialog.get_emergency_password()
            if not (ok and verify_password(password)):
                print("❌ Exit denied - wrong password")
                if was_blocking:
                    self.input_blocker.enable()
                if self.lock_screen and self.is_locked:
                    self.lock_screen.show()
                    self.lock_screen.show_error_message("❌ Sai mật khẩu!")
                return

        print("👋 Exiting...")
        self.is_running = False
        self.input_blocker.disable()
        if self.lock_screen:
            self.lock_screen.allow_close()
            self.lock_screen.close()
        if self.timer_widget:
            self.timer_widget.close()
        self.app.quit()

    def run(self):
        """Chạy ứng dụng"""
        return self.app.exec_()


def main():
    """Entry point"""
    guard = None
    if SINGLE_INSTANCE:
        guard = SingleInstance()
        if guard.already_running:
            print("⚠️ Parental Control đang chạy rồi - thoát instance này.")
            return

    try:
        app = ParentalControlApp()
        sys.exit(app.run())
    except SystemExit:
        raise
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if guard:
            guard.release()


if __name__ == "__main__":
    main()
