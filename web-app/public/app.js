// App State
let currentDevices = {};
let currentRequests = {};
let selectedDevice = null;

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

    // Listen to requests
    const requestsRef = window.dbRef.ref(window.db, 'requests');
    window.dbRef.onValue(requestsRef, (snapshot) => {
        const data = snapshot.val();
        console.log('📨 Requests data from Firebase:', data);
        currentRequests = {};

        if (data) {
            Object.keys(data).forEach(key => {
                console.log(`Checking request ${key}:`, data[key]);
                if (data[key].status === 'pending') {
                    console.log('✅ Found pending request:', key, data[key]);
                    currentRequests[key] = data[key];
                } else {
                    console.log(`⏭️ Skipping request ${key} with status:`, data[key].status);
                }
            });
        }

        console.log('Current pending requests:', currentRequests);
        renderPendingRequests();
    });

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
    const pendingList = Object.entries(currentRequests);
    console.log('🎨 Rendering pending requests. Count:', pendingList.length);

    if (pendingList.length === 0) {
        console.log('❌ No pending requests - hiding request card');
        elements.pendingRequests.classList.add('hidden');
        elements.noRequests.classList.remove('hidden');
        return;
    }

    console.log('✅ Showing pending request card');
    elements.pendingRequests.classList.remove('hidden');
    elements.noRequests.classList.add('hidden');

    // Show first pending request
    const [requestId, request] = pendingList[0];
    console.log('Displaying request:', requestId, request);
    elements.requestDeviceName.textContent = request.deviceName || 'Unknown Device';
    elements.requestTime.textContent = getTimeAgo(request.timestamp);

    // Send notification for new request
    if (window.notificationManager && window.notificationManager.isActive) {
        window.notificationManager.showUnlockRequest(
            request.deviceName || 'Unknown Device',
            request.deviceId,
            requestId
        );
    }

    // Store current request ID
    elements.approveBtn.dataset.requestId = requestId;
    elements.rejectBtn.dataset.requestId = requestId;
    elements.approveBtn.dataset.deviceId = request.deviceId;
    console.log('Request card updated with:', {
        deviceName: request.deviceName,
        requestId,
        deviceId: request.deviceId
    });
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
            const timeText = isUnlocked ? formatTime(device.timeRemaining || 0) : '';

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
                        ${timeText ? `<div class="device-time">Còn ${timeText}</div>` : ''}
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
    const isOnline = isDeviceOnline(device.lastActive);
    const onlineStatus = document.getElementById('modalOnlineStatus');
    onlineStatus.textContent = isOnline ? '● Online' : '○ Offline';
    onlineStatus.className = `online-status ${isOnline ? '' : 'offline'}`;

    // Timer
    const timerCard = document.getElementById('timerCard');
    if (isUnlocked) {
        timerCard.classList.remove('hidden');
        updateTimer(device.timeRemaining || 0);
        startTimerUpdates(deviceId);
    } else {
        timerCard.classList.add('hidden');
        stopTimerUpdates();
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
    } else {
        lockSection.classList.add('hidden');
    }

    elements.deviceModal.classList.remove('hidden');
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
            updateTimer(device.timeRemaining || 0);
        }
    }, 1000);
}

function stopTimerUpdates() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function updateTimer(seconds) {
    const display = document.getElementById('timerDisplay');
    const timerCard = document.getElementById('timerCard');

    display.textContent = formatTimeDisplay(seconds);

    // Warning state
    if (seconds <= 600) {
        timerCard.classList.add('warning');
    } else {
        timerCard.classList.remove('warning');
    }
}

// Handle Approve - Mở máy ngay, KHÔNG giới hạn thời gian
async function handleApprove() {
    const requestId = elements.approveBtn.dataset.requestId;
    const deviceId = elements.approveBtn.dataset.deviceId;

    if (!requestId || !deviceId) return;

    try {
        // Update request status
        await window.dbRef.update(window.dbRef.ref(window.db, `requests/${requestId}`), {
            status: 'approved'
        });

        // Unlock device - NO time limit (set to null/unlimited)
        await window.dbRef.update(window.dbRef.ref(window.db, `devices/${deviceId}`), {
            status: 'unlocked',
            timeRemaining: null  // Không giới hạn thời gian
        });

        showToast('✅ Đã cho phép mở máy (không giới hạn)', 'success');

        // Send Slack notification
        sendSlackNotification('approved', deviceId);
    } catch (error) {
        console.error('Error approving request:', error);
        showToast('❌ Lỗi: ' + error.message, 'error');
    }
}

// Handle Reject
async function handleReject() {
    const requestId = elements.rejectBtn.dataset.requestId;
    const deviceId = elements.rejectBtn.dataset.deviceId;

    if (!requestId) return;

    try {
        console.log('🚫 Rejecting request:', requestId);

        // Update request status to rejected (để Windows Client biết)
        await window.dbRef.update(window.dbRef.ref(window.db, `requests/${requestId}`), {
            status: 'rejected'
        });

        console.log('✅ Request marked as rejected');

        showToast('❌ Đã từ chối yêu cầu', 'success');

        // Send Slack notification
        sendSlackNotification('rejected', deviceId);
    } catch (error) {
        console.error('Error rejecting request:', error);
        showToast('❌ Lỗi: ' + error.message, 'error');
    }
}

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

// Unlock Device
async function unlockDevice(deviceId) {
    try {
        const device = currentDevices[deviceId];
        await window.dbRef.update(window.dbRef.ref(window.db, `devices/${deviceId}`), {
            status: 'unlocked',
            timeRemaining: device.timeLimit || 7200
        });

        showToast('✅ Đã mở khóa máy tính', 'success');
        closeModal();
    } catch (error) {
        console.error('Error unlocking device:', error);
        showToast('❌ Lỗi: ' + error.message, 'error');
    }
}

// Add Time
async function addTime(deviceId, seconds) {
    try {
        const device = currentDevices[deviceId];
        const newTime = (device.timeRemaining || 0) + seconds;

        await window.dbRef.update(window.dbRef.ref(window.db, `devices/${deviceId}`), {
            timeRemaining: newTime
        });

        const minutes = seconds / 60;
        showToast(`⏱️ Đã thêm ${minutes} phút`, 'success');
    } catch (error) {
        console.error('Error adding time:', error);
        showToast('❌ Lỗi: ' + error.message, 'error');
    }
}

// Set Time Limit
async function setTimeLimit(deviceId, seconds) {
    try {
        await window.dbRef.update(window.dbRef.ref(window.db, `devices/${deviceId}`), {
            timeLimit: seconds
        });

        const hours = seconds / 3600;
        showToast(`✅ Đã đặt giới hạn: ${hours} giờ/ngày`, 'success');
    } catch (error) {
        console.error('Error setting time limit:', error);
        showToast('❌ Lỗi: ' + error.message, 'error');
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

function isDeviceOnline(lastActive) {
    const now = Math.floor(Date.now() / 1000);
    return (now - lastActive) < 10;
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
