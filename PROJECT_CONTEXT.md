# Parental Control System - Project Context

## Tổng Quan Dự Án

### Mục đích
Hệ thống Parental Control cho phép phụ huynh kiểm soát việc sử dụng máy tính của con cái từ xa thông qua Web App trên điện thoại.

### Architecture
```
┌─────────────────────┐
│   Web App           │
│   (Netlify)         │
│   - Google Auth     │
│   - Control Panel   │
└──────────┬──────────┘
           │
           │ Firebase Realtime DB
           │ (Real-time sync)
           │
┌──────────▼──────────┐
│  Windows Client     │
│  (Python/PyQt5)     │
│  - Lock Screen      │
│  - Auto-start       │
└─────────────────────┘
```

### Tech Stack

**Frontend (Web App):**
- HTML5/CSS3/Vanilla JavaScript
- Firebase SDK v9 (modular)
- Firebase Authentication (Google Sign-In)
- Firebase Realtime Database
- Deployed on Netlify

**Backend:**
- Firebase Realtime Database (real-time sync)
- Firebase Security Rules (server-side validation)

**Windows Client:**
- Python 3.13
- PyQt5 (GUI framework)
- Pyrebase (Firebase client)
- Windows Task Scheduler (auto-start)

---

## Key Features Đã Implement

### 1. Unlock Logic (KHÔNG giới hạn thời gian)
- **Location:** `web-app/public/app.js:260-272`
- **Behavior:** Khi phụ huynh bấm "Cho phép", máy mở khóa VÔ THỜI HẠN
- **Implementation:** Set `timeRemaining: null` trong Firebase

### 2. Multiple Lock Options
- **Location:** `web-app/public/index.html:83-90`
- **Options:** Khóa ngay, sau 30p, 1h, 1.5h, 2h, 3h
- **Implementation:**
  - Frontend: 6 buttons với `data-delay` attribute
  - Backend: `lockScheduled` timestamp system
  - Client: `windows-client/main.py:249-257`

### 3. Push Notifications (v1.1) ⭐ NEW
- **Location:** `web-app/public/notifications.js`
- **Features:**
  - Browser push notifications khi có yêu cầu mở máy
  - Toggle button để bật/tắt (🔔 On/Off)
  - Test notification khi enable lần đầu
  - Click notification → Focus web app
  - Âm thanh + rung trên mobile
- **Implementation:**
  - NotificationManager class với Notification API
  - Permission request on first use
  - Duplicate notification prevention
  - Integration: `app.js:106-113`, `app.js:467-540`
- **Browser Support:** Chrome, Firefox, Edge, Safari 16.4+

### 4. Google Authentication
- **Location:** `web-app/public/index.html:168-200`
- **Security:**
  - Email whitelist stored in Firebase Rules (server-side)
  - Frontend tests database access to verify permission
  - NO email exposure in client code

### 4. Firebase Security Rules
- **Location:** `FIREBASE-RULES-SECURE.json`
- **Rules:**
  - `auth == null` → Allow Windows Client (no auth)
  - `auth.token.email == 'hanhtoami@gmail.com' || 'thuydungsp@gmail.com'` → Allow Web App
  - Email whitelist ONLY in Firebase Console, NOT in frontend

### 5. Emergency Unlock
- **Hotkey:** `Ctrl+Shift+Alt+U`
- **Password:** `admin123` (configurable in `config.py:25`)
- **Location:**
  - Dialog: `windows-client/emergency_dialog.py`
  - Handler: `windows-client/main.py:170-200`
- **Security:** NO hint shown on lock screen

### 6. Auto-start with Windows
- **Location:** `windows-client/setup_autostart.bat`
- **Method:** Windows Task Scheduler
- **Features:**
  - Run with highest privileges
  - Hidden console (uses `pythonw.exe`)
  - Auto-restart if failed

### 7. Lock Screen Management
- **Location:** `windows-client/lock_screen.py`
- **Features:**
  - Fullscreen lock screen
  - Cannot close or minimize
  - Always on top
  - Recreated on each lock (prevents state issues)

