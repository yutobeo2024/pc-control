import 'package:flutter/material.dart';
import '../services/firebase_service.dart';
import '../models/device.dart';

/// Màn hình điều khiển thiết bị
class ControlScreen extends StatefulWidget {
  final Device device;

  const ControlScreen({Key? key, required this.device}) : super(key: key);

  @override
  State<ControlScreen> createState() => _ControlScreenState();
}

class _ControlScreenState extends State<ControlScreen> {
  final FirebaseService _firebaseService = FirebaseService();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E1E1E),
      appBar: AppBar(
        title: Text(widget.device.deviceName),
        backgroundColor: const Color(0xFF2D2D2D),
        elevation: 0,
      ),
      body: StreamBuilder<Device?>(
        stream: _firebaseService.getDevice(widget.device.id),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(color: Colors.orange),
            );
          }

          if (!snapshot.hasData) {
            return const Center(
              child: Text(
                'Không tìm thấy thiết bị',
                style: TextStyle(color: Colors.white70, fontSize: 18),
              ),
            );
          }

          final device = snapshot.data!;
          final isUnlocked = device.status == 'unlocked';

          return SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                // Trạng thái thiết bị
                _buildStatusCard(device, isUnlocked),

                const SizedBox(height: 24),

                // Đồng hồ đếm ngược (nếu đang mở khóa)
                if (isUnlocked) _buildTimerCard(device),

                const SizedBox(height: 24),

                // Nút điều khiển
                _buildControlButtons(device, isUnlocked),

                const SizedBox(height: 24),

                // Cài đặt giới hạn thời gian
                _buildTimeLimitSettings(device),
              ],
            ),
          );
        },
      ),
    );
  }

  /// Card trạng thái thiết bị
  Widget _buildStatusCard(Device device, bool isUnlocked) {
    final color = isUnlocked ? Colors.green : Colors.red;
    final icon = isUnlocked ? Icons.check_circle : Icons.lock;
    final status = device.statusText;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: const Color(0xFF2D2D2D),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          Icon(icon, size: 80, color: color),
          const SizedBox(height: 16),
          Text(
            status,
            style: TextStyle(
              color: color,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          if (device.isActive) ...[
            const SizedBox(height: 8),
            const Text(
              '● Đang hoạt động',
              style: TextStyle(color: Colors.green, fontSize: 14),
            ),
          ] else ...[
            const SizedBox(height: 8),
            const Text(
              '○ Offline',
              style: TextStyle(color: Colors.white38, fontSize: 14),
            ),
          ],
        ],
      ),
    );
  }

  /// Card đồng hồ đếm ngược
  Widget _buildTimerCard(Device device) {
    final hours = device.timeRemaining ~/ 3600;
    final minutes = (device.timeRemaining % 3600) ~/ 60;
    final seconds = device.timeRemaining % 60;

    final isWarning = device.timeRemaining <= 600; // Còn <= 10 phút

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: isWarning
            ? const Color(0xFF4D2D1F)
            : const Color(0xFF2D2D2D),
        borderRadius: BorderRadius.circular(20),
        border: isWarning
            ? Border.all(color: Colors.orange, width: 2)
            : null,
      ),
      child: Column(
        children: [
          Text(
            isWarning ? '⚠️ Sắp hết giờ' : '⏱️ Thời gian còn lại',
            style: TextStyle(
              color: isWarning ? Colors.orange : Colors.white70,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            '${hours.toString().padLeft(2, '0')}:${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}',
            style: TextStyle(
              color: isWarning ? Colors.orange : Colors.white,
              fontSize: 56,
              fontWeight: FontWeight.bold,
              fontFamily: 'Courier',
            ),
          ),
        ],
      ),
    );
  }

  /// Nút điều khiển
  Widget _buildControlButtons(Device device, bool isUnlocked) {
    return Column(
      children: [
        // Nút Khóa ngay / Mở khóa
        if (isUnlocked)
          _buildBigButton(
            label: 'Khóa máy ngay',
            icon: Icons.lock,
            color: Colors.red.shade700,
            onPressed: () => _lockDevice(device.id),
          )
        else
          _buildBigButton(
            label: 'Mở khóa',
            icon: Icons.lock_open,
            color: Colors.green.shade600,
            onPressed: () => _unlockDevice(device.id),
          ),

        const SizedBox(height: 16),

        // Nút Thêm thời gian (chỉ hiện khi đang mở khóa)
        if (isUnlocked) ...[
          Row(
            children: [
              Expanded(
                child: _buildSmallButton(
                  label: '+15 phút',
                  onPressed: () => _addTime(device.id, 900),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildSmallButton(
                  label: '+30 phút',
                  onPressed: () => _addTime(device.id, 1800),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildSmallButton(
                  label: '+1 giờ',
                  onPressed: () => _addTime(device.id, 3600),
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  /// Cài đặt giới hạn thời gian
  Widget _buildTimeLimitSettings(Device device) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF2D2D2D),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Giới hạn thời gian mặc định',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildTimeLimitButton(
                  '1 giờ',
                  3600,
                  device.id,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildTimeLimitButton(
                  '2 giờ',
                  7200,
                  device.id,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildTimeLimitButton(
                  '3 giờ',
                  10800,
                  device.id,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Nút lớn
  Widget _buildBigButton({
    required String label,
    required IconData icon,
    required Color color,
    required VoidCallback onPressed,
  }) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon, size: 32),
        label: Text(
          label,
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 20),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }

  /// Nút nhỏ
  Widget _buildSmallButton({
    required String label,
    required VoidCallback onPressed,
  }) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF3A3A3A),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      child: Text(
        label,
        style: const TextStyle(fontSize: 16),
      ),
    );
  }

  /// Nút cài đặt giới hạn thời gian
  Widget _buildTimeLimitButton(String label, int seconds, String deviceId) {
    return OutlinedButton(
      onPressed: () => _setTimeLimit(deviceId, seconds),
      style: OutlinedButton.styleFrom(
        foregroundColor: Colors.white,
        side: const BorderSide(color: Colors.white38),
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      child: Text(label),
    );
  }

  /// Khóa thiết bị
  Future<void> _lockDevice(String deviceId) async {
    try {
      await _firebaseService.lockDevice(deviceId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('🔒 Đã khóa máy tính'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      _showError(e);
    }
  }

  /// Mở khóa thiết bị
  Future<void> _unlockDevice(String deviceId) async {
    try {
      await _firebaseService.approveUnlockRequest('manual', deviceId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Đã mở khóa máy tính'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      _showError(e);
    }
  }

  /// Thêm thời gian
  Future<void> _addTime(String deviceId, int seconds) async {
    try {
      await _firebaseService.addTime(deviceId, seconds);
      final minutes = seconds ~/ 60;
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('⏱️ Đã thêm $minutes phút'),
            backgroundColor: Colors.blue,
          ),
        );
      }
    } catch (e) {
      _showError(e);
    }
  }

  /// Đặt giới hạn thời gian
  Future<void> _setTimeLimit(String deviceId, int seconds) async {
    try {
      await _firebaseService.setTimeLimit(deviceId, seconds);
      final hours = seconds ~/ 3600;
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Đã đặt giới hạn: $hours giờ/ngày'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      _showError(e);
    }
  }

  /// Hiển thị lỗi
  void _showError(Object e) {
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
