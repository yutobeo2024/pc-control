// App State
let currentDevices = {};
let currentRequests = {};
let selectedDevice = null;

// Máy con gửi heartbeat mỗi 5 giây (HEARTBEAT_INTERVAL trong config.py).
// Ngưỡng 20s cho phép lỡ vài nhịp vì mạng chập chờn mà chưa báo Offline.
const ONLINE_THRESHOLD_SECONDS = 20;

// Dọn request cũ: đã xử lý > 1 giờ, hoặc pending > 24 giờ (máy con đã tắt)
const CLEANUP_INTERVAL_MS = 10 * 60 * 1000;
const RESOLVED_REQUEST_TTL_SECONDS = 60 * 60;
const PENDING_REQUEST_TTL_SECONDS = 24 * 60 * 60;

// DOM Elements
const elements = {
    connectionStatus: document.getElementById('connectionStatus'),
    pendingRequests: document.getElementById('pendingRequests'),
    noRequests: document.getElementById('noRequests'),
    requestDeviceName: document.getElementById('requestDeviceName'),
    requestTime: document.getElementById('requestTime'),
    approveBtn: document.getElementById('approveBtn'),
    rejectBtn: document.getElementById('rejectBtn'),
    devicesList: document.getElementById('devicesList'),
    deviceModal: document.getElementById('deviceModal'),
    closeModal: document.getElementById('closeModal'),
    toast: document.getElementById('toast'),
    toastMessage: document.getElementById('toastMessage')
};

// Initialize App
function init() {
    console.log('Initializing app...');

    // Initialize notifications
    initializeNotifications();

    // Listen to devices
    const devicesRef = window.dbRef.ref(window.db, 'devices');
    window.dbRef.onValue(devicesRef, (snapshot) => {
        const data = snapshot.val();
        currentDevices = data || {};
        renderDevices();
        updateConnectionStatus(true);
    }, (error) => {
        console.error('Error loading devices:', error);
        updateConnectionStatus(false);
    });

    // Listen to requests - chỉ lấy các request đang pending.
    // Trước đây load cả nhánh `requests` nên app chậm dần theo thời gian.
    // Cần index `.indexOn: ["status"]` trong Security Rules.
    const pendingQuery = window.dbRef.query(
        window.dbRef.ref(window.db, 'requests'),
        window.dbRef.orderByChild('status'),
        window.dbRef.equalTo('pending')
    );
    window.dbRef.onValue(pendingQuery, (snapshot) => {
        currentRequests = snapshot.val() || {};
        renderPendingRequests();
    }, (error) => {
        console.error('Error loading requests:', error);
    });

    // Dọn request cũ còn sót lại (client offline nên không tự xóa được)
    cleanupStaleRequests();
    setInterval(cleanupStaleRequests, CLEANUP_INTERVAL_MS);

    // Event Listeners
    elements.approveBtn.addEventListener('click', handleApprove);
    elements.rejectBtn.addEventListener('click', handleReject);
    elements.closeModal.addEventListener('click', closeModal);

    // Close modal on backdrop click
    elements.deviceModal.addEventListener('click', (e) => {
        if (e.target === elements.deviceModal) {
            closeModal();
        }
    });
}

// Update Connection Status
function updateConnectionStatus(connected) {
    elements.connectionStatus.classList.toggle('connected', connected);
    elements.connectionStatus.querySelector('.text').textContent =
        connected ? 'Connected' : 'Connecting...';
}

// Render Pending Requests
function renderPendingRequests() {
    const pendingList = Object.entries(currentRequests)
        .sort((a, b) => (a[1].timestamp || 0) - (b[1].timestamp || 0));

    // Dọn notification của các request không còn pending
    if (window.notificationManager) {
        window.notificationManager.closeResolved(Object.keys(currentRequests));
    }

    if (pendingList.length === 0) {
        elements.pendingRequests.classList.add('hidden');
        elements.noRequests.classList.remove('hidden');
        return;
    }

    elements.pendingRequests.classList.remove('hidden');
    elements.noRequests.classList.add('hidden');

    // Hiển thị yêu cầu cũ nhất
    const [requestId, request] = pendingList[0];
    const deviceName = request.deviceName || 'Unknown Device';

    elements.requestDeviceName.textContent = deviceName;
    elements.requestTime.textContent = getTimeAgo(request.timestamp);

    // Thẻ này chỉ hiện được MỘT yêu cầu. Không nói ra thì các máy còn lại trông
    // như không gửi yêu cầu gì - phụ huynh thấy máy bị khóa mà tưởng hỏng.
    // Duyệt/từ chối cái đang hiện thì cái tiếp theo tự lên.
    const queue = document.getElementById('requestQueue');
    if (queue) {
        const others = pendingList.length - 1;
        queue.textContent = others > 0
            ? `+${others} yêu cầu khác đang chờ — hoặc mở khóa thẳng ở mục Thiết bị`
            : '';
        queue.classList.toggle('hidden', others === 0);
    }

    // Send notification for new request
    if (window.notificationManager && window.notificationManager.isActive) {
        window.notificationManager.showUnlockRequest(deviceName, request.deviceId, requestId);
    }

    // Lưu id lên CẢ HAI nút - thiếu deviceId ở nút từ chối khiến thông báo
    // Slack luôn ghi "Unknown Device"
    elements.approveBtn.dataset.requestId = requestId;
    elements.approveBtn.dataset.deviceId = request.deviceId;
    elements.rejectBtn.dataset.requestId = requestId;
    elements.rejectBtn.dataset.deviceId = request.deviceId;
}