---

## Code Locations Quan Trọng

### Web App

**Authentication Flow:**
- `web-app/public/index.html:168-200` - Auth state listener, permission check

**Approve Handler (No time limit):**
- `web-app/public/app.js:260-272` - Set `timeRemaining: null`

**Lock Buttons:**
- `web-app/public/index.html:83-90` - 6 lock option buttons
- `web-app/public/app.js:316-340` - `lockDevice()` function with delay

**Lock Buttons Setup:**
- `web-app/public/app.js:190-204` - Event handlers for lock buttons

### Windows Client

**Lock Screen Creation (Recreate each time):**
- `windows-client/main.py:77-99` - `show_lock_screen()` - Deletes old, creates new

**Unlock Logic (Handle null timeRemaining):**
- `windows-client/main.py:130-165` - `complete_unlock()` - Check if `timeRemaining is None`

**Emergency Unlock:**
- `windows-client/main.py:170-200` - `handle_emergency_unlock()` - Show dialog, validate password
- `windows-client/emergency_dialog.py` - Custom password dialog

**Lock Detection:**
- `windows-client/lock_screen.py:134-144` - `keyPressEvent()` - Detect `Ctrl+Shift+Alt+U`

**Firebase Updates Check:**
- `windows-client/main.py:212-270` - `check_firebase_updates()` - Check lock/unlock commands, lockScheduled

**Scheduled Lock:**
- `windows-client/main.py:249-257` - Check `lockScheduled` timestamp

---

## Git History & Development Timeline

### Session 1: Initial Setup (Previous)
- Basic lock/unlock functionality
- Firebase integration
- Web app with time limit

### Session 2: Logic Changes (Current)
**Commits:**
1. `feat: Remove time limit on approve` - Set `timeRemaining: null`
2. `feat: Add multiple lock options` - 6 lock buttons with delay
3. `feat: Implement scheduled lock` - `lockScheduled` timestamp system

### Session 3: Security Implementation
**Commits:**
1. `feat: Add Google Authentication` - Firebase Auth integration
2. `security: Move email whitelist to Firebase Rules` - Remove from frontend
3. `fix: Update Firebase Rules for Windows Client` - Allow `auth == null`

### Session 4: Emergency Unlock
**Commits:**
1. `feat: Add emergency unlock hotkey` - `Ctrl+Shift+Alt+U`
2. `feat: Create custom emergency dialog` - Replace QInputDialog (fix crash)
3. `security: Hide emergency unlock hint` - Remove from lock screen

### Session 5: Bug Fixes & Polish
**Commits:**
1. `fix: Lock screen not showing on 2nd lock` - Recreate lock screen each time
2. `fix: Approved screen not closing` - Recreate approved screen each time
3. `fix: Hide Python console window` - Use `pythonw.exe` in START.bat

### Session 6: Auto-start
**Commits:**
1. `feat: Add auto-start setup scripts` - Task Scheduler integration
2. `docs: Add auto-start guide` - Comprehensive documentation

---

## Known Issues & Solutions

### Issue 1: Email Whitelist Exposed in Frontend
**Problem:** Email addresses visible in HTML source code
**Solution:** Moved to Firebase Security Rules (server-side)
**Files Changed:** `index.html`, `FIREBASE-RULES-SECURE.json`

### Issue 2: QInputDialog Crashes on Hotkey
**Problem:** `QInputDialog` caused Python crash when showing over lock screen
**Solution:** Created custom `EmergencyDialog` class
**Files Changed:** `emergency_dialog.py`, `main.py`

### Issue 3: Lock Screen Not Showing on 2nd Lock
**Problem:** Lock screen reused from previous lock, state corrupted
**Solution:** Delete and recreate lock screen on each lock
**Location:** `main.py:77-99` (show_lock_screen)

### Issue 4: Approved Screen Not Closing
**Problem:** Timer expired on first show, not reset on subsequent shows
**Solution:** Recreate approved screen each unlock
**Location:** `main.py:113-128` (unlock_computer)

