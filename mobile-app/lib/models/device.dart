/// Model cho Device (máy tính con)
class Device {
  final String id;
  final String status;
  final int timeLimit;
  final int timeRemaining;
  final int lastActive;
  final String deviceName;
  final String parentId;

  Device({
    required this.id,
    required this.status,
    required this.timeLimit,
    required this.timeRemaining,
    required this.lastActive,
    required this.deviceName,
    required this.parentId,
  });

  factory Device.fromJson(String id, Map<dynamic, dynamic> json) {
    return Device(
      id: id,
      status: json['status'] ?? 'locked',
      timeLimit: json['timeLimit'] ?? 7200,
      timeRemaining: json['timeRemaining'] ?? 0,
      lastActive: json['lastActive'] ?? 0,
      deviceName: json['deviceName'] ?? 'Unknown Device',
      parentId: json['parentId'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'status': status,
      'timeLimit': timeLimit,
      'timeRemaining': timeRemaining,
      'lastActive': lastActive,
      'deviceName': deviceName,
      'parentId': parentId,
    };
  }

  bool get isActive {
    final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    return now - lastActive < 10; // Active nếu cập nhật trong 10 giây
  }

  String get statusText {
    switch (status) {
      case 'locked':
        return 'Đã khóa';
      case 'unlocked':
        return 'Đang hoạt động';
      case 'pending':
        return 'Chờ phê duyệt';
      default:
        return 'Không xác định';
    }
  }
}
