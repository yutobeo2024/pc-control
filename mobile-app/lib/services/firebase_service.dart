import 'package:firebase_database/firebase_database.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import '../models/device.dart';
import '../models/unlock_request.dart';

/// Service quản lý Firebase
class FirebaseService {
  final DatabaseReference _database = FirebaseDatabase.instance.ref();
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;

  /// Lấy danh sách thiết bị
  Stream<List<Device>> getDevices() {
    return _database.child('devices').onValue.map((event) {
      final List<Device> devices = [];
      if (event.snapshot.value != null) {
        final data = event.snapshot.value as Map<dynamic, dynamic>;
        data.forEach((key, value) {
          if (value is Map) {
            devices.add(Device.fromJson(key, value));
          }
        });
      }
      return devices;
    });
  }

  /// Lấy thông tin một thiết bị cụ thể
  Stream<Device?> getDevice(String deviceId) {
    return _database.child('devices/$deviceId').onValue.map((event) {
      if (event.snapshot.value != null) {
        final data = event.snapshot.value as Map<dynamic, dynamic>;
        return Device.fromJson(deviceId, data);
      }
      return null;
    });
  }

  /// Lấy danh sách yêu cầu mở khóa đang chờ
  Stream<List<UnlockRequest>> getPendingRequests() {
    return _database.child('requests').onValue.map((event) {
      final List<UnlockRequest> requests = [];
      if (event.snapshot.value != null) {
        final data = event.snapshot.value as Map<dynamic, dynamic>;
        data.forEach((key, value) {
          if (value is Map && value['status'] == 'pending') {
            requests.add(UnlockRequest.fromJson(key, value));
          }
        });
        // Sắp xếp theo thời gian, mới nhất trước
        requests.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      }
      return requests;
    });
  }

  /// Phê duyệt yêu cầu mở khóa
  Future<void> approveUnlockRequest(String requestId, String deviceId) async {
    try {
      // Cập nhật trạng thái request
      await _database.child('requests/$requestId').update({
        'status': 'approved',
      });

      // Mở khóa thiết bị
      await _database.child('devices/$deviceId').update({
        'status': 'unlocked',
      });
    } catch (e) {
      print('Error approving request: $e');
      rethrow;
    }
  }

  /// Từ chối yêu cầu mở khóa
  Future<void> rejectUnlockRequest(String requestId) async {
    try {
      await _database.child('requests/$requestId').update({
        'status': 'rejected',
      });
    } catch (e) {
      print('Error rejecting request: $e');
      rethrow;
    }
  }

  /// Khóa máy tính ngay lập tức
  Future<void> lockDevice(String deviceId) async {
    try {
      await _database.child('devices/$deviceId').update({
        'status': 'locked',
        'timeRemaining': 0,
      });
    } catch (e) {
      print('Error locking device: $e');
      rethrow;
    }
  }

  /// Thêm thời gian
  Future<void> addTime(String deviceId, int seconds) async {
    try {
      // Lấy thời gian hiện tại
      final snapshot = await _database.child('devices/$deviceId/timeRemaining').get();
      int currentTime = 0;
      if (snapshot.value != null) {
        currentTime = snapshot.value as int;
      }

      // Cộng thêm thời gian
      await _database.child('devices/$deviceId').update({
        'timeRemaining': currentTime + seconds,
      });
    } catch (e) {
      print('Error adding time: $e');
      rethrow;
    }
  }

  /// Đặt giới hạn thời gian
  Future<void> setTimeLimit(String deviceId, int seconds) async {
    try {
      await _database.child('devices/$deviceId').update({
        'timeLimit': seconds,
      });
    } catch (e) {
      print('Error setting time limit: $e');
      rethrow;
    }
  }

  /// Setup push notifications
  Future<void> setupNotifications() async {
    try {
      // Request permission
      NotificationSettings settings = await _messaging.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );

      if (settings.authorizationStatus == AuthorizationStatus.authorized) {
        print('User granted permission');

        // Get FCM token
        String? token = await _messaging.getToken();
        print('FCM Token: $token');

        // Listen to foreground messages
        FirebaseMessaging.onMessage.listen((RemoteMessage message) {
          print('Got a message whilst in the foreground!');
          print('Message data: ${message.data}');

          if (message.notification != null) {
            print('Message also contained a notification: ${message.notification}');
          }
        });
      }
    } catch (e) {
      print('Error setting up notifications: $e');
    }
  }

  /// Đăng ký thiết bị với parent ID
  Future<void> registerDevice(String deviceId, String parentId) async {
    try {
      await _database.child('devices/$deviceId').update({
        'parentId': parentId,
      });
    } catch (e) {
      print('Error registering device: $e');
      rethrow;
    }
  }
}
