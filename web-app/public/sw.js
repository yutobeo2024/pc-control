/**
 * Service Worker cho Parental Control.
 *
 * Lý do tồn tại: `new Notification(...)` ở trang chính bỏ qua `actions` và
 * `vibrate` - chỉ notification tạo từ ServiceWorkerRegistration mới hỗ trợ nút
 * bấm. Service Worker cũng giữ notification sống khi tab bị ẩn/đóng.
 *
 * GIỚI HẠN: đây KHÔNG phải Web Push. Trình duyệt chỉ đánh thức Service Worker
 * khi có push message từ server (cần FCM + VAPID key + backend gửi message).
 * Hiện tại notification vẫn phải do trang web đang mở tạo ra.
 */

const APP_URL = './';

self.addEventListener('install', (event) => {
    // Kích hoạt bản mới ngay, không chờ tab cũ đóng
    event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

/**
 * Bấm vào notification hoặc nút Cho phép / Từ chối.
 * Focus tab đang mở (hoặc mở tab mới) rồi chuyển hành động cho trang xử lý -
 * Service Worker không có Firebase SDK nên không tự ghi database được.
 */
self.addEventListener('notificationclick', (event) => {
    const action = event.action || 'open';
    const data = event.notification.data || {};

    event.notification.close();

    event.waitUntil((async () => {
        const clientList = await self.clients.matchAll({
            type: 'window',
            includeUncontrolled: true
        });

        let client = clientList.find((c) => 'focus' in c);

        if (client) {
            await client.focus();
        } else if (self.clients.openWindow) {
            client = await self.clients.openWindow(APP_URL);
            // Trang mới cần thời gian khởi động trước khi nhận được message
            await new Promise((resolve) => setTimeout(resolve, 1500));
        }

        if (client && action !== 'open') {
            client.postMessage({
                type: 'notification-action',
                action,
                requestId: data.requestId,
                deviceId: data.deviceId
            });
        }
    })());
});

self.addEventListener('notificationclose', () => {
    // Không làm gì - giữ handler để tránh warning ở một số trình duyệt
});