// Render Devices List
function renderDevices() {
    if (Object.keys(currentDevices).length === 0) {
        elements.devicesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">💻</div>
                <div class="empty-text">Chưa có thiết bị nào</div>
            </div>
        `;
        return;
    }

    elements.devicesList.innerHTML = Object.entries(currentDevices)
        .map(([deviceId, device]) => {
            const isUnlocked = device.status === 'unlocked';
            const icon = isUnlocked ? '💻' : '🔒';
            const statusText = device.statusText || (isUnlocked ? 'Đang hoạt động' : 'Đã khóa');

            // Mở khóa vô thời hạn -> web set timeRemaining = null, Firebase xóa
            // hẳn key. `|| 0` cũ khiến UI hiện "Còn 0h 0m".
            const timeText = !isUnlocked
                ? ''
                : (hasTimeLimit(device) ? `Còn ${formatTime(device.timeRemaining)}` : '∞ Không giới hạn');

            return `
                <div class="device-card" data-device-id="${deviceId}">
                    <div class="device-icon ${isUnlocked ? 'unlocked' : 'locked'}">
                        ${icon}
                    </div>
                    <div class="device-info">
                        <div class="device-name-text">${device.deviceName || 'Unknown Device'}</div>
                        <div class="device-status ${isUnlocked ? 'unlocked' : 'locked'}">
                            ${statusText}
                        </div>
                        ${timeText ? `<div class="device-time">${timeText}</div>` : ''}
                    </div>
                    <div class="device-arrow">›</div>
                </div>
            `;
        })
        .join('');

    // Add click handlers
    elements.devicesList.querySelectorAll('.device-card').forEach(card => {
        card.addEventListener('click', () => {
            const deviceId = card.dataset.deviceId;
            openDeviceModal(deviceId);
        });
    });
}

// Open Device Modal
function openDeviceModal(deviceId) {
    selectedDevice = { id: deviceId, ...currentDevices[deviceId] };

    const device = selectedDevice;
    const isUnlocked = device.status === 'unlocked';

    // Update modal content
    document.getElementById('modalDeviceName').textContent = device.deviceName || 'Unknown Device';
    document.getElementById('modalStatusIcon').textContent = isUnlocked ? '✅' : '🔒';
    document.getElementById('modalStatusText').textContent = isUnlocked ? 'Đang hoạt động' : 'Đã khóa';
    document.getElementById('modalStatusText').className = `status-text ${isUnlocked ? 'unlocked' : 'locked'}`;

    // Online status
    renderOnlineStatus(device);

    // Timer
    const timerCard = document.getElementById('timerCard');
    if (isUnlocked) {
        timerCard.classList.remove('hidden');
        updateTimer(hasTimeLimit(device) ? device.timeRemaining : null);
        startTimerUpdates(deviceId);
    } else {
        timerCard.classList.add('hidden');
        stopTimerUpdates();
    }

    // Nút mở khóa - hiển thị khi máy đang khóa.
    //
    // Trước đây trang thiết bị chỉ có nút KHÓA, đường mở khóa duy nhất là thẻ
    // "Yêu cầu mở máy" ở đầu trang. Mà thẻ đó chỉ hiện MỘT yêu cầu cũ nhất, nên
    // một yêu cầu pending cũ của máy khác là đủ để che yêu cầu của máy đang
    // khóa - phụ huynh nhìn thấy máy bị khóa mà không có chỗ nào mở.
    const unlockSection = document.querySelector('.unlock-section');
    if (isUnlocked) {
        unlockSection.classList.add('hidden');
    } else {
        unlockSection.classList.remove('hidden');
        document.getElementById('unlockNowBtn').onclick = () => unlockDevice(deviceId);
    }

    // Lock buttons - hiển thị khi máy đang mở
    const lockSection = document.querySelector('.lock-section');
    if (isUnlocked) {
        lockSection.classList.remove('hidden');

        // Setup các nút khóa máy
        document.querySelectorAll('.btn-lock-now, .btn-lock-delay').forEach(btn => {
            btn.onclick = () => {
                const delayMinutes = parseInt(btn.dataset.delay);
                lockDevice(deviceId, delayMinutes);
            };
        });

        const cancelBtn = document.getElementById('cancelScheduleBtn');
        cancelBtn.onclick = () => cancelSchedule(deviceId);
    } else {
        lockSection.classList.add('hidden');
    }

    renderScheduleControls(device);
    elements.deviceModal.classList.remove('hidden');
}

// Hiện nút "Hủy lịch khóa" khi và chỉ khi có gì để hủy. Gọi lại mỗi giây cùng
// với đồng hồ, vì phụ huynh có thể vừa bấm "Sau 30 phút" xong đổi ý ngay.
function renderScheduleControls(device) {
    const cancelBtn = document.getElementById('cancelScheduleBtn');
    if (!cancelBtn) return;

    const hasSchedule = device.status === 'unlocked' &&
        (hasTimeLimit(device) || !!device.lockScheduled);
    cancelBtn.classList.toggle('hidden', !hasSchedule);
}

// Cập nhật chỉ báo Online/Offline (gọi lại mỗi giây khi modal đang mở)
function renderOnlineStatus(device) {
    const onlineStatus = document.getElementById('modalOnlineStatus');
    if (!onlineStatus) return;

    const isOnline = isDeviceOnline(device.lastActive);
    onlineStatus.textContent = isOnline ? '● Online' : '○ Offline';
    onlineStatus.className = `online-status ${isOnline ? '' : 'offline'}`;
}

// Close Modal
function closeModal() {
    elements.deviceModal.classList.add('hidden');
    selectedDevice = null;
    stopTimerUpdates();
}

// Timer Updates
let timerInterval = null;

function startTimerUpdates(deviceId) {
    stopTimerUpdates();
    timerInterval = setInterval(() => {
        const device = currentDevices[deviceId];
        if (device) {
            updateTimer(hasTimeLimit(device) ? device.timeRemaining : null);
            renderOnlineStatus(device);
            renderScheduleControls(device);
        }
    }, 1000);
}

function stopTimerUpdates() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// `seconds === null` nghĩa là mở khóa vô thời hạn
function updateTimer(seconds) {
    const display = document.getElementById('timerDisplay');
    const timerCard = document.getElementById('timerCard');
    const label = timerCard.querySelector('.timer-label');

    if (seconds === null) {
        display.textContent = '∞';
        if (label) label.textContent = '⏱️ Không giới hạn thời gian';
        timerCard.classList.remove('warning');
        return;
    }

    if (label) label.textContent = '⏱️ Thời gian còn lại';
    display.textContent = formatTimeDisplay(seconds);

    // Warning state
    if (seconds <= 600) {
        timerCard.classList.add('warning');
    } else {
        timerCard.classList.remove('warning');
    }
}

// Handle Approve - Mở máy ngay, KHÔNG giới hạn thời gian
function handleApprove() {
    return approveRequest(
        elements.approveBtn.dataset.requestId,
        elements.approveBtn.dataset.deviceId
    );
}

// Handle Reject
function handleReject() {
    return rejectRequest(
        elements.rejectBtn.dataset.requestId,
        elements.rejectBtn.dataset.deviceId
    );
}

// Tách khỏi handler để nút trên notification cũng gọi được
async function approveRequest(requestId, deviceId) {
    if (!requestId || !deviceId) return;

    try {
        // Update request status - Windows Client đọc rồi tự xóa node này
        await window.dbRef.update(window.dbRef.ref(window.db, `requests/${requestId}`), {
            status: 'approved'
        });

        // Unlock device - NO time limit (set to null/unlimited)
        await window.dbRef.update(window.dbRef.ref(window.db, `devices/${deviceId}`), {
            status: 'unlocked',
            timeRemaining: null,   // Không giới hạn thời gian
            lockScheduled: null    // Hủy mọi lịch khóa còn treo - nếu không,
                                   // timestamp quá khứ sẽ khóa lại ngay sau 2 giây
        });

        showToast('✅ Đã cho phép mở máy (không giới hạn)', 'success');
        sendSlackNotification('approved', deviceId);
    } catch (error) {
        console.error('Error approving request:', error);
        showToast('❌ Lỗi: ' + error.message, 'error');
    }
}

async function rejectRequest(requestId, deviceId) {
    if (!requestId) return;

    try {
        await window.dbRef.update(window.dbRef.ref(window.db, `requests/${requestId}`), {
            status: 'rejected'
        });

        showToast('❌ Đã từ chối yêu cầu', 'success');
        sendSlackNotification('rejected', deviceId);
    } catch (error) {
        console.error('Error rejecting request:', error);
        showToast('❌ Lỗi: ' + error.message, 'error');
    }
}

// Bấm nút "Cho phép" / "Từ chối" ngay trên notification của hệ điều hành.
// Service Worker chuyển sự kiện về đây qua postMessage.
window.addEventListener('notification-action', (event) => {
    const { action, requestId, deviceId } = event.detail || {};
    if (action === 'approve') {
        approveRequest(requestId, deviceId);
    } else if (action === 'reject') {
        rejectRequest(requestId, deviceId);
    }
});

// Lock Device với delay options
async function lockDevice(deviceId, delayMinutes = 0) {
    try {
        if (delayMinutes === 0) {
            // Khóa ngay
            await window.dbRef.update(window.dbRef.ref(window.db, `devices/${deviceId}`), {
                status: 'locked',
                timeRemaining: 0,
                lockScheduled: null
            });
            showToast('🔒 Đã khóa máy tính ngay lập tức', 'success');
        } else {
            // Lên lịch khóa sau X phút
            const lockTime = Date.now() + (delayMinutes * 60 * 1000);
            await window.dbRef.update(window.dbRef.ref(window.db, `devices/${deviceId}`), {
                lockScheduled: lockTime,
                timeRemaining: delayMinutes * 60  // Set countdown timer
            });
            showToast(`⏱️ Sẽ khóa máy sau ${delayMinutes} phút`, 'success');
        }
        closeModal();
    } catch (error) {
        console.error('Error locking device:', error);
        showToast('❌ Lỗi: ' + error.message, 'error');
    }
}

// Mở khóa thẳng từ trang thiết bị, không cần đi qua thẻ yêu cầu.
//
// Không cần đụng tới `requests/`: máy con thấy status = 'unlocked' là tự xóa
// request của nó (main.py:handle_locked_state).
async function unlockDevice(deviceId) {
    if (!deviceId) return;

    try {
        await window.dbRef.update(window.dbRef.ref(window.db, `devices/${deviceId}`), {
            status: 'unlocked',
            timeRemaining: null,
            lockScheduled: null
        });
        showToast('✅ Đã mở khóa máy tính', 'success');
        sendSlackNotification('approved', deviceId);
        closeModal();
    } catch (error) {
        console.error('Error unlocking device:', error);
        showToast('❌ Lỗi: ' + error.message, 'error');
    }
}

// Hủy lịch khóa / giới hạn thời gian, máy vẫn đang mở.
//
// Phải xóa CẢ HAI: lockScheduled là mốc giờ, timeRemaining là đồng hồ đếm ngược
// chạy độc lập bên máy con - còn sót cái nào thì máy vẫn khóa đúng giờ cũ.
// Không đụng tới `status`: máy đang mở thì cứ để mở.
async function cancelSchedule(deviceId) {
    if (!deviceId) return;

    try {
        await window.dbRef.update(window.dbRef.ref(window.db, `devices/${deviceId}`), {
            lockScheduled: null,
            timeRemaining: null
        });
        showToast('✅ Đã hủy lịch khóa - máy không giới hạn thời gian', 'success');
    } catch (error) {
        console.error('Error cancelling schedule:', error);
        showToast('❌ Lỗi: ' + error.message, 'error');
    }
}

// Dọn request cũ còn sót trong Firebase.
//
// Bình thường Windows client tự xóa request ngay sau khi đọc kết quả duyệt,
// nên nhánh `requests/` chỉ giữ vài node. Hàm này xử lý phần còn lại: máy con
// bị tắt/mất mạng giữa chừng, hoặc request từ các phiên bản cũ.
async function cleanupStaleRequests() {
    try {
        const snapshot = await window.dbRef.get(window.dbRef.ref(window.db, 'requests'));
        const data = snapshot.val();
        if (!data) return;

        const now = Math.floor(Date.now() / 1000);
        const stale = Object.entries(data).filter(([, req]) => {
            const age = now - (req.timestamp || 0);
            const ttl = req.status === 'pending'
                ? PENDING_REQUEST_TTL_SECONDS
                : RESOLVED_REQUEST_TTL_SECONDS;
            return age > ttl;
        });

        if (stale.length === 0) return;

        await Promise.all(stale.map(([id]) =>
            window.dbRef.remove(window.dbRef.ref(window.db, `requests/${id}`))
        ));
        console.log(`🗑️ Đã dọn ${stale.length} request cũ`);
    } catch (error) {
        console.error('Error cleaning up requests:', error);
    }
}

// Slack Notification
async function sendSlackNotification(action, deviceId) {
    const webhookUrl = localStorage.getItem('slackWebhook');
    if (!webhookUrl) return;

    const device = currentDevices[deviceId];
    const deviceName = device?.deviceName || 'Unknown Device';

    const messages = {
        approved: `✅ Đã cho phép mở máy: *${deviceName}*`,
        rejected: `❌ Đã từ chối yêu cầu: *${deviceName}*`,
    };

    try {
        await fetch(webhookUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: messages[action],
                blocks: [{
                    type: 'section',
                    text: {
                        type: 'mrkdwn',
                        text: messages[action]
                    }
                }]
            })
        });
    } catch (error) {
        console.error('Error sending Slack notification:', error);
    }
}

// Utility Functions
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
}

function formatTimeDisplay(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function getTimeAgo(timestamp) {
    const now = Math.floor(Date.now() / 1000);
    const diff = now - timestamp;

    if (diff < 60) return 'Vừa xong';
    if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
    return `${Math.floor(diff / 86400)} ngày trước`;
}

// Máy con set timeRemaining = null khi mở khóa vô thời hạn; Firebase xóa hẳn
// key nên giá trị đọc về là undefined.
function hasTimeLimit(device) {
    return device.timeRemaining !== null && device.timeRemaining !== undefined;
}

function isDeviceOnline(lastActive) {
    if (!lastActive) return false;
    const now = Math.floor(Date.now() / 1000);
    return (now - lastActive) < ONLINE_THRESHOLD_SECONDS;
}

function showToast(message, type = 'success') {
    elements.toastMessage.textContent = message;
    elements.toast.className = `toast ${type}`;
    elements.toast.classList.remove('hidden');

    setTimeout(() => {
        elements.toast.classList.add('hidden');
    }, 3000);
}

// Notification Functions
async function initializeNotifications() {
    console.log('🔔 Initializing notifications...');

    // Wait for notificationManager to be available
    if (!window.notificationManager) {
        console.warn('⚠️ NotificationManager not loaded yet, waiting...');
        setTimeout(initializeNotifications, 500);
        return;
    }

    const notifBtn = document.getElementById('notificationBtn');
    const notifStatus = document.getElementById('notificationStatus');

    if (!notifBtn) {
        console.error('❌ Notification button not found');
        return;
    }

    // Initialize notification manager
    const granted = await window.notificationManager.initialize();

    // Update UI
    updateNotificationButton(granted);

    // Button click handler
    notifBtn.addEventListener('click', async () => {
        if (window.notificationManager.permission === 'granted') {
            // Toggle on/off
            if (window.notificationManager.isActive) {
                window.notificationManager.disable();
                updateNotificationButton(false);
                showToast('🔕 Đã tắt thông báo', 'info');
            } else {
                window.notificationManager.enable();
                updateNotificationButton(true);
                showToast('🔔 Đã bật thông báo', 'success');

                // Test notification
                window.notificationManager.test();
            }
        } else {
            // Request permission again
            const granted = await window.notificationManager.initialize();
            updateNotificationButton(granted);

            if (granted) {
                showToast('🔔 Đã bật thông báo', 'success');
                window.notificationManager.test();
            } else {
                showToast('❌ Trình duyệt chặn thông báo. Hãy cho phép trong Settings.', 'error');
            }
        }
    });

    console.log('✅ Notifications initialized');
}

function updateNotificationButton(isActive) {
    const notifBtn = document.getElementById('notificationBtn');
    const notifStatus = document.getElementById('notificationStatus');

    if (!notifBtn || !notifStatus) return;

    if (isActive) {
        notifBtn.classList.add('active');
        notifStatus.textContent = 'On';
        notifBtn.title = 'Thông báo đang BẬT';
    } else {
        notifBtn.classList.remove('active');
        notifStatus.textContent = 'Off';
        notifBtn.title = 'Thông báo đang TẮT';
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