### Issue 5: Python Console Visible
**Problem:** Console window showing in taskbar
**Solution:** Use `pythonw.exe` instead of `python.exe` in START.bat
**Location:** `START.bat:4`

### Issue 6: Firebase Permission Denied for Windows Client
**Problem:** New security rules blocked Windows Client
**Solution:** Update rules to allow `auth == null`
**Location:** `FIREBASE-RULES-SECURE.json`

---

## Development History

### Phase 1: Initial Development
- Basic parental control with fixed time limits
- Simple lock/unlock mechanism
- Web app with single approve/reject buttons

### Phase 2: Logic Redesign (This Session)
- Changed to NO time limit on approve
- Added 6 lock options with scheduling
- Implemented `lockScheduled` system

### Phase 3: Security Hardening
- Added Google Authentication
- Moved email whitelist to server-side
- Updated Firebase Rules for proper access control

### Phase 4: User Experience
- Added emergency unlock for emergencies
- Hidden emergency hint (security)
- Fixed all UI bugs (lock screen, approved screen)

### Phase 5: Production Ready
- Auto-start with Windows
- Hidden console window
- Comprehensive documentation

---

## How to Run

### Prerequisites
```bash
# Install Python 3.13
# Install dependencies
pip install pyqt5 pyrebase4 requests
```

### Windows Client
```bash
# Run once (manual)
cd "d:\yuto control\windows-client"
START.bat

# Enable auto-start
# Right-click setup_autostart.bat → Run as administrator

# Disable auto-start
# Right-click remove_autostart.bat → Run as administrator
```

### Web App
1. Deploy `web-app/public/` to Netlify
2. Add domain to Firebase Console → Authentication → Authorized domains
3. Update Firebase Rules in Firebase Console → Realtime Database → Rules

### Firebase Setup
1. **Add Authorized Domain:**
   - Firebase Console → Authentication → Settings → Authorized domains
   - Add: `yutokun.netlify.app`

2. **Update Security Rules:**
   - Firebase Console → Realtime Database → Rules
   - Copy from `FIREBASE-RULES-SECURE.json`
   - Publish

---

## Configuration Files

### `windows-client/config.py`
```python
EMERGENCY_UNLOCK_PASSWORD = "admin123"  # Change this!
CHECK_INTERVAL = 2000  # ms - Check Firebase every 2s
WARNING_TIME = 600  # seconds - Warning at 10 min remaining
```

### `web-app/public/index.html`
```javascript
// Firebase config (lines 125-133)
const firebaseConfig = {
  apiKey: "...",
  authDomain: "...",
  databaseURL: "...",
  // ...
};
```

### `FIREBASE-RULES-SECURE.json`
```json
{
  "rules": {
    "devices": {
      ".read": "auth == null || (auth.token.email == 'hanhtoami@gmail.com' || auth.token.email == 'thuydungsp@gmail.com')",
      ".write": "auth == null || (auth.token.email == 'hanhtoami@gmail.com' || auth.token.email == 'thuydungsp@gmail.com')"
    }
  }
}
```

---

## Future Features (Not Implemented)

### High Priority
- [ ] Multiple device profiles (different kids)
- [ ] Usage statistics & reports
- [ ] Schedule automatic locks (bedtime, etc.)
- [ ] Whitelist/blacklist applications
- [ ] Screen time limits per day

### Medium Priority
- [ ] Mobile app (React Native)
- [ ] Email notifications
- [ ] Activity logs
- [ ] Remote screenshot capture
- [ ] Website filtering

### Low Priority
- [ ] Multi-language support
- [ ] Dark mode for web app
- [ ] Voice commands
- [ ] AI-powered usage analysis

---

## Security Considerations

### Current Security Measures
✅ Google Authentication required for web app
✅ Email whitelist stored server-side (Firebase Rules)
✅ Emergency unlock password protected
✅ Emergency hint hidden from lock screen
✅ Windows Client runs local only (no remote exploit)

