"""
Firebase Handler - Quản lý kết nối và đồng bộ dữ liệu với Firebase
"""

import pyrebase
import uuid
import os
from datetime import datetime
from config import FIREBASE_CONFIG, DEVICE_ID_FILE
from paths import app_path

# device_id.txt phải nằm cạnh ứng dụng và tồn tại lâu dài. Dùng đường dẫn tuyệt
# đối để không phụ thuộc thư mục làm việc, và để chạy đúng khi đóng gói .exe.
DEVICE_ID_PATH = app_path(DEVICE_ID_FILE)


class FirebaseHandler:
    def __init__(self):
        self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        self.db = self.firebase.database()
        self.device_id = self._get_or_create_device_id()
        self.device_path = f"devices/{self.device_id}"

    def _get_or_create_device_id(self):
        """Lấy hoặc tạo Device ID duy nhất (riêng cho từng máy)"""
        if os.path.exists(DEVICE_ID_PATH):
            with open(DEVICE_ID_PATH, 'r') as f:
                existing = f.read().strip()
                if existing:
                    return existing
        device_id = str(uuid.uuid4())
        with open(DEVICE_ID_PATH, 'w') as f:
            f.write(device_id)
        return device_id

    def initialize_device(self):
        """
        Đăng ký thiết bị lên Firebase.

        Lần đầu thì tạo node đầy đủ. Các lần khởi động sau chỉ `update()` những
        field thuộc về client.

        KHÔNG dùng `set()` ở đây: `set()` là thay thế toàn bộ node, nên mỗi lần
        khởi động sẽ ghi đè `createdAt` (biến nó thành "lần chạy gần nhất"),
        xóa `lockScheduled` và xóa sạch mọi field do web app thêm vào sau này.
        """
        now = self._get_timestamp()
        device_name = os.environ.get('COMPUTERNAME', 'Unknown')

        # Phải phân biệt "node chưa tồn tại" với "đọc lỗi". get_device_status()
        # trả None cho cả hai, dùng nó ở đây thì một lần mất mạng lúc khởi động
        # sẽ rơi vào nhánh set() và xóa sạch node.
        try:
            existing = self.db.child(self.device_path).get().val()
        except Exception as e:
            print(f"⚠️ Cannot read device node ({e}) - skip initialization")
            return

        if existing:
            self.db.child(self.device_path).update({
                "deviceName": device_name,
                "lastActive": now,
            })
            print(f"Device registered (existing): {self.device_id}")
            return

        self.db.child(self.device_path).set({
            "status": "locked",
            "timeLimit": 7200,  # 2 giờ mặc định
            "timeRemaining": 0,
            "lastActive": now,
            "deviceName": device_name,
            "parentId": "",
            "createdAt": now
        })
        print(f"Device initialized with ID: {self.device_id}")

    def send_unlock_request(self):
        """Gửi yêu cầu mở khóa máy tính"""
        request_id = str(uuid.uuid4())
        request_data = {
            "deviceId": self.device_id,
            "type": "unlock_request",
            "timestamp": self._get_timestamp(),
            "status": "pending",
            "deviceName": os.environ.get('COMPUTERNAME', 'Unknown')
        }
        try:
            self.db.child(f"requests/{request_id}").set(request_data)
        except Exception as e:
            # Hay xảy ra ngay sau khi máy ngủ dậy: card mạng chưa kết nối lại.
            # Trả None để main.py biết mà hẹn gửi lại.
            print(f"Error sending unlock request: {e}")
            return None
        print(f"Unlock request sent: {request_id}")
        return request_id

    def get_device_status(self):
        """Lấy trạng thái hiện tại của thiết bị"""
        try:
            data = self.db.child(self.device_path).get().val()
            if data:
                return data
            return None
        except Exception as e:
            print(f"Error getting device status: {e}")
            return None

    def update_status(self, status):
        """
        Cập nhật trạng thái thiết bị.

        Ném exception ở đây là chết người: hàm này nằm giữa đường khóa máy
        (on_time_expired -> update_status -> show_lock_screen). Exception không
        bắt trong một slot của Qt sẽ làm PyQt gọi qFatal và giết cả app, để lại
        máy KHÔNG khóa. Nuốt lỗi và vẫn khóa là lựa chọn an toàn hơn - trạng
        thái trên Firebase sẽ được heartbeat đồng bộ lại khi mạng có lại.
        """
        try:
            self.db.child(self.device_path).update({
                "status": status,
                "lastActive": self._get_timestamp()
            })
            return True
        except Exception as e:
            print(f"Error updating status: {e}")
            return False

    def update_time_remaining(self, seconds):
        """Cập nhật thời gian còn lại"""
        try:
            self.db.child(self.device_path).update({
                "timeRemaining": seconds,
                "lastActive": self._get_timestamp()
            })
            return True
        except Exception as e:
            print(f"Error updating time remaining: {e}")
            return False

    def clear_lock_schedule(self):
        """
        Xóa `lockScheduled` sau khi lịch khóa đã kích hoạt.

        Một lịch đã chạy phải được "tiêu thụ". Nếu để nguyên, timestamp quá khứ
        vẫn nằm trong DB và lần mở khóa kế tiếp sẽ bị khóa lại ngay lập tức
        (check ở main.py:handle_unlocked_state thấy current_time >= lockScheduled).
        """
        try:
            # Firebase xóa hẳn key khi nhận giá trị null
            self.db.child(self.device_path).update({"lockScheduled": None})
            return True
        except Exception as e:
            print(f"Error clearing lock schedule: {e}")
            return False

    def send_heartbeat(self):
        """
        Cập nhật lastActive để web app biết máy còn online.

        Cần gọi định kỳ kể cả khi mở khóa không giới hạn thời gian - lúc đó
        không có timer nên update_time_remaining() không bao giờ chạy, khiến
        lastActive đứng yên và web luôn báo Offline.
        """
        try:
            self.db.child(self.device_path).update({
                "lastActive": self._get_timestamp()
            })
            return True
        except Exception as e:
            print(f"Error sending heartbeat: {e}")
            return False

    def delete_request(self, request_id):
        """
        Xóa một request sau khi đã xử lý xong.

        Không dọn thì nhánh `requests/` phình vô hạn: mỗi lần bị từ chối client
        lại tạo request mới, còn web app load toàn bộ nhánh này mỗi lần có thay
        đổi nên sẽ chậm dần theo thời gian.
        """
        if not request_id:
            return False
        try:
            self.db.child(f"requests/{request_id}").remove()
            print(f"🗑️ Deleted request: {request_id}")
            return True
        except Exception as e:
            print(f"Error deleting request: {e}")
            return False

    def check_unlock_approved(self, request_id):
        """Kiểm tra yêu cầu mở khóa đã được phê duyệt chưa"""
        try:
            request = self.db.child(f"requests/{request_id}").get().val()
            if request and request.get('status') == 'approved':
                return True
            return False
        except Exception as e:
            print(f"Error checking unlock approval: {e}")
            return False

    def check_request_status(self, request_id):
        """Kiểm tra trạng thái của request (pending/approved/rejected)"""
        try:
            request = self.db.child(f"requests/{request_id}").get().val()
            if request:
                return request.get('status', 'pending')
            return None
        except Exception as e:
            print(f"Error checking request status: {e}")
            return None

    def listen_for_remote_commands(self, callback):
        """Lắng nghe lệnh từ xa từ app phụ huynh"""
        def stream_handler(message):
            if message["event"] == "put" and message["path"] == "/":
                data = message["data"]
                if data:
                    callback(data)

        try:
            self.db.child(self.device_path).stream(stream_handler)
        except Exception as e:
            print(f"Error listening for commands: {e}")

    def _get_timestamp(self):
        """Lấy timestamp hiện tại"""
        return int(datetime.now().timestamp())

    def get_device_id(self):
        """Trả về Device ID"""
        return self.device_id
