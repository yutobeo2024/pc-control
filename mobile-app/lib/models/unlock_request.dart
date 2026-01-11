/// Model cho Unlock Request
class UnlockRequest {
  final String id;
  final String deviceId;
  final String type;
  final int timestamp;
  final String status;
  final String deviceName;

  UnlockRequest({
    required this.id,
    required this.deviceId,
    required this.type,
    required this.timestamp,
    required this.status,
    required this.deviceName,
  });

  factory UnlockRequest.fromJson(String id, Map<dynamic, dynamic> json) {
    return UnlockRequest(
      id: id,
      deviceId: json['deviceId'] ?? '',
      type: json['type'] ?? 'unlock_request',
      timestamp: json['timestamp'] ?? 0,
      status: json['status'] ?? 'pending',
      deviceName: json['deviceName'] ?? 'Unknown Device',
    );
  }

  bool get isPending => status == 'pending';

  String get timeAgo {
    final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    final diff = now - timestamp;

    if (diff < 60) return 'Vừa xong';
    if (diff < 3600) return '${diff ~/ 60} phút trước';
    if (diff < 86400) return '${diff ~/ 3600} giờ trước';
    return '${diff ~/ 86400} ngày trước';
  }
}