### Potential Vulnerabilities
⚠️ Firebase config public (acceptable per Google)
⚠️ Emergency password in plaintext (config.py)
⚠️ Windows Client allows non-auth access (by design for local use)
⚠️ No rate limiting on unlock requests

### Recommendations
- Change emergency password from default `admin123`
- Keep emergency password in secure location (written note)
- Use Strong Google account passwords
- Enable 2FA on Firebase account

---

## Testing Checklist

### Web App
- [ ] Login with authorized email → Success
- [ ] Login with unauthorized email → Denied
- [ ] Approve request → Machine unlocks (no time limit)
- [ ] Lock now → Machine locks immediately
- [ ] Lock after 30min → Machine locks after 30min
- [ ] All lock options work correctly

### Windows Client
- [ ] Auto-start on Windows boot
- [ ] Lock screen shows on start
- [ ] Emergency unlock works (Ctrl+Shift+Alt+U)
- [ ] Wrong password → Shows error, lock remains
- [ ] Approve on web → Machine unlocks
- [ ] Lock on web → Lock screen shows
- [ ] Lock screen recreates correctly on 2nd lock
- [ ] Approved screen auto-closes after 2 seconds
- [ ] No console window visible

### Edge Cases
- [ ] Internet disconnection → Graceful handling
- [ ] Firebase down → Shows error message
- [ ] Multiple rapid lock/unlock → No state corruption
- [ ] Emergency unlock during normal unlock → Works correctly

---

## File Structure

```
d:\yuto control\
├── web-app/
│   └── public/
│       ├── index.html          # Main HTML with auth & UI
│       ├── app.js              # App logic (approve, lock, etc.)
│       ├── styles.css          # All styles
│       └── .firebaserc         # Firebase project config
├── windows-client/
│   ├── main.py                 # Main application entry point
│   ├── firebase_handler.py     # Firebase integration
│   ├── lock_screen.py          # Lock screen UI
│   ├── emergency_dialog.py     # Emergency unlock dialog
│   ├── timer_widget.py         # Countdown timer widget
│   ├── slack_notifier.py       # Slack notifications
│   ├── config.py               # Configuration
│   ├── START.bat               # Startup script (pythonw.exe)
│   ├── setup_autostart.bat     # Enable auto-start
│   ├── remove_autostart.bat    # Disable auto-start
│   └── AUTO-START-GUIDE.md     # Auto-start documentation
├── FIREBASE-RULES-SECURE.json  # Firebase Security Rules
├── FIREBASE-SECURITY-SETUP.md  # Security setup guide
├── SECURITY-SUMMARY.md         # Security changes summary
└── PROJECT_CONTEXT.md          # This file

```

---

## Contact & Support

**GitHub Repository:** https://github.com/yutobeo2024/pc-control

**For Issues:**
- Create issue on GitHub
- Include error logs from console
- Include screenshots if UI-related

---

## Changelog

### v1.1 (2026-01-11) - Push Notifications
- 🔔 Browser push notifications for unlock requests
- 🔘 Toggle button to enable/disable notifications
- ✅ Visual indicator (On/Off with green color)
- 🧪 Test notification on first enable
- 📱 Mobile support (sound + vibration)
- 👆 Click notification to focus web app
- 🔄 Auto-notification for new pending requests
- 🌐 Cross-browser support (Chrome, Firefox, Edge, Safari)

**Commit:** e23986f
**Files:** notifications.js (NEW), index.html, app.js, styles.css

### v1.0.0 (2026-01-11) - Initial Release
- ✅ Basic lock/unlock functionality
- ✅ No time limit on approve
- ✅ 6 lock options with scheduling
- ✅ Google Authentication
- ✅ Email whitelist (server-side)
- ✅ Emergency unlock (Ctrl+Shift+Alt+U)
- ✅ Auto-start with Windows
- ✅ Hidden console window
- ✅ Comprehensive documentation

**Commit:** cec6417

---

**Last Updated:** 2026-01-11
**Version:** 1.1
**Status:** Production Ready + Notifications ✅
