import 'package:flutter/material.dart';
import '../services/firebase_service.dart';
import '../models/device.dart';
import '../models/unlock_request.dart';
import 'control_screen.dart';

/// Màn hình chính - Hiển thị yêu cầu mở khóa và danh sách thiết bị
class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final FirebaseService _firebaseService = FirebaseService();

  @override
  void initState() {
    super.initState();
    _firebaseService.setupNotifications();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E1E1E),
      appBar: AppBar(
        title: const Text(
          'Parental Control',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF2D2D2D),
        elevation: 0,
      ),
      body: Column(
        children: [
          // Phần yêu cầu mở khóa
          _buildPendingRequests(),

          const SizedBox(height: 20),

          // Danh sách thiết bị
          Expanded(
            child: _buildDeviceList(),
          ),
        ],
      ),
    );
  }

  /// Phần hiển thị yêu cầu mở khóa
  Widget _buildPendingRequests() {
    return StreamBuilder<List<UnlockRequest>>(
      stream: _firebaseService.getPendingRequests(),
      builder: (context, snapshot) {
        if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return const SizedBox.shrink();
        }

        final request = snapshot.data!.first;

        return Container(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: const Color(0xFF3A3A3A),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.orange.withOpacity(0.3),
                blurRadius: 10,
                spreadRadius: 2,
              ),
            ],
          ),
          child: Column(
            children: [
              const Text(
                '🔔 Yêu cầu mở máy',
                style: TextStyle(
                  color: Colors.orange,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                request.deviceName,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                request.timeAgo,
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // Nút Từ chối
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _rejectRequest(request.id),
                      icon: const Icon(Icons.close, size: 28),
                      label: const Text(
                        'Từ chối',
                        style: TextStyle(fontSize: 18),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red.shade700,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  // Nút Cho phép
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _approveRequest(request),
                      icon: const Icon(Icons.check, size: 28),
                      label: const Text(
                        'Cho phép',
                        style: TextStyle(fontSize: 18),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green.shade600,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  /// Danh sách thiết bị
  Widget _buildDeviceList() {
    return StreamBuilder<List<Device>>(
      stream: _firebaseService.getDevices(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(
            child: CircularProgressIndicator(color: Colors.orange),
          );
        }

        if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  '📱',
                  style: TextStyle(fontSize: 60),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Chưa có thiết bị nào',
                  style: TextStyle(color: Colors.white70, fontSize: 18),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Cài đặt app trên máy tính con',
                  style: TextStyle(color: Colors.white54, fontSize: 14),
                ),
              ],
            ),
          );
        }

        final devices = snapshot.data!;

        return ListView.builder(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          itemCount: devices.length,
          itemBuilder: (context, index) {
            final device = devices[index];
            return _buildDeviceCard(device);
          },
        );
      },
    );
  }

  /// Card hiển thị thiết bị
  Widget _buildDeviceCard(Device device) {
    final isUnlocked = device.status == 'unlocked';
    final color = isUnlocked ? Colors.green : Colors.red;

    return Card(
      color: const Color(0xFF2D2D2D),
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.2),
          radius: 28,
          child: Icon(
            isUnlocked ? Icons.computer : Icons.lock,
            color: color,
            size: 28,
          ),
        ),
        title: Text(
          device.deviceName,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              device.statusText,
              style: TextStyle(
                color: color,
                fontSize: 14,
              ),
            ),
            if (isUnlocked) ...[
              const SizedBox(height: 4),
              Text(
                _formatTime(device.timeRemaining),
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 14,
                ),
              ),
            ],
          ],
        ),
        trailing: const Icon(
          Icons.arrow_forward_ios,
          color: Colors.white38,
          size: 20,
        ),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ControlScreen(device: device),
            ),
          );
        },
      ),
    );
  }

  /// Format thời gian
  String _formatTime(int seconds) {
    final hours = seconds ~/ 3600;
    final minutes = (seconds % 3600) ~/ 60;
    final secs = seconds % 60;
    return 'Còn ${hours}h ${minutes}m ${secs}s';
  }

  /// Phê duyệt yêu cầu
  Future<void> _approveRequest(UnlockRequest request) async {
    try {
      await _firebaseService.approveUnlockRequest(request.id, request.deviceId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Đã cho phép mở máy'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Lỗi: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Từ chối yêu cầu
  Future<void> _rejectRequest(String requestId) async {
    try {
      await _firebaseService.rejectUnlockRequest(requestId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('❌ Đã từ chối yêu cầu'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Lỗi: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
