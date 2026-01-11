"""
Firebase Handler - Quản lý kết nối và đồng bộ dữ liệu với Firebase
"""

import pyrebase
import uuid
import os
from datetime import datetime
from config import FIREBASE_CONFIG, DEVICE_ID_FILE


class FirebaseHandler:
    def __init__(self):
        self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        self.db = self.firebase.database()
        self.device_id = self._get_or_create_device_id()
        self.device_path = f"devices/{self.device_id}"

    def _get_or_create_device_id(self):
        """Lấy hoặc tạo Device ID duy nhất"""
        if os.path.exists(DEVICE_ID_FILE):
            with open(DEVICE_ID_FILE, 'r') as f:
                return f.read().strip()
        else:
            device_id = str(uuid.uuid4())
            with open(DEVICE_ID_FILE, 'w') as f:
                f.write(device_id)
            return device_id

    def initialize_device(self):
        """Khởi tạo thông tin thiết bị trên Firebase"""
        device_data = {
            "status": "locked",
            "timeLimit": 7200,  # 2 giờ mặc định
            "timeRemaining": 0,
            "lastActive": self._get_timestamp(),
            "deviceName": os.environ.get('COMPUTERNAME', 'Unknown'),
            "parentId": "",
            "createdAt": self._get_timestamp()
        }
        self.db.child(self.device_path).set(device_data)
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
        self.db.child(f"requests/{request_id}").set(request_data)
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
        """Cập nhật trạng thái thiết bị"""
        self.db.child(self.device_path).update({
            "status": status,
            "lastActive": self._get_timestamp()
        })

    def update_time_remaining(self, seconds):
        """Cập nhật thời gian còn lại"""
        self.db.child(self.device_path).update({
            "timeRemaining": seconds,
            "lastActive": self._get_timestamp()
        })

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
