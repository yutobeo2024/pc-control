/**
 * Push Notifications for Parental Control
 * Hiển thị thông báo khi có yêu cầu mở máy mới.
 *
 * Notification được tạo qua Service Worker (`sw.js`) thay vì
 * `new Notification(...)`: chỉ cách này mới hiện được nút "Cho phép" /
 * "Từ chối" và rung trên mobile.
 *
 * GIỚI HẠN: không phải Web Push thật - trang web phải đang mở (kể cả ở tab
 * nền) thì mới có thông báo. Muốn nhận khi đã đóng hẳn trình duyệt thì cần
 * FCM Web Push: VAPID key + backend gửi message, xem README.
 */

const SW_PATH = 'sw.js';

class NotificationManager {
    constructor() {
        this.permission = 'default';
        this.notifiedRequests = new Set(); // Track requests đã thông báo
        this.isActive = false;
        this.registration = null;
    }

    get isSupported() {
        return 'Notification' in window;
    }

    /**
     * Đăng ký Service Worker. Trả về registration hoặc null nếu không dùng được
     * (trình duyệt cũ, hoặc trang chạy qua http:// không phải localhost).
     */
    async registerServiceWorker() {
        if (this.registration) return this.registration;
        if (!('serviceWorker' in navigator)) {
            console.warn('⚠️ Trình duyệt không hỗ trợ Service Worker');
            return null;
        }

        try {
            this.registration = await navigator.serviceWorker.register(SW_PATH);
            await navigator.serviceWorker.ready;

            // Nhận hành động Cho phép / Từ chối bấm từ notification
            navigator.serviceWorker.addEventListener('message', (event) => {
                const data = event.data || {};
                if (data.type !== 'notification-action') return;

                window.dispatchEvent(new CustomEvent('notification-action', {
                    detail: {
                        action: data.action,
                        requestId: data.requestId,
                        deviceId: data.deviceId
                    }
                }));
            });

            console.log('✅ Service Worker registered');
            return this.registration;
        } catch (error) {
            console.error('❌ Service Worker registration failed:', error);
            return null;
        }
    }

    /**
     * Khởi tạo và xin quyền notification
     */
    async initialize() {
        if (!this.isSupported) {
            console.warn('Browser không hỗ trợ notifications');
            return false;
        }

        this.permission = Notification.permission;

        if (this.permission === 'default') {
            this.permission = await Notification.requestPermission();
        }

        if (this.permission !== 'granted') {
            console.warn('⚠️ Notification permission denied');
            this.isActive = false;
            return false;
        }

        await this.registerServiceWorker();
        console.log('✅ Notification permission granted');
        this.isActive = true;
        return true;
    }

    /**
     * Hiển thị notification. Ưu tiên Service Worker (có nút bấm), nếu không
     * đăng ký được thì rơi về Notification thường (không có nút).
     */
    async show(title, options) {
        if (!this.isActive || this.permission !== 'granted') return;

        try {
            const registration = this.registration || await this.registerServiceWorker();
            if (registration) {
                await registration.showNotification(title, options);
                return;
            }

            // Fallback: `actions` và `vibrate` sẽ bị bỏ qua
            const { actions, vibrate, ...basic } = options;
            new Notification(title, basic);
        } catch (error) {
            console.error('Error showing notification:', error);
        }
    }

    /**
     * Hiển thị notification khi có yêu cầu mở máy mới
     */
    async showUnlockRequest(deviceName, deviceId, requestId) {
        if (!this.isActive || this.permission !== 'granted') return;

        // Tránh thông báo trùng cho cùng một request
        if (this.notifiedRequests.has(requestId)) return;
        this.notifiedRequests.add(requestId);

        await this.show('🔔 Yêu cầu mở máy', {
            body: `${deviceName} đang yêu cầu mở máy`,
            tag: requestId,          // trùng tag -> thay thế notification cũ
            renotify: true,
            requireInteraction: true,
            silent: false,
            vibrate: [200, 100, 200],
            data: { deviceId, requestId, deviceName, timestamp: Date.now() },
            actions: [
                { action: 'approve', title: '✅ Cho phép' },
                { action: 'reject', title: '❌ Từ chối' }
            ]
        });

        console.log(`🔔 Notification sent for ${deviceName}`);
    }

    /**
     * Đóng notification của các request đã được xử lý xong.
     * requireInteraction khiến notification nằm lại cho tới khi bị đóng tay,
     * nên phải tự dọn khi request không còn pending.
     */
    async closeResolved(activeRequestIds) {
        if (!this.registration) return;

        try {
            const active = new Set(activeRequestIds);
            const shown = await this.registration.getNotifications();
            shown.forEach((notification) => {
                const requestId = notification.data && notification.data.requestId;
                if (requestId && !active.has(requestId)) {
                    notification.close();
                }
            });
        } catch (error) {
            console.error('Error closing notifications:', error);
        }
    }

    /**
     * Hiển thị notification khi máy bị khóa
     */
    async showDeviceLocked(deviceName, delayMinutes) {
        const message = delayMinutes === 0
            ? `${deviceName} đã bị khóa ngay lập tức`
            : `${deviceName} sẽ bị khóa sau ${delayMinutes} phút`;

        await this.show('🔒 Máy tính bị khóa', {
            body: message,
            tag: `lock-${deviceName}`,
            requireInteraction: false,
            silent: true
        });
    }

    /**
     * Hiển thị notification khi máy được mở
     */
    async showDeviceUnlocked(deviceName) {
        await this.show('✅ Máy tính đã mở', {
            body: `${deviceName} đã được mở khóa`,
            tag: `unlock-${deviceName}`,
            requireInteraction: false,
            silent: true
        });
    }

    /**
     * Test notification
     */
    async test() {
        if (!this.isActive) {
            console.error('Notifications not active');
            return;
        }

        await this.show('🧪 Test Notification', {
            body: 'Thông báo đang hoạt động!',
            tag: 'test',
            requireInteraction: false
        });
    }

    /**
     * Clear notified requests (gọi khi app refresh)
     */
    clearNotifiedRequests() {
        this.notifiedRequests.clear();
    }

    disable() {
        this.isActive = false;
    }

    enable() {
        if (this.permission === 'granted') {
            this.isActive = true;
        }
    }
}

// Export singleton instance
window.notificationManager = new NotificationManager();
