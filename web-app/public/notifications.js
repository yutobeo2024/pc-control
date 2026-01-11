/**
 * Push Notifications for Parental Control
 * Hiển thị thông báo khi có yêu cầu mở máy mới
 */

class NotificationManager {
    constructor() {
        this.permission = 'default';
        this.notifiedRequests = new Set(); // Track requests đã thông báo
        this.isActive = false;
    }

    /**
     * Khởi tạo và xin quyền notification
     */
    async initialize() {
        if (!('Notification' in window)) {
            console.warn('Browser không hỗ trợ notifications');
            return false;
        }

        // Kiểm tra permission hiện tại
        this.permission = Notification.permission;

        if (this.permission === 'default') {
            // Chưa xin quyền, xin ngay
            this.permission = await Notification.requestPermission();
        }

        if (this.permission === 'granted') {
            console.log('✅ Notification permission granted');
            this.isActive = true;
            return true;
        } else {
            console.warn('⚠️ Notification permission denied');
            return false;
        }
    }

    /**
     * Hiển thị notification khi có yêu cầu mới
     */
    showUnlockRequest(deviceName, deviceId, requestId) {
        if (!this.isActive || this.permission !== 'granted') {
            return;
        }

        // Kiểm tra đã thông báo chưa
        if (this.notifiedRequests.has(requestId)) {
            return;
        }

        // Mark as notified
        this.notifiedRequests.add(requestId);

        // Tạo notification
        const notification = new Notification('🔔 Yêu cầu mở máy', {
            body: `${deviceName} đang yêu cầu mở máy`,
            icon: '/favicon.ico', // Thêm icon nếu có
            badge: '/badge.png', // Badge icon
            tag: requestId, // Unique tag để replace notification cũ
            requireInteraction: true, // Không tự đóng
            silent: false, // Có âm thanh
            vibrate: [200, 100, 200], // Rung trên mobile
            data: {
                deviceId: deviceId,
                requestId: requestId,
                deviceName: deviceName,
                timestamp: Date.now()
            },
            actions: [
                {
                    action: 'approve',
                    title: '✅ Cho phép',
                    icon: '/approve-icon.png'
                },
                {
                    action: 'reject',
                    title: '❌ Từ chối',
                    icon: '/reject-icon.png'
                }
            ]
        });

        // Click notification → Focus web app
        notification.onclick = (event) => {
            event.preventDefault();
            window.focus();
            notification.close();

            // Scroll to device
            const deviceCard = document.querySelector(`[data-device-id="${deviceId}"]`);
            if (deviceCard) {
                deviceCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                deviceCard.classList.add('highlight');
                setTimeout(() => deviceCard.classList.remove('highlight'), 2000);
            }
        };

        // Auto-close sau 30 giây nếu không requireInteraction
        // (Trên desktop requireInteraction có thể bị ignore)
        setTimeout(() => {
            notification.close();
        }, 30000);

        console.log(`🔔 Notification sent for ${deviceName}`);
    }

    /**
     * Hiển thị notification khi máy bị khóa
     */
    showDeviceLocked(deviceName, delayMinutes) {
        if (!this.isActive || this.permission !== 'granted') {
            return;
        }

        const message = delayMinutes === 0
            ? `${deviceName} đã bị khóa ngay lập tức`
            : `${deviceName} sẽ bị khóa sau ${delayMinutes} phút`;

        new Notification('🔒 Máy tính bị khóa', {
            body: message,
            icon: '/favicon.ico',
            tag: `lock-${Date.now()}`,
            requireInteraction: false,
            silent: true
        });
    }

    /**
     * Hiển thị notification khi máy được mở
     */
    showDeviceUnlocked(deviceName) {
        if (!this.isActive || this.permission !== 'granted') {
            return;
        }

        new Notification('✅ Máy tính đã mở', {
            body: `${deviceName} đã được mở khóa`,
            icon: '/favicon.ico',
            tag: `unlock-${Date.now()}`,
            requireInteraction: false,
            silent: true
        });
    }

    /**
     * Test notification
     */
    test() {
        if (!this.isActive) {
            console.error('Notifications not active');
            return;
        }

        new Notification('🧪 Test Notification', {
            body: 'Thông báo đang hoạt động!',
            icon: '/favicon.ico',
            requireInteraction: false
        });
    }

    /**
     * Clear notified requests (gọi khi app refresh)
     */
    clearNotifiedRequests() {
        this.notifiedRequests.clear();
    }

    /**
     * Disable notifications
     */
    disable() {
        this.isActive = false;
    }

    /**
     * Enable notifications
     */
    enable() {
        if (this.permission === 'granted') {
            this.isActive = true;
        }
    }
}

// Export singleton instance
window.notificationManager = new NotificationManager();
